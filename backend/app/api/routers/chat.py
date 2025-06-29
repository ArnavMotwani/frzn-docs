# backend/app/api/routers/chat.py

import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.agents.agent import graph

router = APIRouter()

@router.post("/chat")
async def chat(
    repoId: str,
    request: Request,
):
    payload = await request.json()
    messages = payload.get("messages", [])
    state = {
        "repo_id": repoId,
        "messages": messages,
    }

    def data_stream():
        for token, metadata in graph.stream(state, stream_mode="messages"):
            if metadata.get("langgraph_node") != "aggregate":
                continue

            text = getattr(token, "content", "") or ""
            if not text:
                continue
            yield f'0:{json.dumps(text)}\n'

        yield 'd:{"finishReason":"stop","usage":{}}\n'

    return StreamingResponse(
        data_stream(),
        media_type="text/plain; charset=utf-8",
    )