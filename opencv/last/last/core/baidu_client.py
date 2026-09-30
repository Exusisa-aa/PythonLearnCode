"""百度智能云人脸识别 API 客户端。

封装了：access_token 获取与缓存、图片 Base64 编码、人脸注册/检索/删除/明细查询，
以及错误码到中文提示的转换。

接口文档要点（详见 README 与 openspec/changes/baidu-face-recognition/design.md）：
- 业务请求统一 POST + `Content-Type: application/json`，access_token 放在 URL query 中；
- `image_type=BASE64` 时，Base64 串**不能**带 `data:image/jpg;base64,` 前缀；
- `user_id` / `group_id` 仅允许数字、字母、下划线，长度上限 48 字节。
"""

from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import requests

if __package__ in (None, ""):
    # 支持 `python core/baidu_client.py` 直接运行自测
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.errors import (
    FACE_NOT_EXIST,
    NO_MATCH_USER,
    USER_NOT_EXIST,
    FaceAPIError,
    FaceNetworkError,
    is_token_error,
)
from core.images import ImageEncodeError, encode_image, load_bgr_image  # noqa: F401

TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
API_BASE = "https://aip.baidubce.com/rest/2.0/face/v3"

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 20

# token 提前刷新余量，避免边界时刻拿到刚过期的 token
_TOKEN_REFRESH_MARGIN_SECONDS = 300

# 两次接口调用之间的最小间隔（秒）。
# 免费额度只有 1 QPS，连续操作（如"注册后立刻识别"）很容易撞上错误码 18（QPS 超限）。
# 1.05 秒的间隔在人工交互中几乎无感，却能稳定规避这个自伤式的失败。
# 若已购买更高 QPS，可下调该值。
MIN_REQUEST_INTERVAL_SECONDS = 1.05


def _brief_error(exc: requests.RequestException) -> str:
    """把 requests 异常压缩成一句简短原因。

    绝不能直接使用 `str(exc)`：它包含完整请求 URL，而取 token 的 URL 里带着
    `client_secret`，一旦原样显示在界面上或写进日志就等于泄露 SK。
    """
    if isinstance(exc, requests.Timeout):
        return "请求超时"
    if isinstance(exc, requests.ConnectionError):
        return "无法连接到百度服务器"
    return exc.__class__.__name__


@dataclass(frozen=True)
class DeleteResult:
    """删除人员的结果。

    removed=True  本次确实从云端删除了；
    removed=False 云端本来就没有这个用户（视为已删除，本地可继续清理）。
    """

    removed: bool


# --------------------------------------------------------------------------
# 客户端
# --------------------------------------------------------------------------


