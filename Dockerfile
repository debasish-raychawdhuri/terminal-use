FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    vim \
    htop \
    less \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Expose the port
EXPOSE 8000

# Run the server
CMD ["terminal-mcp-server", "--host", "0.0.0.0"]
