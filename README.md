# frzn-docs

**frzn-docs** is an AI-powered documentation assistant that turns any public GitHub repository into a conversational knowledge base. Clone, index and embed your code, then ask natural-language questions and get context-aware answers powered by a LangGraph agent and OpenAI’s embeddings & chat models.

## What it does

1. **Repo indexing**  
   - Shallow-clones your GitHub repo  
   - Walks the file tree, filters by extension/pattern  
   - Splits each file into fixed-size chunks  
   - Generates embeddings in batches and stores everything in PostgreSQL (with pgvector)

2. **Vector retrieval**  
   - On each user query, embeds just the latest prompt  
   - Runs a cosine-similarity search over your code chunks  
   - Gathers the top-K most relevant snippets as grounding context

3. **LangGraph agent orchestration**  
   - Builds a lightweight state graph with explicit “tool” nodes for embedding, retrieval and LLM calls  
   - Pipes messages + retrieved code into GPT-4 as a system prompt  
   - Streams back LLM responses in real time

4. **Advanced multi-stage research pipeline**  
   - **Repo summary**: Automatically generates a concise 2–3 paragraph overview of your entire codebase  
   - **Context fetch**: Retrieves and ranks the top-3 most relevant code snippets for any query  
   - **Focused research loops**: Runs three parallel expert “mini-agents” (logic-level, file-level, architecture-level) that iteratively refine their insights until they converge  
   - **Final aggregation**: Combines summary, metadata, and each loop’s findings into one coherent, context-rich answer

5. **Full-stack chat UI**  
   - **Backend:** FastAPI + SQLModel + Alembic migrations, background indexing  
   - **Frontend:** Next.js + Tailwind + [assistant-ui](https://www.assistant-ui.com/) primitives for a polished, accessible chat experience  
   - **Dockerized:** Launch Postgres, backend and frontend with one command

## Why use frzn-docs?

- **Instant knowledge on your code:** No more hunting through files, just ask.  
- **Fully self-hosted:** Keep your data in your own infrastructure.  
- **Modular & extensible:** Swap out embedding models, adjust chunk sizes, or add custom LangGraph nodes.  
- **Streamed responses:** Users get answers token-by-token as they’re generated.

## 🚀 Getting Started

### Clone the repo 
   ```
   git clone https://github.com/YourOrg/frzn-docs.git
   cd frzn-docs
   ```

### Environment Variables

Create a `.env` file in the root of your project (or copy from `.env.example`) and populate it with the following settings:

```dotenv
# PostgreSQL configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=your_database_name_here

# SQLModel / SQLAlchemy connection URL
DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# LangChain settings
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_CALLBACKS_BACKGROUND=true
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=your_project_name_here
```

### Running the app (Docker Compose)

> **Note:** Make sure your Docker daemon is running before starting the services.

Run `docker-compose up --build` to start the full stack:

- **db** (PostgreSQL + pgvector)  
  - Port: `5432`  
  - Persists data in the `db-data` volume

- **backend** (FastAPI)  
  - Built from `backend/Dockerfile`  
  - Reads `.env` for `DATABASE_URL`, `OPENAI_API_KEY`, etc.  
  - Port: `8000`  
  - Live‐reloads code from `backend/app` and `backend/alembic`

- **frontend** (Next.js + Assistant-UI)  
  - Built from `frontend/Dockerfile`  
  - Uses `BACKEND_URL=http://backend:8000`  
  - Port: `3000`  
  - Hot‐reloads code from the `frontend` directory

After bringing up the services, visit:

- Frontend: <http://localhost:3000>  
- Backend API docs: <http://localhost:8000/docs>

> **Note:** Add -d to run in detached mode (so you get your terminal back): `docker-compose up --build -d`

## License 

Distributed under the **MIT** License. See **LICENSE** for more information.