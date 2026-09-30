"""单人识别页签：对待识别图片做 1:N 检索，输出姓名或"陌生人"。"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from core.errors import describe_exception
from ui.base_tab import BaseTab
from ui.preview import CameraPreview
from ui.register_tab import IMAGE_FILETYPES

UNKNOWN_NAME = "陌生人"

_COLOR_MATCH = "#0a7d32"
_COLOR_STRANGER = "#c0392b"
_COLOR_IDLE = "#555555"


class RecognizeTab(BaseTab):
    def __init__(self, master: tk.Misc, app) -> None:
        super().__init__(master, app)
        self._build()

    # -- 构建界面 ----------------------------------------------------------

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        panel = ttk.Frame(self)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        panel.columnconfigure(0, weight=1)

        ttk.Label(panel, text="单人识别", font=("", 14, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            panel,
            text="采集一张人脸照片，在云端人脸库中查找最相似的人员。",
            foreground="#555555",
            wraplength=380,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(0, 16))

        ttk.Label(panel, text="待识别图片").grid(row=2, column=0, sticky="w")

        picker = ttk.Frame(panel)
        picker.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        picker.columnconfigure((0, 1), weight=1)

        self.capture_btn = ttk.Button(picker, text="抓拍当前画面", command=self._on_capture)
        self.capture_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4), ipady=3)

        self.file_btn = ttk.Button(picker, text="选择文件…", command=self._on_choose_file)
        self.file_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0), ipady=3)

        self.live_btn = ttk.Button(panel, text="返回实时画面", command=self._on_back_to_live)
        self.live_btn.grid(row=4, column=0, sticky="ew", pady=(6, 0))

        self.image_state = tk.StringVar(value="尚未采集图片")
        ttk.Label(panel, textvariable=self.image_state, foreground="#777777").grid(
            row=5, column=0, sticky="w", pady=(8, 14)
        )

        self.recognize_btn = ttk.Button(panel, text="识 别", command=self._on_recognize)
        self.recognize_btn._idle_text = "识 别"
        self.recognize_btn.grid(row=6, column=0, sticky="ew", ipady=8)

        ttk.Separator(panel, orient="horizontal").grid(row=7, column=0, sticky="ew", pady=16)

        result_box = ttk.Frame(panel, padding=12, relief="groove")
        result_box.grid(row=8, column=0, sticky="ew")
        result_box.columnconfigure(0, weight=1)

        self.result_label = ttk.Label(
            result_box,
            text="—",
            font=("", 22, "bold"),
            foreground=_COLOR_IDLE,
            anchor="center",
        )
        self.result_label.grid(row=0, column=0, sticky="ew", pady=(4, 8))

        self.detail_var = tk.StringVar(value="尚未识别")
        ttk.Label(
            result_box,
            textvariable=self.detail_var,
            foreground="#555555",
            anchor="center",
            justify="center",
            wraplength=340,
        ).grid(row=1, column=0, sticky="ew")

        self.threshold_var = tk.StringVar(
            value=f"判定阈值：{self.app.settings.match_threshold} 分"
        )
        ttk.Label(
            result_box, textvariable=self.threshold_var, foreground="#999999", anchor="center"
        ).grid(row=2, column=0, sticky="ew", pady=(8, 0))

        self.preview_widget = CameraPreview(
            self, self.app, on_camera_state=self._on_camera_state
        )
        self.preview_widget.grid(row=0, column=1, sticky="n")

    # -- 页签生命周期 ------------------------------------------------------

    def preview(self) -> CameraPreview:
        return self.preview_widget

    def on_show(self) -> None:
        self._on_camera_state(self.app.camera.state)
        self.threshold_var.set(f"判定阈值：{self.app.settings.match_threshold} 分")

    def _on_camera_state(self, state: str) -> None:
        """摄像头可用性变化时同步"抓拍"按钮。"""
        self.capture_btn.configure(state="normal" if state == "running" else "disabled")

    # -- 取图 --------------------------------------------------------------

    def _on_capture(self) -> None:
        frame = self.preview_widget.current_frame()
        if frame is None:
            self.app.show_warning(
                "当前没有可用画面。若摄像头不可用，请改用「选择文件」。", "无法抓拍"
            )
            return
        self.preview_widget.show_static(frame)
        self._set_image_state("已抓拍当前摄像头画面")

    def _on_choose_file(self) -> None:
        path = filedialog.askopenfilename(
            title="选择待识别图片", filetypes=IMAGE_FILETYPES, parent=self
        )
        if not path:
            return
        if not self.preview_widget.show_static_file(path):
            self.app.show_error(
                f"无法读取该图片文件，可能格式不受支持或文件已损坏：\n{Path(path).name}"
            )
            return
        self._set_image_state(f"已选择文件：{Path(path).name}")

    def _on_back_to_live(self) -> None:
        self.preview_widget.show_live()
        self._set_image_state("尚未采集图片")

    def _set_image_state(self, text: str) -> None:
        self.image_state.set(text)
        self.app.status(text)

    # -- 识别 --------------------------------------------------------------

    def _on_recognize(self) -> None:
        frame = self.preview_widget.current_frame()
        if frame is None:
            self.app.show_warning(
                "请先点击「抓拍当前画面」或「选择文件」提供一张待识别照片。", "缺少待识别图片"
            )
            return

        group_id = self.app.settings.group_id
        threshold = self.app.settings.match_threshold

        self.app.set_busy(self.recognize_btn, True, "识别中…")
        self._reset_result(show_placeholder=False)
        self.app.status("正在识别…")

        def work():
            return self.app.client.search(frame, group_id, threshold)

        def done(candidates: list[dict]) -> None:
            self.app.set_busy(self.recognize_btn, False)
            if not candidates:
                # 云端未返回任何候选：可能是无人脸，也可能是分数全部低于阈值
                self._show_stranger(threshold, best_score=None)
                return
            best = candidates[0]
            if best["score"] < threshold:
                self._show_stranger(threshold, best_score=best["score"])
            else:
                self._show_match(best, threshold)

        def failed(exc: BaseException) -> None:
            # 网络/配额等失败必须与"陌生人"区分开，否则会把故障误报成没认出人
            self.app.set_busy(self.recognize_btn, False)
            self._reset_result(show_placeholder=True)
            self.app.show_error(describe_exception(exc))

        self.app.run_in_background(work, done, failed)

    def _resolve_name(self, candidate: dict) -> str:
        """优先用云端 user_info；为空时回退到本地档案，再不行才显示 user_id。"""
        name = (candidate.get("user_info") or "").strip()
        if name:
            return name
        person = self.app.store.get_person(candidate.get("user_id", ""))
        if person is not None:
            return person.name
        return candidate.get("user_id", "未知")

    def _show_match(self, best: dict, threshold: int) -> None:
        name = self._resolve_name(best)
        self.result_label.configure(text=name, foreground=_COLOR_MATCH)
        self.detail_var.set(f"相似度 {best['score']:.1f} 分（阈值 {threshold} 分）")
        self.app.status(f"识别成功：{name} · 相似度 {best['score']:.1f} 分")

    def _show_stranger(self, threshold: int, best_score: float | None) -> None:
        # 陌生人场景绝不展示候选姓名
        if best_score is None:
            detail = f"人脸库中未找到匹配项（阈值 {threshold} 分）"
        else:
            detail = f"最高相似度仅 {best_score:.1f} 分，未达到阈值 {threshold} 分"
        self.result_label.configure(text=UNKNOWN_NAME, foreground=_COLOR_STRANGER)
        self.detail_var.set(detail)
        self.app.status(f"识别结果：{UNKNOWN_NAME} · {detail}")

    def _reset_result(self, show_placeholder: bool) -> None:
        self.result_label.configure(
            text="—" if show_placeholder else "识别中…", foreground=_COLOR_IDLE
        )
        self.detail_var.set("尚未识别" if show_placeholder else "正在检索云端人脸库…")
