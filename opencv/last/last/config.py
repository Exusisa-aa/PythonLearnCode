"""配置加载：从 .env 读取百度智能云凭据与运行参数。

所有路径均以本文件所在目录为基准，因此程序可以从任意工作目录启动。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PHOTO_DIR = DATA_DIR / "faces"
DB_PATH = DATA_DIR / "faces.db"

DEFAULT_GROUP_ID = "face_recognition"
DEFAULT_MATCH_THRESHOLD = 80

CONTROL_LEVELS = ("NONE", "LOW", "NORMAL", "HIGH")
DEFAULT_QUALITY_CONTROL = "NORMAL"
DEFAULT_LIVENESS_CONTROL = "NORMAL"

# 姓名写入百度 user_info 字段，该字段上限 256 字节；UTF-8 下中文占 3 字节。
MAX_NAME_BYTES = 256


class ConfigError(RuntimeError):
    """配置缺失或非法。消息面向使用者，可直接展示在界面上。"""


@dataclass(frozen=True)
class Config:
    api_key: str
    secret_key: str
    group_id: str
    match_threshold: int
    quality_control: str
    liveness_control: str
    db_path: Path
    photo_dir: Path


def load_config() -> Config:
    """读取配置。缺少 AK/SK 时抛出 ConfigError，而不是等到发请求才失败。"""
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("BAIDU_API_KEY", "").strip()
    secret_key = os.getenv("BAIDU_SECRET_KEY", "").strip()

    missing = [
        name
        for name, value in (("BAIDU_API_KEY", api_key), ("BAIDU_SECRET_KEY", secret_key))
        if not value
    ]
    if missing:
        raise ConfigError(
            "缺少配置项：" + "、".join(missing) + "\n\n"
            "请将 .env.example 复制为 .env，并填入百度智能云控制台应用的 API Key 与 Secret Key。\n"
            "获取方式：百度智能云控制台 → 人脸识别 → 创建应用。"
        )

    group_id = os.getenv("FACE_GROUP_ID", "").strip() or DEFAULT_GROUP_ID
    match_threshold = _parse_threshold(os.getenv("MATCH_THRESHOLD", ""))
    quality_control = _parse_control(
        os.getenv("QUALITY_CONTROL", ""), "QUALITY_CONTROL", DEFAULT_QUALITY_CONTROL
    )
    liveness_control = _parse_control(
        os.getenv("LIVENESS_CONTROL", ""), "LIVENESS_CONTROL", DEFAULT_LIVENESS_CONTROL
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)

    return Config(
        api_key=api_key,
        secret_key=secret_key,
        group_id=group_id,
        match_threshold=match_threshold,
        quality_control=quality_control,
        liveness_control=liveness_control,
        db_path=DB_PATH,
        photo_dir=PHOTO_DIR,
    )


def _parse_threshold(raw: str) -> int:
    """阈值必须在 0~100 之间；留空或非法时回退到百度官方推荐值 80。"""
    if not raw.strip():
        return DEFAULT_MATCH_THRESHOLD
    try:
        value = int(float(raw))
    except ValueError:
        raise ConfigError(f"MATCH_THRESHOLD 必须是数字，当前值为：{raw!r}") from None
    if not 0 <= value <= 100:
        raise ConfigError(f"MATCH_THRESHOLD 必须在 0~100 之间，当前值为：{value}")
    return value


def _parse_control(raw: str, name: str, default: str) -> str:
    """质量/活体控制等级，留空则用默认值。"""
    value = raw.strip().upper() or default
    if value not in CONTROL_LEVELS:
        raise ConfigError(
            f"{name} 只能是 {'/'.join(CONTROL_LEVELS)} 之一，当前值为：{raw!r}"
        )
    return value
