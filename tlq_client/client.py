"""TLQ Client implementation."""

import json
import os
import time
from typing import List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout, RequestException

from .exceptions import (
    TLQConnectionError, 
    TLQTimeoutError, 
    TLQServerError, 
    TLQValidationError
)
from .models import TLQMessage, TLQConfig


class TLQClient:
    """Client for interacting with TLQ (Tiny Little Queue) server."""
    
    MAX_MESSAGE_SIZE = 65536  # 64KB
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None
    ):
        """Initialize TLQ client with configuration.
        
        Args:
            host: TLQ server hostname (default: localhost, env: TLQ_HOST)
            port: TLQ server port (default: 1337, env: TLQ_PORT)  
            timeout: Request timeout in seconds (default: 30.0, env: TLQ_TIMEOUT)
            max_retries: Max retry attempts (default: 3, env: TLQ_MAX_RETRIES)
        """
        self.config = TLQConfig(
            host=host or os.getenv("TLQ_HOST", "localhost"),
            port=int(port or os.getenv("TLQ_PORT", 1337)),
            timeout=float(timeout or os.getenv("TLQ_TIMEOUT", 30.0)),
            max_retries=int(max_retries or os.getenv("TLQ_MAX_RETRIES", 3))
        )
        
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=0)  # We handle retries ourselves
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _validate_message_body(self, body: str) -> None:
        """Validate message body size."""
        if len(body.encode('utf-8')) > self.MAX_MESSAGE_SIZE:
            raise TLQValidationError(
                f"Message body exceeds maximum size of {self.MAX_MESSAGE_SIZE} bytes"
            )
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[dict] = None,
        retries: Optional[int] = None
    ) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = f"{self.config.base_url}{endpoint}"
        max_retries = retries if retries is not None else self.config.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, 
                        timeout=self.config.timeout
                    )
                else:
                    response = self.session.post(
                        url,
                        json=data,
                        timeout=self.config.timeout,
                        headers={"Content-Type": "application/json"}
                    )
                
                if response.status_code >= 500 and attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                if not response.ok:
                    raise TLQServerError(
                        f"Server returned {response.status_code}: {response.text}",
                        response.status_code
                    )
                
                return response
                
            except ConnectionError as e:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise TLQConnectionError(f"Failed to connect to TLQ server: {e}")
            
            except Timeout as e:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise TLQTimeoutError(f"Request timed out: {e}")
            
            except RequestException as e:
                raise TLQConnectionError(f"Request failed: {e}")
    
    def health_check(self) -> bool:
        """Check if TLQ server is healthy.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = self._make_request("GET", "/hello", retries=1)
            return response.status_code == 200
        except Exception:
            return False
    
    def add_message(self, body: str) -> str:
        """Add a message to the queue.
        
        Args:
            body: Message content
            
        Returns:
            Message ID
            
        Raises:
            TLQValidationError: If message body is too large
            TLQConnectionError: If connection fails
            TLQTimeoutError: If request times out
            TLQServerError: If server returns error
        """
        self._validate_message_body(body)
        
        response = self._make_request("POST", "/add", {"body": body})
        result = response.json()
        return result["id"]
    
    def get_messages(self, count: int = 1) -> List[TLQMessage]:
        """Get messages from the queue.
        
        Args:
            count: Number of messages to retrieve (default: 1)
            
        Returns:
            List of TLQMessage objects
            
        Raises:
            TLQConnectionError: If connection fails
            TLQTimeoutError: If request times out
            TLQServerError: If server returns error
        """
        response = self._make_request("POST", "/get", {"count": count})
        result = response.json()
        return [TLQMessage.from_dict(msg) for msg in result["messages"]]
    
    def delete_messages(self, message_ids: Union[str, List[str]]) -> None:
        """Delete processed messages from the queue.
        
        Args:
            message_ids: Single message ID or list of message IDs
            
        Raises:
            TLQConnectionError: If connection fails
            TLQTimeoutError: If request times out
            TLQServerError: If server returns error
        """
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        self._make_request("POST", "/delete", {"ids": message_ids})
    
    def retry_messages(self, message_ids: Union[str, List[str]]) -> None:
        """Return messages to the queue for retry.
        
        Args:
            message_ids: Single message ID or list of message IDs
            
        Raises:
            TLQConnectionError: If connection fails
            TLQTimeoutError: If request times out
            TLQServerError: If server returns error
        """
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        self._make_request("POST", "/retry", {"ids": message_ids})
    
    def purge_queue(self) -> None:
        """Clear all messages from the queue.
        
        Raises:
            TLQConnectionError: If connection fails
            TLQTimeoutError: If request times out
            TLQServerError: If server returns error
        """
        self._make_request("POST", "/purge")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()