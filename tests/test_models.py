"""Tests for TLQ models."""

import pytest
from tlq_client.models import TLQMessage, TLQConfig


class TestTLQMessage:
    """Tests for TLQMessage class."""
    
    def test_message_creation(self):
        """Test TLQMessage creation."""
        message = TLQMessage(
            id="test-id",
            body="Hello, world!",
            state="Ready", 
            retry_count=0
        )
        
        assert message.id == "test-id"
        assert message.body == "Hello, world!"
        assert message.state == "Ready"
        assert message.retry_count == 0
    
    def test_from_dict(self):
        """Test TLQMessage creation from dictionary."""
        data = {
            "id": "msg-123",
            "body": "Test message",
            "state": "Processing",
            "retry_count": 2
        }
        
        message = TLQMessage.from_dict(data)
        
        assert message.id == "msg-123"
        assert message.body == "Test message"
        assert message.state == "Processing"
        assert message.retry_count == 2
    
    def test_to_dict(self):
        """Test TLQMessage conversion to dictionary."""
        message = TLQMessage(
            id="msg-456",
            body="Another test",
            state="Failed",
            retry_count=1
        )
        
        result = message.to_dict()
        expected = {
            "id": "msg-456",
            "body": "Another test", 
            "state": "Failed",
            "retry_count": 1
        }
        
        assert result == expected


class TestTLQConfig:
    """Tests for TLQConfig class."""
    
    def test_config_defaults(self):
        """Test TLQConfig with default values."""
        config = TLQConfig()
        
        assert config.host == "localhost"
        assert config.port == 1337
        assert config.timeout == 30.0
        assert config.max_retries == 3
    
    def test_config_custom_values(self):
        """Test TLQConfig with custom values."""
        config = TLQConfig(
            host="example.com",
            port=8080,
            timeout=60.0,
            max_retries=5
        )
        
        assert config.host == "example.com"
        assert config.port == 8080
        assert config.timeout == 60.0
        assert config.max_retries == 5
    
    def test_base_url_property(self):
        """Test base_url property."""
        config = TLQConfig(host="example.com", port=9000)
        assert config.base_url == "http://example.com:9000"
        
        config = TLQConfig()  # defaults
        assert config.base_url == "http://localhost:1337"