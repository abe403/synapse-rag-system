FROM python:3.10-slim

WORKDIR /app

# Install faiss dependencies if needed
RUN apt-get update && apt-get install -y libomp-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for FastMCP over SSE (or a custom HTTP bridge)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5000"]
