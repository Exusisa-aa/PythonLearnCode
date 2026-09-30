"""百度人脸识别接口的错误码映射与异常类型。

错误码取自官方《软件说明文档》"接口流控及鉴权错误码"与各接口的错误码表。
目标是：任何一次失败都能给使用者一句可读的中文说明 + 一条可操作的建议，
而不是把 223113 这样的数字直接抛到界面上。
"""

from __future__ import annotations

# ---- 客户端需要分支处理的错误码 ----
TOKEN_INVALID = 110
TOKEN_EXPIRED = 111
NO_MATCH_USER = 222207  # 1:N 检索未找到匹配用户，属正常业务结果而非故障
USER_NOT_EXIST = 223103
FACE_NOT_EXIST = 223106
GROUP_NOT_EXIST = 223100
GROUP_ALREADY_EXIST = 223101

_TOKEN_ERRORS = frozenset({TOKEN_INVALID, TOKEN_EXPIRED})
_QUOTA_ERRORS = frozenset({17, 18, 19})

# ---- 可读提示 ----

_QUOTA_MESSAGES = {
    17: "今日免费额度已用完。可在百度智能云控制台购买次数包或开通按量后付费。",
    18: "调用频率超出限制（QPS 超限）。请稍候几秒再试。",
    19: "请求总量已超出限制。可在百度智能云控制台购买次数包或开通按量后付费。",
}

_AUTH_MESSAGES = {
    100: "access_token 参数无效，请检查 .env 中的 AK/SK 是否正确。",
    110: "access_token 已失效，请重新获取；若持续出现请核对 AK/SK。",
    111: "access_token 已过期，程序会自动重新获取。",
    2: "百度服务暂时不可用，请稍后重试。",
    4: "百度集群超限额，请稍后重试。",
    6: "当前应用没有该接口的权限。请确认调用的是 V3 版本接口，且账号已完成企业实名认证。",
}

_IMAGE_MESSAGES = {
    222200: "请求体不是合法的 JSON，通常是程序内部错误。",
    222202: "图片中未检测到人脸。请让面部清晰完整地出现在画面中。",
    222203: "无法解析图片中的人脸。请换一张更清晰的照片，或确认图片未损坏。",
    222204: "从图片 URL 下载失败。请确认该 URL 可公网访问。",
    222205: "服务端请求失败，请重试。",
    222206: "服务端请求失败，请重试。",
    222207: "未找到匹配的用户。",
    222208: "请求体中图片数量不正确。",
    222209: "face_token 不存在。未入库的 face_token 有效期只有 1 小时。",
    222301: "获取人脸失败，请重试；若持续出现请提交工单。",
    222304: "图片尺寸太大。请确保分辨率不超过 6000×6000。",
    222915: "百度后端服务繁忙，请重试。",
}

# 人脸质量类：逐条给出"哪里不合格"，让使用者知道怎么重拍
_QUALITY_MESSAGES = {
    223113: "人脸有遮挡。请勿遮挡面部后重拍。",
    223114: "人脸模糊。拍摄时请保持稳定，避免晃动。",
    223115: "人脸光照不佳。请到光线适宜的地方拍摄。",
    223116: "人脸不完整。请将完整的人脸移入画面内。",
    223120: "活体检测未通过，照片中的人脸疑似二次翻拍。请拍摄真人。",
    223121: "左眼遮挡程度过高。请勿遮挡左眼。",
    223122: "右眼遮挡程度过高。请勿遮挡右眼。",
    223123: "左脸遮挡程度过高。请勿遮挡左脸颊。",
    223124: "右脸遮挡程度过高。请勿遮挡右脸颊。",
    223125: "下巴遮挡程度过高。请勿遮挡下巴。",
    223126: "鼻子遮挡程度过高。请勿遮挡鼻子。",
    223127: "嘴巴遮挡程度过高。请勿遮挡嘴巴。",
    223129: "人脸未面向正前方，角度超出限制。请使用正面照。",
    223131: "合成图检测未通过，照片疑似经过 PS 或人脸融合处理。请使用原始照片。",
}

_GROUP_MESSAGES = {
    223100: "用户组不存在。请检查 .env 中的 FACE_GROUP_ID 是否正确。",
    223101: "用户组已存在。",
    223103: "该用户在人脸库中不存在。",
    223106: "该人脸在人脸库中不存在。",
    223111: "目标用户组不存在。",
    223202: "请求的场景类型与用户组设置不匹配。",
}

# 参数格式错误：程序侧的问题，提示统一风格，附上原始字段名
_PARAM_MESSAGES = {
    222013: "image 参数格式错误。",
    222015: "image_type 参数格式错误。",
    222016: "max_face_num 参数格式错误。",
    222017: "face_field 参数格式错误。",
    222018: "user_id 参数格式错误（仅允许数字、字母、下划线）。",
    222019: "quality_control 参数格式错误。",
    222020: "liveness_control 参数格式错误。",
    222021: "max_user_num 参数格式错误。",
    222024: "face_type 参数格式错误。",
    222030: "match_threshold 参数格式错误。",
    222039: "face_sort_type 参数格式错误。",
    222043: "display_corp_image 参数格式错误。",
    222154: "liveness_strategy 参数格式错误。",
    222201: "scene_type 参数格式错误。",
    223130: "spoofing_control 参数格式错误。",
}

ERROR_MESSAGES: dict[int, str] = {
    **_AUTH_MESSAGES,
    **_QUOTA_MESSAGES,
    **_PARAM_MESSAGES,
    **_IMAGE_MESSAGES,
    **_QUALITY_MESSAGES,
    **_GROUP_MESSAGES,
}


def is_token_error(code: int) -> bool:
    """token 失效类错误——客户端应清缓存、重取 token 后重试一次。"""
    return code in _TOKEN_ERRORS


def is_quota_error(code: int) -> bool:
    return code in _QUOTA_ERRORS


def friendly_message(code: int, raw_message: str = "") -> str:
    """把错误码翻译为面向使用者的中文说明。

    未收录的错误码退回原始信息，避免显示"未知错误"丢失排查线索。
    """
    known = ERROR_MESSAGES.get(code)
    if known:
        return known
    if raw_message:
        return f"接口返回错误（{code}）：{raw_message}"
    return f"接口返回未知错误（{code}）。"


class FaceAPIError(Exception):
    """百度接口返回了非零 error_code。"""

    def __init__(self, code: int, raw_message: str = "") -> None:
        self.code = code
        self.raw_message = raw_message
        self.friendly = friendly_message(code, raw_message)
        super().__init__(f"[{code}] {raw_message or self.friendly}")

    @property
    def is_token_error(self) -> bool:
        return is_token_error(self.code)

    @property
    def is_quota_error(self) -> bool:
        return is_quota_error(self.code)


class FaceNetworkError(Exception):
    """请求未能拿到响应：超时、连接失败等。

    与 FaceAPIError 分开，是为了让上层不会把网络故障误报成"陌生人"。
    """

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)

    @property
    def friendly(self) -> str:
        return f"网络请求失败：{self.detail}。请检查网络连接后重试。"


def describe_exception(exc: BaseException) -> str:
    """把任意异常翻译成一句面向使用者的中文说明。

    放在本模块而不是界面层，是为了让各页签都能直接使用，避免
    界面模块之间相互 import 造成循环依赖。
    """
    if isinstance(exc, (FaceAPIError, FaceNetworkError)):
        return exc.friendly
    if isinstance(exc, ValueError) and str(exc):
        # ImageEncodeError 等本地校验类错误，消息本身已是可读中文
        return str(exc)
    return f"发生未预期的错误：{exc}"
