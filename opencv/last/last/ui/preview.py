"""摄像头预览/静态图片显示控件，供注册页与识别页共用。

两种模式：
- live：定时从 CameraStream 取最新帧显示；
- static：显示一张固定的图片（抓拍结果或用户选择的文件）。

关键陷阱：`ImageTk.PhotoImage` 对象必须被本控件持有引用（`self._photo`），
否则会被 Python 垃圾回收，界面上表现为画面空白或闪烁。
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Callable

import cv2
import numpy as np
from PIL import Image, ImageTk

from core.images import ImageEncodeError, load_bgr_image

if TYPE_CHECKING:
    from ui.main_window import MainWindow

PREVIEW_WIDTH = 480
PREVIEW_HEIGHT = 360

# 约 30 FPS；用 after 轮询而非线程直接刷界面，保证所有 UI 操作都在主线程
REFRESH_INTERVAL_MS = 33

_PLACEHOLDER_RUNNING = "正在启动摄像头…"
_PLACEHOLDER_FAILED = "摄像头不可用\n请改用「选择文件」"


def bgr_to_photoimage(frame: np.ndarray, box: tuple[int, int]) -> ImageTk.PhotoImage:
    """BGR 帧 → 等比缩放到 box 内 → Tk 可显示的 PhotoImage。"""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb)
    image.thumbnail(box, Image.LANCZOS)
    return ImageTk.PhotoImage(image)


class CameraPreview(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        app: "MainWindow",
        box: tuple[int, int] = (PREVIEW_WIDTH, PREVIEW_HEIGHT),
        on_camera_state: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(master)
        self._app = app
        self._box = box
        # 摄像头状态变化时的回调，用于让"抓拍"按钮跟随可用性自动启用/禁用
        self._on_camera_state = on_camera_state
        self._last_camera_state: str | None = None
        self._mode = "live"
        self._static_frame: np.ndarray | None = None
        self._last_live: np.ndarray | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._after_id: str | None = None

        self._label = ttk.Label(
            self,
            width=0,
            anchor="center",
            justify="center",
            background="#1e1e1e",
            foreground="#bbbbbb",
            text=_PLACEHOLDER_RUNNING,
            compound="center",
        )
        self._label.pack(fill="both", expand=True)

    # -- 生命周期 ----------------------------------------------------------

    def start(self) -> None:
        if self._after_id is None:
            self._tick()

    def stop(self) -> None:
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    # -- 模式切换 ----------------------------------------------------------

    def show_live(self) -> None:
        self._mode = "live"
        self._static_frame = None

    def show_static(self, frame: np.ndarray) -> None:
        self._mode = "static"
        self._static_frame = frame
        self._render(frame)

    def show_static_file(self, path: str) -> bool:
        """从文件加载并固定显示。返回是否成功。

        经 core.images 读取而非 `cv2.imread`：后者在 Windows 上读不了含中文的路径。
        """
        try:
            frame = load_bgr_image(path)
        except ImageEncodeError:
            return False
        self.show_static(frame)
        return True

    @property
    def mode(self) -> str:
        return self._mode

    def current_frame(self) -> np.ndarray | None:
        """取当前应当提交给接口的图片：静态模式取固定图，实时模式取最新帧。"""
        if self._mode == "static":
            return self._static_frame
        # 不能写 `camera.read() or self._last_live`：read() 返回的是 NumPy 数组，
        # `or` 会对数组做真值判断，触发 "truth value of an array is ambiguous"。
        frame = self._app.camera.read()
        if frame is not None:
            return frame
        return self._last_live

    # -- 刷新循环 ----------------------------------------------------------

    def _tick(self) -> None:
        # 摄像头是异步启动的：状态可能在页签打开之后才变为 running，
        # 因此在轮询里同步状态，而不是只在页签显示时同步一次。
        state = self._app.camera.state
        if state != self._last_camera_state:
            self._last_camera_state = state
            if self._on_camera_state is not None:
                try:
                    self._on_camera_state(state)
                except tk.TclError:
                    pass

        if self._mode == "live":
            frame = self._app.camera.read()
            if frame is not None:
                self._last_live = frame
            if frame is not None or self._last_live is not None:
                self._render(self._last_live)
            else:
                self._render_placeholder()
        self._after_id = self.after(REFRESH_INTERVAL_MS, self._tick)

    def _render(self, frame: np.ndarray) -> None:
        self._photo = bgr_to_photoimage(frame, self._box)
        self._label.configure(image=self._photo, text="")

    def _render_placeholder(self) -> None:
        self._photo = None
        if self._app.camera.state == "failed":
            text = _PLACEHOLDER_FAILED
        elif self._app.camera.available:
            text = "等待画面…"
        else:
            text = _PLACEHOLDER_RUNNING
        self._label.configure(image="", text=text)
