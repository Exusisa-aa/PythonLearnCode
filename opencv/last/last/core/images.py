"""图片读写辅助。

**不要使用 `cv2.imread` / `cv2.imwrite`。**
它们在 Windows 上无法处理含非 ASCII 字符的路径——文件明明存在，
`cv2.imread` 却返回 None，`cv2.imwrite` 则静默失败。中文文件名和中文用户目录
（如 `C:\\Users\\张三\\Pictures\\`）在这里都非常常见，所以统一改走：

    读：path.read_bytes() → np.frombuffer → cv2.imdecode
    写：cv2.imencode → path.write_bytes()

本模块同时负责把图片编码成百度接口要求的 Base64（不含 `data:` 前缀）。
"""

from __future__ import annotations

import base64
from pathlib import Path

import cv2
import numpy as np

# 百度要求 Base64 编码后的图片不超过 2M
MAX_BASE64_BYTES = 2 * 1024 * 1024
# 超过该长度时先缩放到长边不超过 1920 再编码
MAX_IMAGE_SIDE = 1920

SUPPORTED_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".bmp"})


class ImageEncodeError(ValueError):
    """图片无法用于接口请求，消息面向使用者。"""


def load_bgr_image(source: str | Path | np.ndarray) -> np.ndarray:
    """把本地文件路径或已解码的帧统一转成 BGR ndarray。"""
    if isinstance(source, np.ndarray):
        if source.size == 0:
            raise ImageEncodeError("图像数据为空，请重新采集。")
        return source

    path = Path(source)
    if not path.exists():
        raise ImageEncodeError(f"图片文件不存在：{path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        readable = "、".join(sorted(s.lstrip(".").upper() for s in SUPPORTED_SUFFIXES))
        raise ImageEncodeError(
            f"不支持的图片格式：{suffix or '（无扩展名）'}。仅支持 {readable}，不支持 GIF。"
        )

    buffer = np.frombuffer(path.read_bytes(), dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise ImageEncodeError(f"无法解析该图片文件（可能已损坏）：{path.name}")
    return frame


def save_bgr_image(frame: np.ndarray, path: str | Path, quality: int = 95) -> bool:
    """把 BGR 帧写成 JPEG 文件。返回是否成功。中文路径同样安全。"""
    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not ok:
            return False
        target.write_bytes(buffer.tobytes())
        return True
    except Exception:
        return False


def _encode_bgr(frame: np.ndarray) -> str:
    """把 BGR 帧编码成符合百度要求的 Base64 字符串。

    先用高质量 JPEG 试编码；若超出 2M 限制则逐步降质，仍超限则缩小分辨率。
    """
    attempts = [(None, quality) for quality in (90, 80, 70)]
    attempts.append((MAX_IMAGE_SIDE, 80))
    attempts.append((MAX_IMAGE_SIDE, 65))

    last_size = 0
    for max_side, quality in attempts:
        image = frame
        if max_side is not None:
            height, width = frame.shape[:2]
            longest = max(height, width)
            if longest > max_side:
                scale = max_side / longest
                image = cv2.resize(
                    frame,
                    (max(1, int(width * scale)), max(1, int(height * scale))),
                    interpolation=cv2.INTER_AREA,
                )

        ok, buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not ok:
            continue

        encoded = base64.b64encode(buffer.tobytes()).decode("ascii")
        last_size = len(encoded)
        if last_size <= MAX_BASE64_BYTES:
            return encoded

    raise ImageEncodeError(
        f"图片过大，压缩后仍为 {last_size / 1024 / 1024:.1f}M，超出接口 2M 限制。"
        "请换一张分辨率更低的照片。"
    )


def encode_image(source: str | Path | np.ndarray) -> str:
    """把图片文件路径或 OpenCV BGR 帧编码为 Base64（不含 data URI 前缀）。"""
    return _encode_bgr(load_bgr_image(source))
