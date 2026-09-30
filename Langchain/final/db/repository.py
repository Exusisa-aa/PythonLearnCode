from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Message, Session


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self) -> Session:
        session = Session()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def list(self) -> list[Session]:
        result = await self.db.execute(
            select(Session).order_by(Session.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, session_id: str) -> Session | None:
        return await self.db.get(Session, session_id)

    async def delete(self, session_id: str) -> bool:
        session = await self.get(session_id)
        if session is None:
            return False
        await self.db.delete(session)
        await self.db.commit()
        return True


class MessageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add(self, session_id: str, role: str, content: str) -> Message:
        message = Message(session_id=session_id, role=role, content=content)
        self.db.add(message)
        session = await self.db.get(Session, session_id)
        if session is not None:
            session.updated_at = func.now()
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def history(self, session_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
        )
        return list(result.scalars().all())
