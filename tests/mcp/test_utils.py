"""
Tests for ETSPI MCP utility functions
"""
import pytest
import base64
from etspi.mcp.utils import (
    apply_jmespath_query,
    format_success_response,
    format_error_response,
    to_json_string,
    decode_file_data,
    validate_positive_integer,
    safe_get,
    build_include_list
)


def test_apply_jmespath_query():
    """Test JMESPath query application"""
    data = {
        "results": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
    }

    # Valid query
    result = apply_jmespath_query(data, "results[*].id")
    assert result == [1, 2]

    # No query returns original data
    result = apply_jmespath_query(data, None)
    assert result == data

    # Invalid query raises ValueError
    with pytest.raises(ValueError) as exc_info:
        apply_jmespath_query(data, "invalid[[[query")
    assert "Invalid JMESPath query" in str(exc_info.value)


def test_format_success_response():
    """Test success response formatting"""
    data = {"listing_id": 123, "title": "Test"}
    response = format_success_response(data)

    assert response["success"] is True
    assert response["data"] == data


def test_format_error_response():
    """Test error response formatting"""
    error = ValueError("Test error message")
    response = format_error_response(error)

    assert response["success"] is False
    assert response["error"]["type"] == "ValueError"
    assert response["error"]["message"] == "Test error message"


def test_to_json_string():
    """Test JSON string conversion"""
    data = {"key": "value"}

    # Pretty format
    json_str = to_json_string(data, pretty=True)
    assert "{\n" in json_str
    assert "  " in json_str

    # Compact format
    json_str = to_json_string(data, pretty=False)
    assert "\n" not in json_str


def test_decode_file_data():
    """Test file data decoding"""
    # Base64 encoded data
    original = b"Hello, World!"
    encoded = base64.b64encode(original).decode('utf-8')

    decoded = decode_file_data(file_data=encoded)
    assert decoded == original

    # Base64 with data URI prefix
    data_uri = f"data:text/plain;base64,{encoded}"
    decoded = decode_file_data(file_data=data_uri)
    assert decoded == original

    # No data provided
    result = decode_file_data()
    assert result is None


def test_validate_positive_integer():
    """Test positive integer validation"""
    # Valid positive integer
    assert validate_positive_integer(5, "test_field") == 5
    assert validate_positive_integer("10", "test_field") == 10

    # Invalid: zero
    with pytest.raises(ValueError) as exc_info:
        validate_positive_integer(0, "test_field")
    assert "must be a positive integer" in str(exc_info.value)

    # Invalid: negative
    with pytest.raises(ValueError):
        validate_positive_integer(-5, "test_field")

    # Invalid: non-numeric
    with pytest.raises(ValueError):
        validate_positive_integer("abc", "test_field")


def test_safe_get():
    """Test safe nested dictionary access"""
    data = {
        "user": {
            "profile": {
                "name": "John Doe"
            }
        }
    }

    # Valid path
    assert safe_get(data, "user", "profile", "name") == "John Doe"

    # Invalid path returns default
    assert safe_get(data, "user", "missing", "key", default="N/A") == "N/A"

    # Partial path
    assert safe_get(data, "user", "profile") == {"name": "John Doe"}


def test_build_include_list():
    """Test include list building and validation"""
    # Valid includes
    includes = ["Images", "Shipping", "Inventory"]
    result = build_include_list(includes)
    assert result == includes

    # None/empty returns None
    assert build_include_list(None) is None
    assert build_include_list([]) is None

    # Invalid include value
    with pytest.raises(ValueError) as exc_info:
        build_include_list(["Images", "InvalidValue"])
    assert "Invalid include values" in str(exc_info.value)
