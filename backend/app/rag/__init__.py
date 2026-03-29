"""
RAG (Retrieval-Augmented Generation) engine for 智农兴乡.

Module layout
─────────────
embeddings.py   — embedding function factory (chromadb EF protocol)
vector_store.py — ChromaDB wrapper (CRUD + semantic search)
retriever.py    — hybrid retriever: semantic search ∪ BM25 re-rank
llm.py          — thin LLM wrapper (OpenAI or no-key fallback)
chain.py        — full RAG pipeline (retrieve → prompt → generate)
"""
