"""
Agent graph definitions for frzn-docs, using LangGraph and OpenAI.
Handles summarization, metadata retrieval, context fetching,
iterative research loops, and final aggregation for a given repo.
"""

from typing import TypedDict, Optional, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from sqlmodel import Session, select
from math import sqrt
from langchain_core.messages import BaseMessage
from app.models import File, CodeChunk as CodeChunkModel
from app.db import engine

# -----------------------------------------------------------------------------
# State definition
# -----------------------------------------------------------------------------
class State(TypedDict):
    """
    The global state passed between LangGraph nodes.
    Fields:
        - repo_id: GitHub repo identifier
        - messages: Conversation history for the LLM
        - embedding: Current question embedding
        - context: Retrieved code snippets for relevance
        - summary: High-level repo overview
        - metadata: File path list in the repo
        - research_logic/file/arch: Outputs from each research scope
    """
    repo_id: int
    messages: Annotated[List[BaseMessage], add_messages]
    embedding: List[float]
    context: Optional[str]
    summary: Optional[str]
    metadata: Optional[List[str]]
    research_logic: Optional[str]
    research_file: Optional[str]
    research_arch: Optional[str]

# -----------------------------------------------------------------------------
# Model initialization
# -----------------------------------------------------------------------------
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
llm = init_chat_model("openai:gpt-4.1", temperature=0.5, max_tokens=1000)

# -----------------------------------------------------------------------------
# Utility function
# -----------------------------------------------------------------------------
def extract_text_from_message(msg: BaseMessage) -> str:
    """
    Pulls raw text out of a BaseMessage, whether it's a string or list of parts.
    """
    content = msg.content
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if part.get("type") == "text")
    if isinstance(content, str):
        return content
    return ""  # Fallback if content is unexpected

# -----------------------------------------------------------------------------
# Summarization section
# -----------------------------------------------------------------------------
def summarize_repo_node(state: State) -> Dict[str, Any]:
    """
    Generates a 2–3 paragraph overview of the repo using the top 10 code chunks.
    """
    with Session(engine) as sess:
        stmt = (
            select(CodeChunkModel)
            .join(CodeChunkModel.file)           # Ensure chunks belong to this repo
            .where(File.repo_id == state["repo_id"])
            .limit(10)
        )
        chunks = sess.exec(stmt).all()
    snippet = "\n".join(c.content for c in chunks)
    prompt = "Provide a concise 2–3 paragraph overview of this codebase:\n" + snippet
    resp = llm.invoke([{"role": "user", "content": prompt}])
    return {"summary": extract_text_from_message(resp)}

# -----------------------------------------------------------------------------
# Metadata retrieval section
# -----------------------------------------------------------------------------
def fetch_metadata_node(state: State) -> Dict[str, Any]:
    """
    Retrieves file paths in the repo for reference in final output.
    """
    with Session(engine) as sess:
        stmt = select(File).where(File.repo_id == state["repo_id"])
        files = sess.exec(stmt).all()
    paths = [f.path for f in files]
    return {"metadata": paths}

# -----------------------------------------------------------------------------
# Embedding section
# -----------------------------------------------------------------------------
def embed_node(state: State) -> Dict[str, Any]:
    """
    Embeds the user’s latest question to drive similarity search.
    """
    last_msg = state["messages"][-1]
    text = extract_text_from_message(last_msg)
    emb = embeddings_model.embed_query(text)
    return {"embedding": emb}

# -----------------------------------------------------------------------------
# Context fetching section
# -----------------------------------------------------------------------------
def fetch_context_node(state: State) -> Dict[str, Any]:
    """
    Retrieves and ranks code chunks by similarity, storing the top 3 in context.
    """
    with Session(engine) as sess:
        stmt = (
            select(CodeChunkModel)
            .join(CodeChunkModel.file)
            .where(File.repo_id == state["repo_id"])
        )
        chunks = sess.exec(stmt).all()

    texts = [c.content for c in chunks]
    embs = embeddings_model.embed_documents(texts)

    def cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = sqrt(sum(x * x for x in a))
        nb = sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0

    # Pick top 3 most similar chunks
    top_idx = sorted(
        range(len(texts)),
        key=lambda i: cosine(state["embedding"], embs[i]),
        reverse=True
    )[:3]

    return {"context": "\n".join(texts[i] for i in top_idx)}

# -----------------------------------------------------------------------------
# Research loops section
# -----------------------------------------------------------------------------
def research_loop(state: State, scope: str) -> Dict[str, Any]:
    """
    Runs up to two iterations of prompting on precomputed context,
    refining until the output stabilizes.
    """
    context = state.get("context", "") or ""
    answer = ""
    for _ in range(2):
        prompt = (
            f"Research in the {scope} scope.\n"
            f"Context:\n{context}\n"
            f"Question:\n{extract_text_from_message(state['messages'][-1])}"
        )
        resp = llm.invoke([{"role": "user", "content": prompt}])
        text_resp = extract_text_from_message(resp)
        if text_resp.strip() == answer.strip():
            break  # Stop if no change
        answer = text_resp
        context += "\n" + answer    # Expand context with new insight
    return {f"research_{scope}": answer}

# -----------------------------------------------------------------------------
# Aggregation section
# -----------------------------------------------------------------------------
def aggregate_node(state: State) -> Dict[str, List[BaseMessage]]:
    """
    Combines summary, metadata, and all research insights into one final answer.
    """
    user_q = extract_text_from_message(state["messages"][-1])
    parts: List[str] = []

    if state.get("summary"):
        parts.append("Overview:\n" + state["summary"])
    if state.get("metadata"):
        parts.append("Files:\n" + ", ".join(state["metadata"][:10]) + " ...")

    for scope in ("logic", "file", "arch"):
        key = f"research_{scope}"
        if state.get(key):
            parts.append(f"{scope.capitalize()} Research:\n{state[key]}")

    parts.append(f"Answer to '{user_q}':")
    combined = "\n\n".join(parts)
    resp = llm.invoke([{"role": "user", "content": combined}])
    return {"messages": [resp]}

# -----------------------------------------------------------------------------
# Graph construction section
# -----------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("summarize_repo", summarize_repo_node)
builder.add_node("fetch_metadata", fetch_metadata_node)
builder.add_node("embed", embed_node)
builder.add_node("fetch_context", fetch_context_node)
builder.add_node("research_logic_node", lambda s: research_loop(s, "logic"))
builder.add_node("research_file_node", lambda s: research_loop(s, "file"))
builder.add_node("research_arch_node", lambda s: research_loop(s, "arch"))
builder.add_node("aggregate", aggregate_node)

builder.add_edge(START, "summarize_repo")
builder.add_edge(START, "fetch_metadata")
builder.add_edge("summarize_repo", "embed")
builder.add_edge("fetch_metadata", "embed")
builder.add_edge("embed", "fetch_context")
builder.add_edge("fetch_context", "research_logic_node")
builder.add_edge("fetch_context", "research_file_node")
builder.add_edge("fetch_context", "research_arch_node")
builder.add_edge("research_logic_node", "aggregate")
builder.add_edge("research_file_node", "aggregate")
builder.add_edge("research_arch_node", "aggregate")
builder.add_edge("aggregate", END)

graph = builder.compile()