FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install basic build tools + curl for uv install
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# App layout inside container:
# /app           <- agents_dir for ADK
# /app/Youtube_Agent <- your project + pyproject.toml
WORKDIR /app

# Copy project into /app/Youtube_Agent
COPY . /app/Youtube_Agent

WORKDIR /app/Youtube_Agent

# Install dependencies from pyproject.toml / uv.lock
RUN uv sync --frozen --no-dev

# ADK Web runs on 8000 by default
EXPOSE 8000

# Run ADK Web:
#   agents_dir  = /app
#   project env = current dir (/app/Youtube_Agent)
CMD ["uv", "run", "adk", "web", "--host", "0.0.0.0", ".."]

