from fastapi import APIRouter, Depends, HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from final.agent.graph import agent_graph, stream_model
from final.db.models import Message
from final.db.repository import MessageRepository, SessionRepository
from final.db.session import get_session

from .schemas import ChatResponse, MessageIn, MessageOut, SessionOut

router = APIRouter()


def _to_langchain_messages(history: list[Message]) -> list:
    converted = []
    for message in history:
        if message.role == "assistant":
            converted.append(AIMessage(content=message.content))
        else:
            converted.append(HumanMessage(content=message.content))
    return converted


@router.post(
    "/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED
)
async def create_session(db: AsyncSession = Depends(get_session)):
    return await SessionRepository(db).create()


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions(db: AsyncSession = Depends(get_session)):
    return await SessionRepository(db).list()


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_session)):
    if not await SessionRepository(db).delete(session_id):
        raise HTTPException(status_code=404, detail="Session not found")


@router.get(
    "/sessions/{session_id}/messages", response_model=list[MessageOut]
)
async def get_history(session_id: str, db: AsyncSession = Depends(get_session)):
    session_repo = SessionRepository(db)
    if await session_repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return await MessageRepository(db).history(session_id)


@router.post(
    "/sessions/{session_id}/messages", response_model=ChatResponse
)
async def send_message(
    session_id: str, payload: MessageIn, db: AsyncSession = Depends(get_session)
):
    session_repo = SessionRepository(db)
    if await session_repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")

    content = payload.content.strip()
    if not content:
        raise HTTPException(
            status_code=422, detail="Message content must not be empty"
        )

    message_repo = MessageRepository(db)
    await message_repo.add(session_id, "user", content)

    history = await message_repo.history(session_id)
    context_messages = _to_langchain_messages(history)

    result = agent_graph.invoke({"messages": context_messages})
    new_messages = result["messages"][len(context_messages):]
    assistant_content = new_messages[-1].content if new_messages else ""

    assistant = await message_repo.add(session_id, "assistant", assistant_content)

    messages = await message_repo.history(session_id)
    return ChatResponse(
        session_id=session_id,
        assistant=MessageOut.model_validate(assistant),
        messages=[MessageOut.model_validate(m) for m in messages],
    )


@router.post("/sessions/{session_id}/messages/stream")
async def send_message_stream(
    session_id: str, payload: MessageIn, db: AsyncSession = Depends(get_session)
):
    session_repo = SessionRepository(db)
    if await session_repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")

    content = payload.content.strip()
    if not content:
        raise HTTPException(
            status_code=422, detail="Message content must not be empty"
        )

    message_repo = MessageRepository(db)
    await message_repo.add(session_id, "user", content)

    history = await message_repo.history(session_id)
    context_messages = _to_langchain_messages(history)

    async def event_generator():
        parts = []
        try:
            for token in stream_model(context_messages):
                parts.append(token)
                yield {"event": "token", "data": token}
            yield {"event": "done", "data": ""}
        finally:
            full_text = "".join(parts)
            if full_text:
                await message_repo.add(session_id, "assistant", full_text)

    return EventSourceResponse(event_generator())
