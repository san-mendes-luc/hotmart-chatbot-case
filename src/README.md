# Hotmart Chatbot

A modern chatbot application built with FastAPI, ChromaDB, and Arize Phoenix for monitoring.

## Features

- FastAPI-based REST API for chat interactions
- RAG (Retrieval Augmented Generation) using ChromaDB
- Monitoring and observability with Arize Phoenix
- Containerized deployment with Docker
- Fast package management with uv

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   └── retrieval.py
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── phoenix_client.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_rag.py
│   └── test_monitoring.py
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── pyproject.toml
```

## Setup and Installation

1. Install uv:
```bash
pip install uv
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Run with Docker:
```bash
docker-compose up --build
```

## Development

- API runs on http://localhost:8000
- API documentation available at http://localhost:8000/docs
- Monitoring dashboard available at http://localhost:8000/monitoring

## License

MIT