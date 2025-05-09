FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MCP_SERVER_PORT=8001
ENV DATA_DIR=/data

# Expose MCP server port
EXPOSE 8001

# Run the server
CMD ["python", "server.py"] 