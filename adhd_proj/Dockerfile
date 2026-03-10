FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
# python3-dev is required for psycopg2 error
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \ 
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install uv

# Copy only requirements to cache them in docker layer
COPY pyproject.toml uv.lock ./

# Install project dependencies
RUN uv sync --frozen --no-dev

# Copy the rest of the code
COPY . /app

# Expose the API port
EXPOSE 8000

# Start the application using uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
