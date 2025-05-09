"""
File Manager MCP Server
=======================
Provides file system operations through MCP protocol.
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import pika
import prometheus_client
import uvicorn
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("file-mcp-server")

# Create FastAPI app
app = FastAPI(
    title="File Manager MCP Server",
    description="MCP server for file operations",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get configuration from environment variables
DATA_DIR = os.environ.get("DATA_DIR", "/data")
MCP_SERVER_PORT = int(os.environ.get("MCP_SERVER_PORT", 8001))
AMQP_URL = os.environ.get("AMQP_URL", "amqp://mcp:mcp@a2a-broker:5672/")
SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "file-manager")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Setup Prometheus metrics
REQUEST_COUNT = Counter(
    "file_mcp_requests_total", "Total number of requests", ["tool", "status"]
)
REQUEST_LATENCY = Histogram(
    "file_mcp_request_latency_seconds", "Request latency in seconds", ["tool"]
)
FILE_COUNT = Gauge("file_mcp_files_total", "Total number of files managed")
DIRECTORY_COUNT = Gauge(
    "file_mcp_directories_total", "Total number of directories managed"
)
TOTAL_BYTES = Gauge("file_mcp_total_bytes", "Total bytes stored")


# === MCP Models ===


class ListToolsRequest(BaseModel):
    pass


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict


class ListToolsResponse(BaseModel):
    tools: List[ToolDefinition]


class CallToolRequest(BaseModel):
    name: str
    arguments: Dict
    correlation_id: Optional[str] = None
    stream: Optional[bool] = False


class CallToolResponseItem(BaseModel):
    type: str
    content: Optional[Union[str, Dict, List]] = None
    format: Optional[str] = None


class ProgressEvent(BaseModel):
    type: str = "progress"
    message: str
    percentage: Optional[float] = None


# === File Operation Models ===


class CreateFileRequest(BaseModel):
    path: str = Field(
        ..., description="Path where to create the file (relative to data directory)"
    )
    content: str = Field(..., description="Content to write to the file")
    overwrite: bool = Field(
        False, description="Whether to overwrite the file if it exists"
    )


class ReadFileRequest(BaseModel):
    path: str = Field(
        ..., description="Path of the file to read (relative to data directory)"
    )
    encoding: str = Field("utf-8", description="File encoding")


class UpdateFileRequest(BaseModel):
    path: str = Field(
        ..., description="Path of the file to update (relative to data directory)"
    )
    content: str = Field(..., description="New content for the file")
    append: bool = Field(
        False, description="Whether to append to the file instead of overwriting"
    )


class DeleteFileRequest(BaseModel):
    path: str = Field(
        ..., description="Path of the file to delete (relative to data directory)"
    )


class ListDirectoryRequest(BaseModel):
    path: str = Field(
        ".", description="Directory path to list (relative to data directory)"
    )
    recursive: bool = Field(
        False, description="Whether to list directories recursively"
    )


class CreateDirectoryRequest(BaseModel):
    path: str = Field(
        ..., description="Directory path to create (relative to data directory)"
    )
    parents: bool = Field(
        True, description="Whether to create parent directories if they don't exist"
    )


class MoveRequest(BaseModel):
    source: str = Field(..., description="Source path (relative to data directory)")
    destination: str = Field(
        ..., description="Destination path (relative to data directory)"
    )
    overwrite: bool = Field(
        False, description="Whether to overwrite destination if it exists"
    )


class FileInfo(BaseModel):
    name: str
    path: str
    type: str  # "file" or "directory"
    size: Optional[int] = None
    modified: Optional[str] = None  # ISO format timestamp


# === A2A Communication ===


class A2AClient:
    """Agent-to-Agent communication client using RabbitMQ."""

    def __init__(self, amqp_url: str, server_name: str):
        self.amqp_url = amqp_url
        self.server_name = server_name
        self.connection = None
        self.channel = None
        self.queue_name = f"mcp.{server_name}"
        self._connect()

    def _connect(self):
        try:
            params = pika.URLParameters(self.amqp_url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()

            # Declare queue for this server
            self.channel.queue_declare(queue=self.queue_name, durable=True)

            # Declare exchange for broadcasting
            self.channel.exchange_declare(
                exchange="mcp.events", exchange_type="topic", durable=True
            )

            # Bind queue to exchange
            self.channel.queue_bind(
                exchange="mcp.events",
                queue=self.queue_name,
                routing_key=f"mcp.{self.server_name}.#",
            )

            logger.info(f"Connected to RabbitMQ and set up queue {self.queue_name}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None

    def send_event(self, event_type: str, data: Dict, routing_key: str = None):
        """Send an event to other agents."""
        if not self.channel:
            logger.warning("Cannot send event: not connected to RabbitMQ")
            return False

        if not routing_key:
            routing_key = f"mcp.events.{event_type}"

        message = {
            "type": event_type,
            "source": self.server_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        try:
            self.channel.basic_publish(
                exchange="mcp.events",
                routing_key=routing_key,
                body=json.dumps(message).encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type="application/json",
                ),
            )
            logger.debug(f"Sent event {event_type} to {routing_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            return False

    def close(self):
        """Close the connection."""
        if self.connection:
            self.connection.close()


# Initialize A2A client
a2a_client = A2AClient(AMQP_URL, SERVER_NAME)


# === Helper Functions ===


def safe_path(path: str) -> Path:
    """Ensure the path is within the data directory."""
    requested_path = Path(path)

    # Convert to absolute path within DATA_DIR
    if requested_path.is_absolute():
        # If absolute, ensure it's within DATA_DIR
        try:
            requested_path.relative_to(DATA_DIR)
            full_path = requested_path
        except ValueError:
            # Path is absolute but outside DATA_DIR, so join with DATA_DIR
            full_path = Path(DATA_DIR) / Path(*requested_path.parts[1:])
    else:
        # Path is relative, so join with DATA_DIR
        full_path = Path(DATA_DIR) / requested_path

    # Normalize path to resolve any .. or . components
    full_path = full_path.resolve()

    # Ensure the path is still within DATA_DIR
    try:
        full_path.relative_to(Path(DATA_DIR))
    except ValueError:
        raise ValueError(f"Path {path} resolves outside of data directory")

    return full_path


def update_metrics():
    """Update Prometheus metrics."""
    file_count = 0
    dir_count = 0
    total_bytes = 0

    for root, dirs, files in os.walk(DATA_DIR):
        dir_count += len(dirs)
        file_count += len(files)

        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_bytes += os.path.getsize(file_path)
            except (OSError, FileNotFoundError):
                pass

    FILE_COUNT.set(file_count)
    DIRECTORY_COUNT.set(dir_count)
    TOTAL_BYTES.set(total_bytes)


def get_file_info(path: Path) -> FileInfo:
    """Get information about a file or directory."""
    if not path.exists():
        raise FileNotFoundError(f"Path {path} not found")

    stat = path.stat()

    return FileInfo(
        name=path.name,
        path=str(path.relative_to(Path(DATA_DIR))),
        type="directory" if path.is_dir() else "file",
        size=stat.st_size if path.is_file() else None,
        modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


# === MCP API Endpoints ===


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(
        content=prometheus_client.generate_latest(), media_type="text/plain"
    )


@app.post("/mcp/listTools", response_model=ListToolsResponse)
async def list_tools(request: ListToolsRequest = None):
    """List available MCP tools."""
    tools = [
        {
            "name": "createFile",
            "description": "Create a new file with specified content",
            "input_schema": CreateFileRequest.schema(),
        },
        {
            "name": "readFile",
            "description": "Read content from a file",
            "input_schema": ReadFileRequest.schema(),
        },
        {
            "name": "updateFile",
            "description": "Update an existing file",
            "input_schema": UpdateFileRequest.schema(),
        },
        {
            "name": "deleteFile",
            "description": "Delete a file",
            "input_schema": DeleteFileRequest.schema(),
        },
        {
            "name": "listDirectory",
            "description": "List contents of a directory",
            "input_schema": ListDirectoryRequest.schema(),
        },
        {
            "name": "createDirectory",
            "description": "Create a new directory",
            "input_schema": CreateDirectoryRequest.schema(),
        },
        {
            "name": "moveFile",
            "description": "Move or rename a file or directory",
            "input_schema": MoveRequest.schema(),
        },
    ]

    return {"tools": tools}


@app.post("/mcp/callTool")
async def call_tool(request: CallToolRequest):
    """Call an MCP tool."""
    start_time = time.time()
    tool_name = request.name
    correlation_id = request.correlation_id or str(uuid.uuid4())

    logger.info(f"Tool call: {tool_name} (correlation_id: {correlation_id})")

    # For streaming responses
    if request.stream:
        return EventSourceResponse(
            stream_tool_response(tool_name, request.arguments, correlation_id)
        )

    try:
        # Dispatch to the appropriate tool handler
        response = await handle_tool_call(tool_name, request.arguments, correlation_id)
        REQUEST_COUNT.labels(tool=tool_name, status="success").inc()
        REQUEST_LATENCY.labels(tool=tool_name).observe(time.time() - start_time)
        return response
    except Exception as e:
        logger.error(f"Tool call error: {tool_name} - {str(e)}")
        REQUEST_COUNT.labels(tool=tool_name, status="error").inc()
        REQUEST_LATENCY.labels(tool=tool_name).observe(time.time() - start_time)

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=500, detail={"error": str(e), "type": type(e).__name__}
        )


async def stream_tool_response(tool_name: str, arguments: Dict, correlation_id: str):
    """Stream a tool response for SSE."""
    try:
        # Initial event to confirm the stream started
        yield {
            "event": "started",
            "id": correlation_id,
            "data": json.dumps(
                {
                    "type": "progress",
                    "message": f"Starting {tool_name}...",
                    "percentage": 0,
                }
            ),
        }

        # Call the tool handler and handle any intermediate progress events
        response = await handle_tool_call(
            tool_name, arguments, correlation_id, stream=True
        )

        # Final result event
        yield {"event": "result", "id": correlation_id, "data": json.dumps(response)}

        # End the stream
        yield {
            "event": "done",
            "id": correlation_id,
            "data": json.dumps(
                {"type": "progress", "message": "Done", "percentage": 100}
            ),
        }
    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        yield {
            "event": "error",
            "id": correlation_id,
            "data": json.dumps({"error": str(e), "type": type(e).__name__}),
        }


async def handle_tool_call(
    tool_name: str, arguments: Dict, correlation_id: str, stream: bool = False
) -> List[CallToolResponseItem]:
    """Handle a tool call based on the tool name."""
    # Update metrics on each call
    update_metrics()

    # Emitted when a tool is called
    a2a_client.send_event(
        "tool_call",
        {"tool": tool_name, "args": arguments, "correlation_id": correlation_id},
    )

    handlers = {
        "createFile": handle_create_file,
        "readFile": handle_read_file,
        "updateFile": handle_update_file,
        "deleteFile": handle_delete_file,
        "listDirectory": handle_list_directory,
        "createDirectory": handle_create_directory,
        "moveFile": handle_move,
    }

    handler = handlers.get(tool_name)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    result = await handler(arguments, correlation_id)

    # Event for tool completion
    a2a_client.send_event(
        "tool_complete", {"tool": tool_name, "correlation_id": correlation_id}
    )

    return result


# === Tool Handlers ===


async def handle_create_file(
    arguments: Dict, correlation_id: str
) -> List[CallToolResponseItem]:
    """Handle the createFile tool."""
    request = CreateFileRequest(**arguments)
    full_path = safe_path(request.path)

    # Check if file exists
    if full_path.exists() and not request.overwrite:
        raise HTTPException(
            status_code=409,
            detail=f"File {request.path} already exists and overwrite is False",
        )

    # Ensure parent directory exists
    full_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    try:
        full_path.write_text(request.content)
        logger.info(f"Created file: {request.path}")

        # Notify other agents about file creation
        a2a_client.send_event(
            "file_created", {"path": request.path, "correlation_id": correlation_id}
        )

        return [
            CallToolResponseItem(
                type="text", content=f"File {request.path} created successfully"
            )
        ]
    except Exception as e:
        logger.error(f"Failed to create file {request.path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create file: {str(e)}")


async def handle_read_file(
    arguments: Dict, correlation_id: str
) -> List[CallToolResponseItem]:
    """Handle the readFile tool."""
    request = ReadFileRequest(**arguments)
    full_path = safe_path(request.path)

    # Check if file exists
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File {request.path} not found")

    if full_path.is_dir():
        raise HTTPException(
            status_code=400, detail=f"Path {request.path} is a directory, not a file"
        )

    # Read file
    try:
        content = full_path.read_text(encoding=request.encoding)

        # Detect format based on file extension
        format = "text"
        if full_path.suffix.lower() in [".json"]:
            format = "json"
        elif full_path.suffix.lower() in [".md", ".markdown"]:
            format = "markdown"
        elif full_path.suffix.lower() in [".yml", ".yaml"]:
            format = "yaml"
        elif full_path.suffix.lower() in [".html", ".htm"]:
            format = "html"
        elif full_path.suffix.lower() in [
            ".py",
            ".js",
            ".ts",
            ".java",
            ".c",
            ".cpp",
            ".cs",
            ".php",
            ".rb",
            ".go",
        ]:
            format = "code"

        logger.info(f"Read file: {request.path}")

        # Notify other agents about file access
        a2a_client.send_event(
            "file_read", {"path": request.path, "correlation_id": correlation_id}
        )

        return [CallToolResponseItem(type="text", content=content, format=format)]
    except Exception as e:
        logger.error(f"Failed to read file {request.path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


async def handle_update_file(
    arguments: Dict, correlation_id: str
) -> List[CallToolResponseItem]:
    """Handle the updateFile tool."""
    request = UpdateFileRequest(**arguments)
    full_path = safe_path(request.path)

    # Check if file exists
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File {request.path} not found")

    if full_path.is_dir():
        raise HTTPException(
            status_code=400, detail=f"Path {request.path} is a directory, not a file"
        )

    # Update file
    try:
        if request.append:
            # Append to file
            with full_path.open("a") as f:
                f.write(request.content)
        else:
            # Overwrite file
            full_path.write_text(request.content)

        logger.info(f"Updated file: {request.path} (append={request.append})")

        # Notify other agents about file update
        a2a_client.send_event(
            "file_updated",
            {
                "path": request.path,
                "append": request.append,
                "correlation_id": correlation_id,
            },
        )

        return [
            CallToolResponseItem(
                type="text", content=f"File {request.path} updated successfully"
            )
        ]
    except Exception as e:
        logger.error(f"Failed to update file {request.path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")


async def handle_delete_file(
    arguments: Dict, correlation_id: str
) -> List[CallToolResponseItem]:
    """Handle the deleteFile tool."""
    request = DeleteFileRequest(**arguments)
    full_path = safe_path(request.path)

    # Check if file exists
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File {request.path} not found")

    # Delete file
    try:
        if full_path.is_dir():
            # Remove directory recursively
            import shutil

            shutil.rmtree(full_path)
        else:
            # Remove file
            full_path.unlink()

        logger.info(f"Deleted: {request.path}")

        # Notify other agents about file deletion
        a2a_client.send_event(
            "file_deleted", {"path": request.path, "correlation_id": correlation_id}
        )

        return [
            CallToolResponseItem(
                type="text", content=f"{request.path} deleted successfully"
            )
        ]
    except Exception as e:
        logger.error(f"Failed to delete {request.path}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")


async def handle_list_directory(
    arguments: Dict, correlation_id: str
) -> List[CallToolResponseItem]:
    """Handle the listDirectory tool."""
    request = ListDirectoryRequest(**arguments)
    full_path = safe_path(request.path)

    # Check if directory exists
    if not full_path.exists():
        raise HTTPException(
            status_code=404, detail=f"Directory {request.path} not found"
        )

    if not full_path.is_dir():
        raise HTTPException(
            status_code=400, detail=f"Path {request.path} is a file, not a directory"
        )

    # List directory
    try:
        entries = []

        if request.recursive:
            # Recursive listing
            for root, dirs, files in os.walk(full_path):
                root_path = Path(root)

                # Add directories
                for dir_name in dirs:
                    dir_path = root_path / dir_name
                    try:
                        entries.append(get_file_info(dir_path))
                    except Exception as e:
                        logger.warning(f"Error getting info for {dir_path}: {e}")

                # Add files
                for file_name in files:
                    file_path = root_path / file_name
                    try:
                        entries.append(get_file_info(file_path))
                    except Exception as e:
                        logger.warning(f"Error getting info for {file_path}: {e}")
        else:
            # Non-recursive listing
            for entry in full_path.iterdir():
                try:
                    entries.append(get_file_info(entry))
                except Exception as e:
                    logger.warning(f"Error getting info for {entry}: {e}")

        # Sort entries: directories first, then files, alphabetically within each group
        entries.sort(key=lambda e: (0 if e.type == "directory" else 1, e.name))

        logger.info(f"Listed directory: {request.path} (recursive={request.recursive})")

        return [
            CallToolResponseItem(
                type="json",
                content={
                    "path": request.path,
                    "entries": [entry.dict() for entry in entries],
                },
            )
        ]
    except Exception as e:
        logger.error(f"Failed to list directory {request.path}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list directory: {str(e)}"
        )


async def handle_create_directory(
    arguments: Dict, correlation_id: str
) -> List[CallToolResponseItem]:
    """Handle the createDirectory tool."""
    request = CreateDirectoryRequest(**arguments)
    full_path = safe_path(request.path)

    # Create directory
    try:
        full_path.mkdir(parents=request.parents, exist_ok=True)
        logger.info(f"Created directory: {request.path}")

        # Notify other agents about directory creation
        a2a_client.send_event(
            "directory_created",
            {"path": request.path, "correlation_id": correlation_id},
        )

        return [
            CallToolResponseItem(
                type="text", content=f"Directory {request.path} created successfully"
            )
        ]
    except FileExistsError:
        logger.warning(f"Directory already exists: {request.path}")
        return [
            CallToolResponseItem(
                type="text", content=f"Directory {request.path} already exists"
            )
        ]
    except Exception as e:
        logger.error(f"Failed to create directory {request.path}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create directory: {str(e)}"
        )


async def handle_move(
    arguments: Dict, correlation_id: str
) -> List[CallToolResponseItem]:
    """Handle the moveFile tool."""
    request = MoveRequest(**arguments)
    source_path = safe_path(request.source)
    dest_path = safe_path(request.destination)

    # Check if source exists
    if not source_path.exists():
        raise HTTPException(
            status_code=404, detail=f"Source {request.source} not found"
        )

    # Check if destination exists and overwrite not allowed
    if dest_path.exists() and not request.overwrite:
        raise HTTPException(
            status_code=409,
            detail=f"Destination {request.destination} already exists and overwrite is False",
        )

    # Create parent directory of destination if it doesn't exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Move file or directory
    try:
        import shutil

        # If destination exists and overwrite is True, remove it first
        if dest_path.exists() and request.overwrite:
            if dest_path.is_dir():
                shutil.rmtree(dest_path)
            else:
                dest_path.unlink()

        # Move the file or directory
        if source_path.is_dir():
            shutil.move(str(source_path), str(dest_path))
        else:
            shutil.move(str(source_path), str(dest_path))

        logger.info(f"Moved {request.source} to {request.destination}")

        # Notify other agents about move
        a2a_client.send_event(
            "file_moved",
            {
                "source": request.source,
                "destination": request.destination,
                "correlation_id": correlation_id,
            },
        )

        return [
            CallToolResponseItem(
                type="text",
                content=f"Moved {request.source} to {request.destination} successfully",
            )
        ]
    except Exception as e:
        logger.error(f"Failed to move {request.source} to {request.destination}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to move: {str(e)}")


# === Shutdown handler ===


@app.on_event("shutdown")
def shutdown_event():
    """Clean up resources on shutdown."""
    if a2a_client:
        a2a_client.close()


# === Main entry point ===

if __name__ == "__main__":
    logger.info(f"Starting File Manager MCP Server on port {MCP_SERVER_PORT}")
    logger.info(f"Data directory: {DATA_DIR}")

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=MCP_SERVER_PORT)
