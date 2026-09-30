"""本地人员档案数据库。

本地库只保存"档案"（姓名、user_id、group_id、face_token、照片路径、时间戳），
不保存人脸特征——特征在百度云端，比对由云端完成。详见 design.md 决策 1。

每个操作独立开连接，避免 SQLite 连接跨线程复用的问题：界面会在工作线程里读写本库。
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS persons (
    user_id    TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    group_id   TEXT NOT NULL,
    face_token TEXT,
    photo_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""

_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class Person:
    user_id: str
    name: str
    group_id: str
    face_token: str | None
    photo_path: str | None
    created_at: str
    updated_at: str

    @classmethod
    def _from_row(cls, row: sqlite3.Row) -> "Person":
        return cls(
            user_id=row["user_id"],
            name=row["name"],
            group_id=row["group_id"],
            face_token=row["face_token"],
            photo_path=row["photo_path"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


def _now() -> str:
    return datetime.now().strftime(_TIME_FORMAT)


class PersonStore:
    """人员档案的增删改查。所有方法均可在工作线程中调用。"""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def upsert_person(
        self,
        user_id: str,
        name: str,
        group_id: str,
        face_token: str | None,
        photo_path: str | None,
    ) -> Person:
        """按 user_id 存在则更新、不存在则插入。

        同名重复注册时 user_id 相同（见 design.md 决策 2），因此会走到更新分支，
        不会产生第二条档案。
        """
        now = _now()
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT created_at FROM persons WHERE user_id = ?", (user_id,)
            ).fetchone()
            if existing is None:
                conn.execute(
                    "INSERT INTO persons "
                    "(user_id, name, group_id, face_token, photo_path, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, name, group_id, face_token, photo_path, now, now),
                )
            else:
                conn.execute(
                    "UPDATE persons SET name = ?, group_id = ?, face_token = ?, "
                    "photo_path = ?, updated_at = ? WHERE user_id = ?",
                    (name, group_id, face_token, photo_path, now, user_id),
                )
        person = self.get_person(user_id)
        assert person is not None  # 刚写入，必然存在
        return person

    def list_persons(self) -> list[Person]:
        """按注册时间顺序返回全部档案。"""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM persons ORDER BY created_at ASC, name ASC"
            ).fetchall()
        return [Person._from_row(row) for row in rows]

    def get_person(self, user_id: str) -> Person | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM persons WHERE user_id = ?", (user_id,)
            ).fetchone()
        return Person._from_row(row) if row else None

    def get_person_by_name(self, name: str) -> Person | None:
        """按姓名精确查找，用于判断是否为同名重复注册。"""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM persons WHERE name = ? ORDER BY created_at ASC LIMIT 1",
                (name,),
            ).fetchone()
        return Person._from_row(row) if row else None

    def delete_person(self, user_id: str) -> bool:
        """返回是否确实删掉了一条记录。"""
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM persons WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0

    def count_persons(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM persons").fetchone()
        return int(row["n"])


def _self_test() -> None:
    """直接运行本文件时的自测入口：不依赖网络与百度接口。"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        store = PersonStore(Path(tmp) / "test.db")
        assert store.count_persons() == 0, "新建库应为空"
        assert store.list_persons() == [], "新建库列表应为空"
        assert store.get_person("nope") is None, "不存在的 user_id 应返回 None"

        a = store.upsert_person("u_a", "张三", "g1", "tok_a", "data/faces/a.jpg")
        assert a.created_at == a.updated_at, "首次插入两个时间戳应一致"
        assert store.count_persons() == 1

        # 同名重复注册：同一个 user_id 应走更新分支，不新增记录
        a2 = store.upsert_person("u_a", "张三", "g1", "tok_a2", "data/faces/a2.jpg")
        assert store.count_persons() == 1, "重复注册不应新增档案"
        assert a2.face_token == "tok_a2", "face_token 应被刷新"
        assert a2.created_at == a.created_at, "created_at 应保持不变"
        assert a2.updated_at >= a.updated_at, "updated_at 应被刷新"
        assert a2.photo_path == "data/faces/a2.jpg", "照片路径应被刷新"

        store.upsert_person("u_b", "李四", "g1", "tok_b", None)
        store.upsert_person("u_c", "王五", "g2", "tok_c", None)
        assert store.count_persons() == 3
        assert [p.name for p in store.list_persons()] == ["张三", "李四", "王五"], "应按注册时间排序"

        assert store.get_person_by_name("李四") is not None
        assert store.get_person_by_name("不存在") is None

        assert store.delete_person("u_b") is True
        assert store.delete_person("u_b") is False, "重复删除应返回 False"
        assert store.count_persons() == 2
        assert [p.name for p in store.list_persons()] == ["张三", "王五"]

    print("database.py 自测通过：建表 / upsert / 列表 / 查询 / 删除 / 计数 全部正常")


if __name__ == "__main__":
    _self_test()
