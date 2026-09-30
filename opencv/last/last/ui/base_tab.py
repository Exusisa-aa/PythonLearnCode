"""页签基类：约定主窗口与各页签之间的接口。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.main_window import MainWindow
    from ui.preview import CameraPreview


class BaseTab(ttk.Frame):
    def __init__(self, master: tk.Misc, app: "MainWindow") -> None:
        super().__init__(master, padding=12)
        self.app = app

    def preview(self) -> "CameraPreview | None":
        """本页签使用的预览控件；没有则返回 None。"""
        return None

    def on_show(self) -> None:
        """页签被切换到前台。"""

    def on_hide(self) -> None:
        """页签被切走。"""