class BaiduFaceClient:
    """线程安全的人脸 API 客户端，可被界面工作线程调用。"""

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        timeout: tuple[int, int] = (CONNECT_TIMEOUT, READ_TIMEOUT),
    ) -> None:
        self._api_key = api_key
        self._secret_key = secret_key
        self._timeout = timeout
        self._session = requests.Session()
        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._token_lock = threading.Lock()
        self._throttle_lock = threading.Lock()
        self._last_request_at: float = 0.0

    def close(self) -> None:
        self._session.close()

    # -- 限流 --------------------------------------------------------------

    def _throttle(self) -> None:
        """把连续请求拉开到 MIN_REQUEST_INTERVAL_SECONDS 以上。

        在锁内 sleep 是有意为之：多个工作线程同时发请求时，这里会把它们串行化，
        正好符合"全局限速"的语义。
        """
        with self._throttle_lock:
            wait = self._last_request_at + MIN_REQUEST_INTERVAL_SECONDS - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last_request_at = time.monotonic()

    # -- 鉴权 --------------------------------------------------------------

    def _get_access_token(self, force_refresh: bool = False) -> str:
        """取得 access_token，命中缓存则直接复用（提前 5 分钟刷新）。"""
        with self._token_lock:
            now = time.monotonic()
            if not force_refresh and self._token and now < self._token_expires_at:
                return self._token

            self._throttle()
            try:
                response = self._session.post(
                    TOKEN_URL,
                    params={
                        "grant_type": "client_credentials",
                        "client_id": self._api_key,
                        "client_secret": self._secret_key,
                    },
                    timeout=self._timeout,
                )
            except requests.RequestException as exc:
                raise FaceNetworkError(f"获取 access_token 失败（{_brief_error(exc)}）") from exc

            try:
                payload = response.json()
            except ValueError:
                raise FaceNetworkError(
                    f"获取 access_token 时返回了无法解析的内容（HTTP {response.status_code}）"
                ) from None

            token = payload.get("access_token")
            if not token:
                description = payload.get("error_description") or payload.get("error") or payload
                raise FaceAPIError(
                    100, f"获取 access_token 失败：{description}"
                )

            expires_in = int(payload.get("expires_in", 0))
            self._token = token
            self._token_expires_at = now + max(0, expires_in - _TOKEN_REFRESH_MARGIN_SECONDS)
            return token

    def _post(self, path: str, payload: dict) -> dict:
        """发起业务请求。token 失效时清缓存重取并重试一次。"""
        last_error: FaceAPIError | None = None

        for attempt in (0, 1):
            token = self._get_access_token(force_refresh=attempt == 1)
            self._throttle()
            try:
                response = self._session.post(
                    f"{API_BASE}{path}",
                    params={"access_token": token},
                    json=payload,
                    timeout=self._timeout,
                )
            except requests.RequestException as exc:
                raise FaceNetworkError(_brief_error(exc)) from exc

            try:
                data = response.json()
            except ValueError:
                raise FaceNetworkError(
                    f"接口返回了无法解析的内容（HTTP {response.status_code}）"
                ) from None

            code = int(data.get("error_code", 0))
            if code == 0:
                return data

            error = FaceAPIError(code, str(data.get("error_msg", "")))
            # 仅 token 失效类错误值得重试；其余直接抛出，避免浪费配额
            if attempt == 0 and is_token_error(code):
                last_error = error
                continue
            raise error

        assert last_error is not None
        raise last_error

    @staticmethod
    def _result_of(data: dict) -> dict:
        """取出响应中的 `result` 载荷。

        人脸 v3 接口在成功时把业务数据包在 `result` 里，而不是放在顶层：

            {"error_code": 0, "error_msg": "SUCCESS",
             "result": {"face_token": "...", "user_list": [...]}}

        部分接口（如删除人员）成功时 `result` 为 null，因此统一归一化为空字典。
        顶层直接取 `face_token` / `user_list` 会永远取到空值，导致检索结果恒为空、
        所有人都被判成"陌生人"。
        """
        result = data.get("result")
        return result if isinstance(result, dict) else {}

    def _post_tolerating(self, path: str, payload: dict, tolerated: set[int]) -> dict | None:
        """执行请求，把 `tolerated` 中的错误码当成"正常但无结果"返回 None。"""
        try:
            return self._post(path, payload)
        except FaceAPIError as exc:
            if exc.code in tolerated:
                return None
            raise

    # -- 业务接口 ----------------------------------------------------------

    def add_user(
        self,
        image: str | Path | np.ndarray,
        user_id: str,
        name: str,
        group_id: str,
        action_type: str = "APPEND",
        quality_control: str = "NORMAL",
        liveness_control: str = "NORMAL",
    ) -> str:
        """注册人脸。返回云端分配的 face_token（入库后永久有效）。

        action_type=APPEND 时，同一 user_id 下已有人脸会被保留，新脸追加；
        这是"同名重复注册"提升识别率的依据。

        liveness_control 默认 NORMAL：活体检测会拒绝二次翻拍的照片。若使用者是从
        已有的图片文件（而非现场拍摄）注册，可能会被误拒并返回 223120，此时可通过
        .env 中的 LIVENESS_CONTROL 调低等级。
        """
        data = self._post(
            "/faceset/user/add",
            {
                "image": encode_image(image),
                "image_type": "BASE64",
                "group_id": group_id,
                "user_id": user_id,
                "user_info": name,
                "action_type": action_type,
                "quality_control": quality_control,
                "liveness_control": liveness_control,
            },
        )
        return str(self._result_of(data).get("face_token", ""))

    def search(
        self,
        image: str | Path | np.ndarray,
        group_id: str,
        threshold: int,
        max_user_num: int = 5,
        quality_control: str = "NORMAL",
        liveness_control: str = "NONE",
    ) -> list[dict]:
        """在指定用户组中做 1:N 检索。

        返回按 score 降序排列的候选 [{user_id, user_info, score, group_id}, ...]。
        云端未找到匹配用户（222207）会被归一化为空列表，而不是抛异常。
        """
        data = self._post_tolerating(
            "/search",
            {
                "image": encode_image(image),
                "image_type": "BASE64",
                "group_id_list": group_id,
                "match_threshold": threshold,
                "max_user_num": max_user_num,
                "quality_control": quality_control,
                "liveness_control": liveness_control,
                "face_sort_type": 0,
            },
            tolerated={NO_MATCH_USER},
        )
        if data is None:
            return []

        candidates = [
            {
                "user_id": item.get("user_id", ""),
                "user_info": item.get("user_info", ""),
                "group_id": item.get("group_id", ""),
                "score": float(item.get("score", 0.0)),
            }
            for item in self._result_of(data).get("user_list", [])
        ]
        candidates.sort(key=lambda item: item["score"], reverse=True)
        return candidates

    def delete_user(self, user_id: str, group_id: str) -> DeleteResult:
        """从云端删除人员。

        云端本就不存在该用户（223103）不算失败，返回 removed=False，
        交由上层决定是否继续清理本地档案。
        """
        data = self._post_tolerating(
            "/faceset/user/delete",
            {"user_id": user_id, "group_id": group_id},
            tolerated={USER_NOT_EXIST},
        )
        return DeleteResult(removed=data is not None)

    def delete_face(self, user_id: str, group_id: str, face_token: str) -> bool:
        """删除某个用户名下的一张人脸。返回是否确实删除。"""
        data = self._post_tolerating(
            "/faceset/face/delete",
            {"user_id": user_id, "group_id": group_id, "face_token": face_token},
            tolerated={FACE_NOT_EXIST},
        )
        return data is not None

    def get_face_list(self, user_id: str, group_id: str) -> list[dict]:
        """查询某用户名下的全部人脸，用于人脸库明细展示。"""
        data = self._post(
            "/faceset/face/getlist", {"user_id": user_id, "group_id": group_id}
        )
        return [
            {"face_token": item.get("face_token", ""), "ctime": item.get("ctime", "")}
            for item in self._result_of(data).get("face_list", [])
        ]


