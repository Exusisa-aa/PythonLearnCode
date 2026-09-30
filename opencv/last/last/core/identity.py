"""姓名 → 云端 user_id 的派生。

百度要求 `user_id` 仅由数字、字母、下划线组成且不超过 48 字节，中文姓名不能直接
使用；同时希望**同一姓名始终派生出同一 user_id**，这样同名重复注册会落到同一个
用户下，从而复用百度"同一 user_id 最多 20 张人脸"的能力来提升识别命中率。

姓名本身通过云端 `user_info` 字段承载（支持中文，上限 256 字节）。
详见 design.md 决策 2。
"""

from __future__ import annotations

import hashlib

USER_ID_PREFIX = "u"
_HASH_LENGTH = 16


def derive_user_id(name: str) -> str:
    """由姓名确定性地派生出一个合法的云端 user_id（共 17 字符）。"""
    digest = hashlib.md5(name.strip().encode("utf-8")).hexdigest()
    return USER_ID_PREFIX + digest[:_HASH_LENGTH]


def _self_test() -> None:
    # 中文姓名也要产出纯 ASCII 的 user_id
    for name in ("张三", "李四", "Alice", "王五_"):
        user_id = derive_user_id(name)
        assert user_id.isascii(), f"{name} 派生出非 ASCII user_id"
        assert all(c.isalnum() or c == "_" for c in user_id), f"{name} 含非法字符"
        assert len(user_id) <= 48, f"{name} 的 user_id 超长"

    # 稳定性：同一姓名必须得到同一结果
    assert derive_user_id("张三") == derive_user_id("张三")
    # 首尾空白不影响派生
    assert derive_user_id("  张三  ") == derive_user_id("张三")
    # 不同姓名不应碰撞
    assert derive_user_id("张三") != derive_user_id("李四")

    print(f"identity.py 自测通过：张三 -> {derive_user_id('张三')}")


if __name__ == "__main__":
    _self_test()
