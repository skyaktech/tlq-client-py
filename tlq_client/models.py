"""TLQ Client data models."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class TLQMessage:
    """Represents a TLQ message."""
    id: str
    body: str
    state: str
    retry_count: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TLQMessage':
        """Create a TLQMessage from dictionary data."""
        return cls(
            id=data['id'],
            body=data['body'],
            state=data['state'],
            retry_count=data['retry_count']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TLQMessage to dictionary."""
        return {
            'id': self.id,
            'body': self.body,
            'state': self.state,
            'retry_count': self.retry_count
        }


@dataclass
class TLQConfig:
    """Configuration for TLQ client."""
    host: str = "localhost"
    port: int = 1337
    timeout: float = 30.0
    max_retries: int = 3
    
    @property
    def base_url(self) -> str:
        """Get the base URL for TLQ server."""
        return f"http://{self.host}:{self.port}"