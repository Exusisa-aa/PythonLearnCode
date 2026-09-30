"""人员注册页签：输入姓名 + 采集人脸 → 注册进百度云端人脸库并写入本地档案。"""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk

import numpy as np

from config import MAX_NAME_BYTES
from core.errors import describe_exception
from core.identity import derive_user_id
from core.images import save_bgr_image
from ui.base_tab import BaseTab
from ui.preview import CameraPreview

IMAGE_FILETYPES = [
    ("图片文件", "*.png *.jpg *.jpeg *.bmp"),
    ("所有文件", "*.*"),
]


class RegisterTab(BaseTab):
    def __init__(self, master: tk.Misc, app) -> None:
        super().__init__(master, app)
        self._build()

    # -- 构建界面 ----------------------------------------------------------

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        form = ttk.Frame(self)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        form.columnconfigure(0, weight=1)

        ttk.Label(form, text="人员注册", font=("", 14, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            form,
            text="输入姓名并采集一张人脸照片，即可将此人注册进百度云端人脸库。",
            foreground="#555555",
            wraplength=380,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(0, 16))

        ttk.Label(form, text="姓名（必填）").grid(row=2, column=0, sticky="w")
        self.name_var = tk.StringVar()
        entry = ttk.Entry(form, textvariable=self.name_var, font=("", 11))
        entry.grid(row=3, column=0, sticky="ew", pady=(4, 4), ipady=3)
        entry.bind("<Return>", lambda _e: self._on_register())

        ttk.Label(
            form,
            text="同名重复注册会为该人员追加一张人脸（同一人最多 20 张），可提升识别命中率。",
            foreground="#777777",
            wraplength=380,
            justify="left",
        ).grid(row=4, column=0, sticky="w", pady=(0, 16))

        ttk.Separator(form, orient="horizontal").grid(row=5, column=0, sticky="ew", pady=8)

        ttk.Label(form, text="人脸图片").grid(row=6, column=0, sticky="w", pady=(8, 6))

        buttons = ttk.Frame(form)
        buttons.grid(row=7, column=0, sticky="ew")
        buttons.columnconfigure((0, 1), weight=1)

        self.capture_btn = ttk.Button(buttons, text="抓拍当前画面", command=self._on_capture)
        self.capture_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4), ipady=3)

        self.file_btn = ttk.Button(buttons, text="选择文件…", command=self._on_choose_file)
        self.file_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0), ipady=3)

        self.live_btn = ttk.Button(form, text="返回实时画面", command=self._on_back_to_live)
        self.live_btn.grid(row=8, column=0, sticky="ew", pady=(6, 0))

        self.image_state = tk.StringVar(value="尚未采集图片")
        ttk.Label(form, textvariable=self.image_state, foreground="#777777").grid(
            row=9, column=0, sticky="w", pady=(8, 16)
        )

        self.register_btn = ttk.Button(form, text="注 册", command=self._on_register)
        self.register_btn._idle_text = "注 册"  # set_busy 依赖该属性还原文字
        self.register_btn.grid(row=10, column=0, sticky="ew", ipady=8)

        self.hint = ttk.Label(form, text="", foreground="#0a7d32", wraplength=380, justify="left")
        self.hint.grid(row=11, column=0, sticky="w", pady=(12, 0))

        self.preview_widget = CameraPreview(
            self, self.app, on_camera_state=self._on_camera_state
        )
        self.preview_widget.grid(row=0, column=1, sticky="n")

    # -- 页签生命周期 ------------------------------------------------------

    def preview(self) -> CameraPreview:
        return self.preview_widget

    def on_show(self) -> None:
        self._on_camera_state(self.app.camera.state)

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
            title="选择人脸图片", filetypes=IMAGE_FILETYPES, parent=self
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

    # -- 注册 --------------------------------------------------------------

    def _validate_name(self, name: str) -> str | None:
        """返回错误说明；通过则返回 None。校验全部在本地完成，不发请求。"""
        if not name:
            return "请输入姓名。"
        size = len(name.encode("utf-8"))
        if size > MAX_NAME_BYTES:
            return f"姓名过长（{size} 字节），请控制在 {MAX_NAME_BYTES} 字节以内。"
        return None

    def _on_register(self) -> None:
        name = self.name_var.get().strip()

        problem = self._validate_name(name)
        if problem:
            self.app.show_warning(problem, "姓名不合法")
            return

        frame = self.preview_widget.current_frame()
        if frame is None:
            self.app.show_warning(
                "请先点击「抓拍当前画面」或「选择文件」提供一张人脸照片。", "缺少人脸图片"
            )
            return

        user_id = derive_user_id(name)
        group_id = self.app.settings.group_id

        self.app.set_busy(self.register_btn, True, "注册中…")
        self.hint.configure(text="")
        self.app.status(f"正在注册「{name}」…")

        def work():
            # 网络调用 + 本地落盘 + 写库都放在工作线程，主线程只负责刷新界面
            face_token = self.app.client.add_user(
                frame,
                user_id,
                name,
                group_id,
                quality_control=self.app.settings.quality_control,
                liveness_control=self.app.settings.liveness_control,
            )
            photo_path = self._save_photo(frame, user_id)
            is_append = self.app.store.get_person(user_id) is not None
            person = self.app.store.upsert_person(
                user_id, name, group_id, face_token, photo_path
            )
            return person, is_append

        def done(result) -> None:
            person, is_append = result
            self.app.set_busy(self.register_btn, False)
            action = "已追加一张人脸到" if is_append else "已注册"
            message = f"{action}「{person.name}」"
            self.hint.configure(text=f"✓ {message}")
            self.app.status(f"{message} · 人脸库共 {self.app.store.count_persons()} 人")
            self._reset_capture()
            self.app.show_info(
                f"{message}。\n\n"
                f"人脸库当前共 {self.app.store.count_persons()} 人。\n"
                "注册结果约 5 秒后在百度侧生效。",
                "注册成功",
            )

        def failed(exc: BaseException) -> None:
            self.app.set_busy(self.register_btn, False)
            self.hint.configure(text="")
            self.app.show_error(describe_exception(exc))

        self.app.run_in_background(work, done, failed)

    def _save_photo(self, frame: np.ndarray, user_id: str) -> str | None:
        """把注册照片落盘，便于人脸库管理页回显。失败不影响注册结果。

        经 core.images 写入而非 `cv2.imwrite`：后者在 Windows 上写不了含中文的路径，
        且是静默失败。
        """
        directory: Path = self.app.settings.photo_dir
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        path = directory / f"{user_id}_{stamp}.jpg"
        return str(path) if save_bgr_image(frame, path) else None

    def _reset_capture(self) -> None:
        self.preview_widget.show_live()
        self.image_state.set("尚未采集图片")
