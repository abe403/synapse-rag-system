# Synapse - Context-Aware Enterprise AI

Synapse is a production-ready, context-aware Retrieval-Augmented Generation (RAG) system. It is designed for high-performance enterprise document search with sub-200ms latency.

## Architecture

The system is built as a microservices-oriented architecture:

- **Frontend**: React + TypeScript SPA with real-time SSE streaming.
- **API Gateway**: FastAPI orchestrator managing Gemini API and MCP tool calls.
- **Retrieval Engine**: PyTorch-based document embedder with FAISS vector search.

## Tech Stack

- **AI**: Gemini API, PyTorch, FAISS, Model Context Protocol (MCP).
- **Backend**: FastAPI, Uvicorn, Python 3.10.
- **Frontend**: React, TypeScript, Vite, Tailwind-style CSS.
- **Orchestration**: Docker, Docker Compose.

## Getting Started

1. Set your Gemini API key in a `.env` file:
   ```env
   GEMINI_API_KEY=your_key_here
   ```
2. Start the services:
   ```bash
   docker-compose up --build
   ```
