"""主窗口：三个功能页签 + 状态栏，以及跨页签共用的异步/忙碌/错误处理辅助。

设计要点（见 design.md 决策 5）：
- 所有网络请求通过 `run_in_background` 放到工作线程，结果经**结果队列**回投主线程；
- 按钮点击回调里绝不直接发请求；
- 任何未预期异常都被 report_callback_exception 接住，窗口不会整体退出。

为什么用队列而不是在工作线程里直接 `root.after(0, ...)`：
`after()` 会调用 Tcl 的 `createcommand`，而 Tcl 解释器只允许主线程操作它。
当主线程不在 `mainloop()` 内部时（例如单测里用 `update()` 驱动事件循环），
从工作线程调用 `after` 会直接抛 `RuntimeError: main thread is not in main loop`。
改成"工作线程只往 Queue 里放结果，主线程定时轮询取出并执行回调"，
既保证回调始终在主线程执行，也不依赖主线程此刻是否卡在 mainloop 里。
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
import traceback
from tkinter import messagebox, ttk
from typing import Callable, TypeVar

from config import Config
from core.baidu_client import BaiduFaceClient
from core.camera import CameraStream
from core.database import PersonStore
from core.errors import describe_exception
from ui.faceset_tab import FacesetTab
from ui.recognize_tab import RecognizeTab
from ui.register_tab import RegisterTab

T = TypeVar("T")

IDLE_STATUS = "就绪"

# 主线程轮询工作线程结果的间隔
RESULT_POLL_MS = 40


class MainWindow(tk.Tk):
    def __init__(
        self,
        config: Config,
        store: PersonStore,
        client: BaiduFaceClient,
        camera: CameraStream,
    ) -> None:
        super().__init__()
        self.settings = config
        self.store = store
        self.client = client
        self.camera = camera

        self.title("人脸识别系统 — 百度智能云")
        self.geometry("1000x720")
        self.minsize(920, 660)

        self._result_queue: queue.Queue[tuple[str, object, object]] = queue.Queue()
        self._poll_id: str | None = None

        self._build_body()
        self._build_statusbar()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.report_callback_exception = self._on_callback_exception

        self.camera.start()
        self.after(200, self._on_tab_changed)
        self._poll_results()
        self.status(f"就绪 · 人脸库用户组：{config.group_id} · 判定阈值：{config.match_threshold} 分")

    # -- 布局 --------------------------------------------------------------

    def _build_body(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(10, 4))

        self.register_tab = RegisterTab(self.notebook, self)
        self.recognize_tab = RecognizeTab(self.notebook, self)
        self.faceset_tab = FacesetTab(self.notebook, self)

        self.notebook.add(self.register_tab, text="  人员注册  ")
        self.notebook.add(self.recognize_tab, text="  单人识别  ")
        self.notebook.add(self.faceset_tab, text="  人脸库管理  ")

        self._tabs = (self.register_tab, self.recognize_tab, self.faceset_tab)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _build_statusbar(self) -> None:
        bar = ttk.Frame(self, relief="sunken", padding=(8, 4))
        bar.pack(fill="x", side="bottom")
        self._status_var = tk.StringVar(value=IDLE_STATUS)
        ttk.Label(bar, textvariable=self._status_var, anchor="w").pack(fill="x")

    # -- 页签切换 ----------------------------------------------------------

    def _current_tab(self):
        index = self.notebook.index(self.notebook.select())
        return self._tabs[index]

    def _on_tab_changed(self, _event: object = None) -> None:
        """只让当前可见页签的预览轮询取帧。

        两个页签同时轮询会争抢容量为 1 的帧队列，导致两边都频繁拿到 None，
        因此切换时必须停掉其他页签的预览。
        """
        try:
            current = self._current_tab()
        except Exception:
            return

        for tab in self._tabs:
            if tab is current:
                continue
            tab.on_hide()
            preview = tab.preview()
            if preview is not None:
                preview.stop()

        preview = current.preview()
        if preview is not None:
            preview.start()
        current.on_show()

    # -- 异步辅助 ----------------------------------------------------------

    def run_in_background(
        self,
        work: Callable[[], T],
        on_success: Callable[[T], None] | None = None,
        on_error: Callable[[BaseException], None] | None = None,
    ) -> None:
        """在工作线程执行 work()，回调一律在主线程执行。

        工作线程只把结果放进队列，绝不去碰 Tk；由主线程的 `_poll_results`
        取出并调用回调，因此界面更新始终发生在主线程。
        """

        def runner() -> None:
            try:
                result = work()
            except BaseException as exc:  # noqa: BLE001 - 工作线程必须兜住一切
                self._result_queue.put(("error", exc, on_error))
            else:
                self._result_queue.put(("ok", result, on_success))

        threading.Thread(target=runner, daemon=True).start()

    def _poll_results(self) -> None:
        """主线程侧的结果泵：取出工作线程的结果并执行回调。"""
        while True:
            try:
                kind, payload, callback = self._result_queue.get_nowait()
            except queue.Empty:
                break
            try:
                if kind == "error":
                    if callback is not None:
                        callback(payload)  # type: ignore[operator]
                    else:
                        self.show_error(describe_exception(payload))  # type: ignore[arg-type]
                elif callback is not None:
                    callback(payload)  # type: ignore[operator]
            except Exception:
                # 回调本身出错不能拖垮结果泵，否则后续结果全部堵死
                traceback.print_exc()
                self.status("界面更新时发生错误，详情见控制台。")

        self._poll_id = self.after(RESULT_POLL_MS, self._poll_results)

    # -- 界面状态辅助 ------------------------------------------------------

    def status(self, text: str) -> None:
        self._status_var.set(text)

    def set_busy(self, widget: tk.Widget, busy: bool, busy_text: str | None = None) -> None:
        """操作进行中禁用触发按钮，避免重复点击浪费接口配额。"""
        try:
            if busy:
                widget.configure(state="disabled")
                if busy_text is not None and hasattr(widget, "_idle_text"):
                    widget.configure(text=busy_text)
            else:
                widget.configure(state="normal")
                if hasattr(widget, "_idle_text"):
                    widget.configure(text=widget._idle_text)
        except tk.TclError:
            pass  # 控件已销毁

    def show_error(self, message: str, title: str = "操作失败") -> None:
        messagebox.showerror(title, message, parent=self)
        self.status(message.splitlines()[0])

    def show_info(self, message: str, title: str = "提示") -> None:
        messagebox.showinfo(title, message, parent=self)

    def show_warning(self, message: str, title: str = "提示") -> None:
        messagebox.showwarning(title, message, parent=self)

    # -- 异常与退出 --------------------------------------------------------

    def _on_callback_exception(self, exc_type, exc_value, exc_tb) -> None:
        """Tkinter 回调里的未捕获异常：记录并提示，但保持窗口存活。"""
        traceback.print_exception(exc_type, exc_value, exc_tb)
        try:
            self.show_error(describe_exception(exc_value))
        except Exception:
            pass

    def _on_close(self) -> None:
        if self._poll_id is not None:
            try:
                self.after_cancel(self._poll_id)
            except Exception:
                pass
            self._poll_id = None
        try:
            self.camera.stop()
        except Exception:
            pass
        try:
            self.client.close()
        except Exception:
            pass
        self.destroy()
