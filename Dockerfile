# Use lightweight Python base image
FROM python:3.11-slim

# Avoid Python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy dependencies (adjust if using requirements.txt or pyproject.toml)
COPY . .

ENV DOTENV_PATH=/app/.env

# Install Python dependencies
RUN pip install uv && uv pip install --system .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI (adjust module path as needed)
CMD ["uvicorn", "src.chat_agents.agent:app", "--host", "0.0.0.0", "--port", "8000"]
