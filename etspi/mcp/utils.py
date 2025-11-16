"""
Utility functions for ETSPI MCP server

Provides common functionality used across multiple tools including:
- JMESPath query support
- Response formatting
- Error handling
- File handling utilities
"""
import json
import base64
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, Callable
from functools import wraps
import jmespath


def apply_jmespath_query(data: Any, query: Optional[str]) -> Any:
    """
    Apply JMESPath query to data if provided

    Args:
        data: Data to query (dict, list, etc.)
        query: JMESPath query string (optional)

    Returns:
        Filtered/transformed data if query provided, otherwise original data

    Raises:
        ValueError: If JMESPath query is invalid
    """
    if not query:
        return data

    try:
        result = jmespath.search(query, data)
        return result if result is not None else data
    except jmespath.exceptions.JMESPathError as ex:
        raise ValueError(f"Invalid JMESPath query: {ex}")


def format_success_response(data: Any) -> Dict[str, Any]:
    """
    Format successful API response

    Args:
        data: Response data from API

    Returns:
        Formatted response dictionary with success flag
    """
    return {
        "success": True,
        "data": data
    }


def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Format error response

    Args:
        error: Exception that occurred

    Returns:
        Formatted error dictionary with details
    """
    error_info = {
        "success": False,
        "error": {
            "type": error.__class__.__name__,
            "message": str(error)
        }
    }

    # Add error code if available (from Etsy API exceptions)
    if hasattr(error, 'code'):
        error_info["error"]["code"] = error.code

    return error_info


def to_json_string(data: Any, pretty: bool = True) -> str:
    """
    Convert data to JSON string

    Args:
        data: Data to convert
        pretty: Whether to format with indentation

    Returns:
        JSON string representation
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def async_wrapper(sync_func: Callable) -> Callable:
    """
    Wrap synchronous function for async context

    This allows the synchronous EtsyAPI methods to be called
    from async MCP tool handlers without blocking.

    Args:
        sync_func: Synchronous function to wrap

    Returns:
        Async wrapper function
    """
    @wraps(sync_func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: sync_func(*args, **kwargs))
    return wrapper


def decode_file_data(file_data: Optional[str] = None,
                     file_uri: Optional[str] = None) -> Optional[bytes]:
    """
    Decode file data from base64 string or URI

    Supports:
    - Base64 encoded data
    - file:// URIs (local file paths)
    - http:// and https:// URIs (downloads)

    Args:
        file_data: Base64 encoded file data
        file_uri: URI to file (file://, http://, https://)

    Returns:
        File contents as bytes, or None if neither provided

    Raises:
        ValueError: If file cannot be decoded or loaded
    """
    if file_data:
        try:
            # Remove data URI prefix if present (e.g., "data:image/png;base64,")
            if ';base64,' in file_data:
                file_data = file_data.split(';base64,')[1]

            return base64.b64decode(file_data)
        except Exception as ex:
            raise ValueError(f"Failed to decode base64 file data: {ex}")

    if file_uri:
        if file_uri.startswith('file://'):
            # Local file path
            path = Path(file_uri[7:])
            if not path.exists():
                raise ValueError(f"File not found: {path}")
            return path.read_bytes()

        elif file_uri.startswith(('http://', 'https://')):
            # Download from URL
            import requests
            try:
                response = requests.get(file_uri, timeout=30)
                response.raise_for_status()
                return response.content
            except Exception as ex:
                raise ValueError(f"Failed to download file from {file_uri}: {ex}")

        else:
            raise ValueError(f"Unsupported URI scheme: {file_uri}")

    return None


def validate_positive_integer(value: Any, field_name: str) -> int:
    """
    Validate that a value is a positive integer

    Args:
        value: Value to validate
        field_name: Name of field (for error messages)

    Returns:
        Validated integer value

    Raises:
        ValueError: If value is not a positive integer
    """
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValueError(f"{field_name} must be a positive integer")
        return int_value
    except (TypeError, ValueError) as ex:
        raise ValueError(f"Invalid {field_name}: {ex}")


def safe_get(data: Dict, *keys, default=None) -> Any:
    """
    Safely get nested dictionary value

    Args:
        data: Dictionary to search
        *keys: Sequence of keys to traverse
        default: Default value if key path not found

    Returns:
        Value at key path, or default if not found

    Example:
        safe_get(data, 'user', 'profile', 'name', default='Unknown')
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def build_include_list(includes: Optional[list]) -> Optional[list]:
    """
    Build and validate include parameter list for Etsy API

    Args:
        includes: List of include values

    Returns:
        Validated include list, or None if empty

    Raises:
        ValueError: If any include value is invalid
    """
    if not includes:
        return None

    valid_includes = {
        'Shipping', 'Images', 'Shop', 'User',
        'Translations', 'Inventory', 'Videos'
    }

    invalid = [inc for inc in includes if inc not in valid_includes]
    if invalid:
        raise ValueError(
            f"Invalid include values: {', '.join(invalid)}. "
            f"Valid values: {', '.join(sorted(valid_includes))}"
        )

    return includes


def parse_range(range_str: Optional[str]) -> Optional[tuple]:
    """
    Parse range string in format "offset,limit"

    Args:
        range_str: Range string like "0,25" or "10,50"

    Returns:
        Tuple of (offset, limit), or None if not provided

    Raises:
        ValueError: If range format is invalid
    """
    if not range_str:
        return None

    try:
        parts = range_str.split(',')
        if len(parts) != 2:
            raise ValueError("Range must be in format 'offset,limit'")

        offset = int(parts[0].strip())
        limit = int(parts[1].strip())

        if offset < 0 or limit <= 0:
            raise ValueError("Offset must be >= 0 and limit must be > 0")

        return (offset, limit)
    except ValueError as ex:
        raise ValueError(f"Invalid range format: {ex}")
