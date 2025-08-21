"""Tests for TLQ exceptions."""

import pytest
from tlq_client.exceptions import (
    TLQError,
    TLQConnectionError,
    TLQTimeoutError,
    TLQServerError,
    TLQValidationError
)


class TestTLQExceptions:
    """Tests for TLQ exception classes."""
    
    def test_tlq_error_base(self):
        """Test base TLQError exception."""
        error = TLQError("Base error message")
        assert str(error) == "Base error message"
        assert isinstance(error, Exception)
    
    def test_tlq_connection_error(self):
        """Test TLQConnectionError exception."""
        error = TLQConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, TLQError)
        assert isinstance(error, Exception)
    
    def test_tlq_timeout_error(self):
        """Test TLQTimeoutError exception."""
        error = TLQTimeoutError("Request timed out")
        assert str(error) == "Request timed out"
        assert isinstance(error, TLQError)
        assert isinstance(error, Exception)
    
    def test_tlq_server_error_without_status_code(self):
        """Test TLQServerError without status code."""
        error = TLQServerError("Server error occurred")
        assert str(error) == "Server error occurred"
        assert error.status_code is None
        assert isinstance(error, TLQError)
        assert isinstance(error, Exception)
    
    def test_tlq_server_error_with_status_code(self):
        """Test TLQServerError with status code."""
        error = TLQServerError("Internal server error", 500)
        assert str(error) == "Internal server error"
        assert error.status_code == 500
        assert isinstance(error, TLQError)
        assert isinstance(error, Exception)
    
    def test_tlq_validation_error(self):
        """Test TLQValidationError exception."""
        error = TLQValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, TLQError)
        assert isinstance(error, Exception)
    
    def test_exception_inheritance_chain(self):
        """Test that all exceptions inherit from TLQError."""
        exceptions = [
            TLQConnectionError("test"),
            TLQTimeoutError("test"),
            TLQServerError("test"),
            TLQValidationError("test")
        ]
        
        for exception in exceptions:
            assert isinstance(exception, TLQError)
            assert isinstance(exception, Exception)