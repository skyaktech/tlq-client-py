"""Tests for TLQ client."""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from tlq_client import TLQClient, TLQMessage, TLQError, TLQTimeoutError, TLQConnectionError
from tlq_client.exceptions import TLQServerError, TLQValidationError


class TestTLQClient:
    """Tests for TLQClient class."""
    
    def test_init_with_defaults(self):
        """Test client initialization with default values."""
        client = TLQClient()
        assert client.config.host == "localhost"
        assert client.config.port == 1337
        assert client.config.timeout == 30.0
        assert client.config.max_retries == 3
    
    def test_init_with_params(self):
        """Test client initialization with custom parameters."""
        client = TLQClient(
            host="example.com",
            port=8080,
            timeout=60.0,
            max_retries=5
        )
        assert client.config.host == "example.com"
        assert client.config.port == 8080
        assert client.config.timeout == 60.0
        assert client.config.max_retries == 5
    
    @patch.dict(os.environ, {
        'TLQ_HOST': 'env-host',
        'TLQ_PORT': '9000',
        'TLQ_TIMEOUT': '45.0',
        'TLQ_MAX_RETRIES': '2'
    })
    def test_init_with_env_vars(self):
        """Test client initialization with environment variables."""
        client = TLQClient()
        assert client.config.host == "env-host"
        assert client.config.port == 9000
        assert client.config.timeout == 45.0
        assert client.config.max_retries == 2
    
    def test_validate_message_body_valid(self):
        """Test message body validation with valid message."""
        client = TLQClient()
        client._validate_message_body("Hello, world!")  # Should not raise
    
    def test_validate_message_body_too_large(self):
        """Test message body validation with oversized message."""
        client = TLQClient()
        large_body = "x" * (client.MAX_MESSAGE_SIZE + 1)
        
        with pytest.raises(TLQValidationError, match="exceeds maximum size"):
            client._validate_message_body(large_body)
    
    @patch('requests.Session.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_get.return_value = mock_response
        
        client = TLQClient()
        result = client.health_check()
        
        assert result is True
        mock_get.assert_called_once_with(
            "http://localhost:1337/hello",
            timeout=30.0
        )
    
    @patch('requests.Session.get')
    def test_health_check_failure(self, mock_get):
        """Test health check failure."""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        client = TLQClient()
        result = client.health_check()
        
        assert result is False
    
    @patch('requests.Session.post')
    def test_add_message_success(self, mock_post):
        """Test successful message addition."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {"id": "test-message-id"}
        mock_post.return_value = mock_response
        
        client = TLQClient()
        message_id = client.add_message("Hello, TLQ!")
        
        assert message_id == "test-message-id"
        mock_post.assert_called_once_with(
            "http://localhost:1337/add",
            json={"body": "Hello, TLQ!"},
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
    
    @patch('requests.Session.post')
    def test_add_message_validation_error(self, mock_post):
        """Test message addition with validation error."""
        client = TLQClient()
        large_body = "x" * (client.MAX_MESSAGE_SIZE + 1)
        
        with pytest.raises(TLQValidationError):
            client.add_message(large_body)
        
        mock_post.assert_not_called()
    
    @patch('requests.Session.post')
    def test_get_messages_success(self, mock_post):
        """Test successful message retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {
            "messages": [
                {
                    "id": "msg-1",
                    "body": "Hello",
                    "state": "Ready",
                    "retry_count": 0
                },
                {
                    "id": "msg-2", 
                    "body": "World",
                    "state": "Ready",
                    "retry_count": 0
                }
            ]
        }
        mock_post.return_value = mock_response
        
        client = TLQClient()
        messages = client.get_messages(count=2)
        
        assert len(messages) == 2
        assert messages[0].id == "msg-1"
        assert messages[0].body == "Hello"
        assert messages[1].id == "msg-2"
        assert messages[1].body == "World"
        
        mock_post.assert_called_once_with(
            "http://localhost:1337/get",
            json={"count": 2},
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
    
    @patch('requests.Session.post')
    def test_delete_messages_single_id(self, mock_post):
        """Test deleting single message."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_post.return_value = mock_response
        
        client = TLQClient()
        client.delete_messages("msg-1")
        
        mock_post.assert_called_once_with(
            "http://localhost:1337/delete",
            json={"ids": ["msg-1"]},
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
    
    @patch('requests.Session.post')
    def test_delete_messages_multiple_ids(self, mock_post):
        """Test deleting multiple messages."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_post.return_value = mock_response
        
        client = TLQClient()
        client.delete_messages(["msg-1", "msg-2"])
        
        mock_post.assert_called_once_with(
            "http://localhost:1337/delete",
            json={"ids": ["msg-1", "msg-2"]},
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
    
    @patch('requests.Session.post')
    def test_retry_messages_single_id(self, mock_post):
        """Test retrying single message."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_post.return_value = mock_response
        
        client = TLQClient()
        client.retry_messages("msg-1")
        
        mock_post.assert_called_once_with(
            "http://localhost:1337/retry",
            json={"ids": ["msg-1"]},
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
    
    @patch('requests.Session.post')
    def test_retry_messages_multiple_ids(self, mock_post):
        """Test retrying multiple messages."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_post.return_value = mock_response
        
        client = TLQClient()
        client.retry_messages(["msg-1", "msg-2"])
        
        mock_post.assert_called_once_with(
            "http://localhost:1337/retry",
            json={"ids": ["msg-1", "msg-2"]},
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
    
    @patch('requests.Session.post')
    def test_purge_queue(self, mock_post):
        """Test queue purging."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_post.return_value = mock_response
        
        client = TLQClient()
        client.purge_queue()
        
        mock_post.assert_called_once_with(
            "http://localhost:1337/purge",
            json=None,
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
    
    @patch('requests.Session.post')
    def test_connection_error(self, mock_post):
        """Test connection error handling."""
        mock_post.side_effect = requests.ConnectionError("Connection failed")
        
        client = TLQClient()
        with pytest.raises(TLQConnectionError, match="Failed to connect"):
            client.add_message("test")
    
    @patch('requests.Session.post')
    def test_timeout_error(self, mock_post):
        """Test timeout error handling."""
        mock_post.side_effect = requests.Timeout("Request timed out")
        
        client = TLQClient()
        with pytest.raises(TLQTimeoutError, match="Request timed out"):
            client.add_message("test")
    
    @patch('requests.Session.post')
    def test_server_error(self, mock_post):
        """Test server error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.ok = False
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        client = TLQClient()
        with pytest.raises(TLQServerError, match="Server returned 500"):
            client.add_message("test")
    
    @patch('time.sleep')
    @patch('requests.Session.post')
    def test_retry_logic(self, mock_post, mock_sleep):
        """Test retry logic with exponential backoff."""
        # First two calls fail with 500, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.ok = False
        mock_response_fail.text = "Server Error"
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.ok = True
        mock_response_success.json.return_value = {"id": "test-id"}
        
        mock_post.side_effect = [
            mock_response_fail,
            mock_response_fail, 
            mock_response_success
        ]
        
        client = TLQClient(max_retries=3)
        message_id = client.add_message("test")
        
        assert message_id == "test-id"
        assert mock_post.call_count == 3
        # Check exponential backoff: sleep(1), sleep(2)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1
    
    def test_context_manager(self):
        """Test client as context manager."""
        with patch('requests.Session.close') as mock_close:
            with TLQClient() as client:
                assert isinstance(client, TLQClient)
            mock_close.assert_called_once()