"""人脸库管理页签：查看已注册人员、查看明细、删除人员。

删除语义（见 design.md 决策 8）：以云端为权威。云端删除成功才清理本地档案；
云端失败则保留本地记录并报错，避免出现"本地以为删了、云端还在"的假象。
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from core.database import Person
from core.errors import describe_exception
from ui.base_tab import BaseTab

THUMBNAIL_BOX = (180, 180)

_EMPTY_HINT = "暂无注册人员。请到「人员注册」页添加第一位人员。"
_NO_PHOTO_HINT = "（该人员的注册照片已丢失）"


class FacesetTab(BaseTab):
    def __init__(self, master: tk.Misc, app) -> None:
        super().__init__(master, app)
        self._persons: dict[str, Person] = {}
        self._thumbnail: ImageTk.PhotoImage | None = None
        # 每次选中自增，用于丢弃过期的人脸数量查询结果
        self._detail_token = 0
        self._build()

    # -- 构建界面 ----------------------------------------------------------

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="人脸库管理", font=("", 14, "bold")).grid(row=0, column=0, sticky="w")

        self.count_var = tk.StringVar(value="共 0 人")
        ttk.Label(header, textvariable=self.count_var, foreground="#555555").grid(
            row=0, column=1, sticky="e", padx=(0, 10)
        )

        self.refresh_btn = ttk.Button(header, text="刷 新", command=self.refresh)
        self.refresh_btn.grid(row=0, column=2, sticky="e")

        list_box = ttk.Frame(self)
        list_box.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        list_box.columnconfigure(0, weight=1)
        list_box.rowconfigure(0, weight=1)

        columns = ("name", "created")
        self.tree = ttk.Treeview(list_box, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="姓名")
        self.tree.heading("created", text="注册时间")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("created", width=170, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        scrollbar = ttk.Scrollbar(list_box, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.empty_label = ttk.Label(list_box, text=_EMPTY_HINT, foreground="#888888")
        self.empty_label.grid(row=1, column=0, sticky="w", pady=(8, 0))

        detail = ttk.LabelFrame(self, text="人员明细", padding=12)
        detail.grid(row=1, column=1, sticky="n")

        self.detail_name = tk.StringVar(value="—")
        self.detail_uid = tk.StringVar(value="—")
        self.detail_faces = tk.StringVar(value="云端人脸数量：—")

        ttk.Label(detail, text="姓名", foreground="#888888").grid(row=0, column=0, sticky="w")
        ttk.Label(detail, textvariable=self.detail_name, font=("", 11, "bold")).grid(
            row=1, column=0, sticky="w", pady=(0, 8)
        )

        ttk.Label(detail, text="user_id", foreground="#888888").grid(row=2, column=0, sticky="w")
        ttk.Label(detail, textvariable=self.detail_uid).grid(
            row=3, column=0, sticky="w", pady=(0, 8)
        )

        ttk.Label(detail, textvariable=self.detail_faces).grid(
            row=4, column=0, sticky="w", pady=(0, 10)
        )

        self.photo_label = ttk.Label(
            detail,
            text="（未选中人员）",
            foreground="#888888",
            anchor="center",
            justify="center",
            width=24,
            background="#f0f0f0",
        )
        self.photo_label.grid(row=5, column=0, sticky="ew", ipady=40, pady=(0, 12))

        self.delete_btn = ttk.Button(detail, text="删除该人员", command=self._on_delete)
        self.delete_btn._idle_text = "删除该人员"
        self.delete_btn.grid(row=6, column=0, sticky="ew", ipady=5)

        ttk.Label(
            detail,
            text="删除会同时移除云端人脸库中的人员，且不可撤销。",
            foreground="#999999",
            wraplength=200,
            justify="left",
        ).grid(row=7, column=0, sticky="w", pady=(8, 0))

    # -- 页签生命周期 ------------------------------------------------------

    def on_show(self) -> None:
        self.refresh()

    # -- 列表 --------------------------------------------------------------

    def refresh(self) -> None:
        """列表数据源是本地档案，不逐条查询云端，以免触发配额限制。"""
        self._persons = {person.user_id: person for person in self.app.store.list_persons()}

        selected = self._selected_user_id()
        self.tree.delete(*self.tree.get_children())
        for person in self._persons.values():
            self.tree.insert("", "end", iid=person.user_id, values=(person.name, person.created_at))

        count = len(self._persons)
        self.count_var.set(f"共 {count} 人")
        if count:
            self.empty_label.grid_remove()
        else:
            self.empty_label.grid()
            self._clear_detail()

        # 尽量保持原本的选中项
        if selected and selected in self._persons:
            self.tree.selection_set(selected)

    def _selected_user_id(self) -> str | None:
        selection = self.tree.selection()
        return selection[0] if selection else None

    # -- 明细 --------------------------------------------------------------

    def _on_select(self, _event: object = None) -> None:
        user_id = self._selected_user_id()
        if user_id is None or user_id not in self._persons:
            self._clear_detail()
            return

        person = self._persons[user_id]
        self._detail_token += 1
        token = self._detail_token

        self.detail_name.set(person.name)
        self.detail_uid.set(person.user_id)
        self.detail_faces.set("云端人脸数量：查询中…")
        self._show_photo(person)

        def work():
            return self.app.client.get_face_list(person.user_id, person.group_id)

        def done(faces: list[dict]) -> None:
            if token != self._detail_token:
                return  # 期间用户已切换到别的人员，丢弃过期结果
            self.detail_faces.set(f"云端人脸数量：{len(faces)} 张")

        def failed(exc: BaseException) -> None:
            if token != self._detail_token:
                return
            # 明细查询失败只影响明细区，列表与其他人员仍可正常浏览
            self.detail_faces.set(f"人脸数量查询失败：{describe_exception(exc)}")

        self.app.run_in_background(work, done, failed)

    def _show_photo(self, person: Person) -> None:
        path = person.photo_path
        if path and Path(path).exists():
            try:
                image = Image.open(path)
                image.thumbnail(THUMBNAIL_BOX, Image.LANCZOS)
                self._thumbnail = ImageTk.PhotoImage(image)
                self.photo_label.configure(image=self._thumbnail, text="")
                return
            except Exception:
                pass  # 落到下面的占位提示

        self._thumbnail = None
        self.photo_label.configure(image="", text=_NO_PHOTO_HINT)

    def _clear_detail(self) -> None:
        self._detail_token += 1
        self.detail_name.set("—")
        self.detail_uid.set("—")
        self.detail_faces.set("云端人脸数量：—")
        self._thumbnail = None
        self.photo_label.configure(image="", text="（未选中人员）")

    # -- 删除 --------------------------------------------------------------

    def _on_delete(self) -> None:
        user_id = self._selected_user_id()
        if user_id is None or user_id not in self._persons:
            self.app.show_warning("请先在左侧列表中选择一位人员。", "未选中人员")
            return

        person = self._persons[user_id]
        confirmed = messagebox.askyesno(
            "确认删除",
            f"确定要删除「{person.name}」吗？\n\n"
            "该操作会同时删除云端人脸库中的人员，且不可撤销。",
            parent=self,
            icon="warning",
        )
        if not confirmed:
            return

        self.app.set_busy(self.delete_btn, True, "删除中…")
        self.app.status(f"正在删除「{person.name}」…")

        def work():
            # 先删云端；云端抛错则本地档案原样保留
            result = self.app.client.delete_user(person.user_id, person.group_id)
            self.app.store.delete_person(person.user_id)
            self._remove_photo(person.photo_path)
            return result

        def done(result) -> None:
            self.app.set_busy(self.delete_btn, False)
            self._clear_detail()
            self.refresh()
            if result.removed:
                message = f"已删除「{person.name}」"
            else:
                message = f"云端本就不存在「{person.name}」，已清理本地记录"
            self.app.status(f"{message} · 人脸库共 {self.app.store.count_persons()} 人")
            self.app.show_info(
                f"{message}。\n\n"
                # 实测：删除接口返回成功后，检索索引仍可能短暂命中该人员。
                # 官方文档也说明删除"可能存在一定延迟"，因此这里明确告知使用者。
                "注意：百度侧的检索索引同步可能有几秒延迟，"
                "若立即识别仍能匹配到该人员，请稍等片刻再试。",
                "删除完成",
            )

        def failed(exc: BaseException) -> None:
            # 云端删除失败：本地档案保留，提示用户重试
            self.app.set_busy(self.delete_btn, False)
            self.app.show_error(
                f"{describe_exception(exc)}\n\n"
                f"「{person.name}」的本地记录已保留，可在网络恢复后重试删除。"
            )

        self.app.run_in_background(work, done, failed)

    @staticmethod
    def _remove_photo(path: str | None) -> None:
        if not path:
            return
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass
