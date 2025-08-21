# TLQ Client for Python

A Python client library for [TLQ (Tiny Little Queue)](https://github.com/skyaktech/tlq), a minimal message queue server written in Rust.

## Features

- Simple, lightweight Python client for TLQ
- Full support for all TLQ API operations
- Built-in retry logic with exponential backoff
- Environment variable configuration
- Type hints and comprehensive error handling
- Context manager support
- Extensive test coverage

## Installation

```bash
pip install tlq-client
```

## Quick Start

```python
from tlq_client import TLQClient

# Create client with default settings (localhost:1337)
client = TLQClient()

# Add a message to the queue
message_id = client.add_message("Hello, TLQ!")
print(f"Added message: {message_id}")

# Get messages from the queue
messages = client.get_messages(count=1)
for message in messages:
    print(f"Received: {message.body} (ID: {message.id})")
    
    # Process the message...
    # Then delete it from the queue
    client.delete_messages(message.id)
```

## Configuration

### Constructor Parameters

```python
client = TLQClient(
    host="localhost",        # TLQ server hostname
    port=1337,              # TLQ server port
    timeout=30.0,           # Request timeout in seconds
    max_retries=3           # Maximum retry attempts
)
```

### Environment Variables

You can also configure the client using environment variables:

- `TLQ_HOST` - Server hostname (default: localhost)
- `TLQ_PORT` - Server port (default: 1337)
- `TLQ_TIMEOUT` - Request timeout in seconds (default: 30.0)
- `TLQ_MAX_RETRIES` - Maximum retry attempts (default: 3)

```bash
export TLQ_HOST=queue.example.com
export TLQ_PORT=8080
export TLQ_TIMEOUT=60.0
export TLQ_MAX_RETRIES=5

python your_script.py
```

## API Reference

### TLQClient

#### `health_check() -> bool`

Check if the TLQ server is healthy.

```python
if client.health_check():
    print("TLQ server is running")
else:
    print("TLQ server is not available")
```

#### `add_message(body: str) -> str`

Add a message to the queue. Returns the message ID.

```python
message_id = client.add_message("Process this task")
```

**Note:** Messages are limited to 64KB in size.

#### `get_messages(count: int = 1) -> List[TLQMessage]`

Retrieve messages from the queue.

```python
# Get one message
messages = client.get_messages()

# Get multiple messages
messages = client.get_messages(count=5)

for message in messages:
    print(f"ID: {message.id}")
    print(f"Body: {message.body}")
    print(f"State: {message.state}")
    print(f"Retry Count: {message.retry_count}")
```

#### `delete_messages(message_ids: Union[str, List[str]])`

Delete processed messages from the queue.

```python
# Delete single message
client.delete_messages(message_id)

# Delete multiple messages
client.delete_messages([id1, id2, id3])
```

#### `retry_messages(message_ids: Union[str, List[str]])`

Return messages to the queue for retry.

```python
# Retry single message
client.retry_messages(message_id)

# Retry multiple messages  
client.retry_messages([id1, id2, id3])
```

#### `purge_queue()`

Clear all messages from the queue.

```python
client.purge_queue()
```

### TLQMessage

Message objects returned by `get_messages()`:

```python
@dataclass
class TLQMessage:
    id: str           # UUID v7 message identifier
    body: str         # Message content
    state: str        # Message state (e.g., "Ready", "Processing")
    retry_count: int  # Number of retry attempts
```

## Error Handling

The client provides specific exception types for different error conditions:

```python
from tlq_client import (
    TLQError,           # Base exception
    TLQConnectionError, # Connection failures
    TLQTimeoutError,    # Request timeouts
    TLQServerError,     # Server errors (4xx, 5xx)
    TLQValidationError  # Client-side validation errors
)

try:
    client.add_message("Hello, TLQ!")
except TLQValidationError as e:
    print(f"Validation error: {e}")
except TLQConnectionError as e:
    print(f"Connection error: {e}")
except TLQTimeoutError as e:
    print(f"Timeout error: {e}")
except TLQServerError as e:
    print(f"Server error: {e} (status: {e.status_code})")
except TLQError as e:
    print(f"TLQ error: {e}")
```

## Context Manager Support

The client can be used as a context manager to ensure proper cleanup:

```python
with TLQClient() as client:
    message_id = client.add_message("Hello!")
    messages = client.get_messages()
    # Session automatically closed when exiting context
```

## Examples

### Basic Producer

```python
from tlq_client import TLQClient

def produce_messages():
    with TLQClient() as client:
        for i in range(10):
            message_id = client.add_message(f"Task {i}")
            print(f"Queued task {i}: {message_id}")

if __name__ == "__main__":
    produce_messages()
```

### Basic Consumer

```python
import time
from tlq_client import TLQClient, TLQError

def consume_messages():
    with TLQClient() as client:
        while True:
            try:
                messages = client.get_messages(count=5)
                
                if not messages:
                    print("No messages available, sleeping...")
                    time.sleep(1)
                    continue
                
                for message in messages:
                    try:
                        # Process the message
                        print(f"Processing: {message.body}")
                        time.sleep(0.1)  # Simulate work
                        
                        # Mark as completed
                        client.delete_messages(message.id)
                        print(f"Completed: {message.id}")
                        
                    except Exception as e:
                        print(f"Failed to process {message.id}: {e}")
                        # Return to queue for retry
                        client.retry_messages(message.id)
                        
            except TLQError as e:
                print(f"TLQ error: {e}")
                time.sleep(5)  # Back off on errors

if __name__ == "__main__":
    consume_messages()
```

### Configuration from Environment

```python
import os
from tlq_client import TLQClient

# Set environment variables
os.environ['TLQ_HOST'] = 'queue.myapp.com'
os.environ['TLQ_PORT'] = '8080'
os.environ['TLQ_TIMEOUT'] = '60'

# Client automatically picks up environment configuration
client = TLQClient()
print(f"Connected to {client.config.base_url}")
```

## Development

### Setup Development Environment

```bash
# Create virtual environment (recommended on macOS/Linux to avoid system Python restrictions)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=tlq_client --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestTLQClient::test_add_message_success
```

### Code Quality

```bash
# Format code
black tlq_client tests

# Sort imports  
isort tlq_client tests

# Lint code
flake8 tlq_client tests

# Type checking
mypy tlq_client
```

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- [TLQ Server](https://github.com/skyaktech/tlq) - The TLQ message queue server
- [TLQ Node.js Client](https://github.com/skyaktech/tlq-client-node) - Node.js client library