# --------------------------------------------------------------------------
# 冒烟测试
# --------------------------------------------------------------------------


def _smoke_test() -> None:
    """全链路冒烟测试：取 token → 注册 → 检索 → 删除。

    需要 .env 中已配置真实 AK/SK。会消耗约 3 次接口配额。
    """
    from config import ConfigError, load_config

    try:
        config = load_config()
    except ConfigError as exc:
        raise SystemExit(f"配置有误，冒烟测试无法进行：\n{exc}") from None

    # lena02.png 位于上一级 opencv/ 目录，是一张标准人脸测试图
    sample = Path(__file__).resolve().parent.parent.parent / "lena02.png"
    if not sample.exists():
        raise SystemExit(f"缺少测试图片：{sample}")

    client = BaiduFaceClient(config.api_key, config.secret_key)
    user_id = "u_smoketest0000"
    name = "冒烟测试"
    group = config.group_id

    try:
        print(f"[1/4] 获取 access_token ...")
        token = client._get_access_token()
        print(f"      OK，token 前缀 {token[:12]}…  缓存生效={client._get_access_token() == token}")

        print(f"[2/4] 注册 {name} 到用户组 {group} ...")
        # lena02.png 是一张扫描版测试图，不是现场拍摄，会被活体检测判为二次翻拍
        # （223120）。冒烟测试只验证链路通断，因此这里关闭活体控制。
        face_token = client.add_user(
            sample, user_id, name, group, liveness_control="NONE"
        )
        print(f"      OK，face_token={face_token}")

        # 官方文档：注册完毕后生效时间一般为 5s 以内，立即检索可能查不到
        print("      等待 6 秒让注册生效 …")
        time.sleep(6)

        print(f"[3/4] 检索同一张图片 ...")
        candidates = client.search(sample, group, threshold=config.match_threshold)
        if not candidates:
            print("      未返回候选（可能是阈值过高，可稍后重试）")
        for item in candidates:
            print(
                f"      {item['user_info']} (user_id={item['user_id']}) "
                f"score={item['score']:.1f}"
            )

        print(f"[4/4] 删除 {user_id} ...")
        result = client.delete_user(user_id, group)
        print(f"      OK，removed={result.removed}")
        print("      再次删除应返回 removed=False ...", end=" ")
        print(client.delete_user(user_id, group).removed is False)

        print("\n全链路冒烟测试通过。")
    except (FaceAPIError, FaceNetworkError) as exc:
        friendly = exc.friendly if isinstance(exc, FaceAPIError) else exc.friendly
        raise SystemExit(f"\n冒烟测试失败：{friendly}") from exc
    finally:
        client.close()


if __name__ == "__main__":
    _smoke_test()
