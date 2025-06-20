from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from sqlmodel import SQLModel, Session, select
from math import sqrt
from langchain_core.messages import BaseMessage
from app.models import File
from app.db import engine
from app.models import CodeChunk as CodeChunkModel

class State(TypedDict):
    repo_id: int
    messages: Annotated[List[BaseMessage], add_messages]
    embedding: List[float]
    context: str

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
llm = init_chat_model("openai:gpt-4.1", temperature=0.5, max_tokens=1000)

def extract_text_from_message(msg: BaseMessage) -> str:
    content = msg.content
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if part.get("type") == "text")
    if isinstance(content, str):
        return content
    return ""

def embed_node(state: State) -> dict[str, List[float]]:
    last_msg = state["messages"][-1]
    text = extract_text_from_message(last_msg)
    emb = embeddings_model.embed_query(text)
    return {"embedding": emb}

def fetch_context(state: State) -> dict[str, str]:
    emb = state["embedding"]
    with Session(engine) as sess:
        stmt = (
            select(CodeChunkModel)
            .join(CodeChunkModel.file)
            .where(File.repo_id == state["repo_id"])
        )
        chunks = sess.exec(stmt).all()

    texts = [c.content for c in chunks]
    embs = embeddings_model.embed_documents(texts)

    def cosine_similarity(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sqrt(sum(x * x for x in a))
        norm_b = sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0

    top_k = sorted(range(len(texts)), key=lambda i: cosine_similarity(emb, embs[i]), reverse=True)[:3]
    context = "\n".join(texts[i] for i in top_k)
    return {"context": context}

def chat_node(state: State) -> dict[str, List[BaseMessage]]:
    user_text = extract_text_from_message(state["messages"][-1])
    prompt = (
        "Here is some relevant code context:\n"
        f"{state['context']}\n\n"
        "Now answer the user question:\n"
        f"{user_text}"
    )
    ai_response = llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [ai_response]}

builder = StateGraph(State)
builder.add_node("embed", embed_node)
builder.add_node("fetch_context", fetch_context)
builder.add_node("chat", chat_node)
builder.add_edge(START, "embed")
builder.add_edge("embed", "fetch_context")
builder.add_edge("fetch_context", "chat")
builder.add_edge("chat", END)
graph = builder.compile()