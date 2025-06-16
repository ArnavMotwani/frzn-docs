# backend/app/api/routers/chat.py

import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.agents.agent import graph

router = APIRouter()

@router.post("/chat")
async def chat(request: Request):
    body = await request.json()

    if isinstance(body, dict) and body.get("messages"):
        last = body["messages"][-1]
        content = last.get("content", "")
        if isinstance(content, list):
            user_text = "".join(part.get("text", "") for part in content)
        else:
            user_text = content or ""
    elif isinstance(body, str):
        user_text = body
    else:
        user_text = body.get("text", "")

    state = {"messages": [{"role": "user", "content": user_text}]}

    def data_stream():
        for token, _ in graph.stream(state, stream_mode="messages"):
            text = getattr(token, "content", "") or ""
            if not text:
                continue
            yield f'0:{json.dumps(text)}\n'

        yield 'd:{"finishReason":"stop","usage":{}}\n'

    return StreamingResponse(
        data_stream(),
        media_type="text/plain; charset=utf-8",
    )