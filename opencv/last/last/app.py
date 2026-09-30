"""程序入口。

    python app.py

启动顺序：加载配置 → 建库 → 建客户端 → 建窗口 → 进入事件循环。
配置缺失时给出可读提示而不是崩溃，退出码为 1。
"""

from __future__ import annotations

import sys
import tkinter as tk
import traceback
from tkinter import messagebox

from config import ConfigError, load_config
from core.baidu_client import BaiduFaceClient
from core.camera import CameraStream
from core.database import PersonStore
from ui.main_window import MainWindow


def _show_fatal(title: str, message: str) -> None:
    """窗口尚未建立时的致命错误提示：先写 stderr，再尽力弹窗。"""
    print(f"{title}：\n{message}", file=sys.stderr)
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        pass  # 无图形环境时仅保留 stderr 输出


def main() -> int:
    try:
        settings = load_config()
    except ConfigError as exc:
        _show_fatal("配置有误", str(exc))
        return 1

    try:
        store = PersonStore(settings.db_path)
    except Exception as exc:
        traceback.print_exc()
        _show_fatal("无法打开本地数据库", f"初始化档案数据库失败：{exc}")
        return 1

    client = BaiduFaceClient(settings.api_key, settings.secret_key)
    camera = CameraStream()

    try:
        window = MainWindow(settings, store, client, camera)
    except Exception as exc:
        traceback.print_exc()
        client.close()
        camera.stop()
        _show_fatal("启动失败", f"界面初始化失败：{exc}")
        return 1

    try:
        window.mainloop()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
