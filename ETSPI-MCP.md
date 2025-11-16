# ETSPI-MCP: Model Context Protocol Server for Etsy Shop Management

## Executive Summary

This document outlines the plan to add a Model Context Protocol (MCP) server to the `etspi-cli` project. The MCP server will expose the existing CLI functionality as a set of tools that LLMs and AI agents can use to manage Etsy shops and listings through natural language interactions.

## Table of Contents

1. [Goals and Objectives](#goals-and-objectives)
2. [MCP Architecture Overview](#mcp-architecture-overview)
3. [Proposed MCP Tools](#proposed-mcp-tools)
4. [Authentication Strategy](#authentication-strategy)
5. [Implementation Approach](#implementation-approach)
6. [Technical Considerations](#technical-considerations)
7. [Benefits and Use Cases](#benefits-and-use-cases)
8. [Project Structure](#project-structure)
9. [Development Phases](#development-phases)
10. [Testing Strategy](#testing-strategy)

---

## Goals and Objectives

### Primary Goals

1. **Expose CLI Functionality via MCP**: Create MCP tools that map to the 23 existing CLI commands, enabling LLMs to perform Etsy shop management tasks
2. **Natural Language Interface**: Allow users to manage their Etsy shop using conversational AI rather than command-line syntax
3. **Reuse Existing Infrastructure**: Leverage the existing `EtsyAPI` class, request models, and business logic without duplicating code
4. **Maintain Security**: Implement secure authentication and token management within the MCP context
5. **Enable Complex Workflows**: Allow AI agents to chain multiple operations together (e.g., "Create 5 listings from these product descriptions")

### Secondary Goals

- Provide rich tool descriptions that help LLMs understand when and how to use each tool
- Support both simple operations (get shop info) and complex workflows (bulk listing management)
- Enable file handling for images, videos, and digital products through MCP resources
- Provide comprehensive error handling and user feedback

---

## MCP Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    LLM / AI Agent                        │
│              (Claude, GPT, etc.)                         │
└─────────────────────┬───────────────────────────────────┘
                      │ MCP Protocol (stdio/SSE)
                      │
┌─────────────────────▼───────────────────────────────────┐
│                 ETSPI MCP Server                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MCP Tools Layer (23+ tools)                    │   │
│  │  - Authentication tools                          │   │
│  │  - Shop & listing discovery tools               │   │
│  │  - Listing CRUD tools                           │   │
│  │  - Media management tools                       │   │
│  │  - Inventory & property tools                   │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │  MCP Bridge Layer                               │   │
│  │  - Parameter validation & transformation        │   │
│  │  - Response formatting                          │   │
│  │  - Error handling & user feedback               │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │  Existing ETSPI Infrastructure                  │   │
│  │  - EtsyAPI class (etsy_api.py)                  │   │
│  │  - Request models (models/)                     │   │
│  │  - Auth helper (auth_helper.py)                 │   │
│  │  - Enums and utilities                          │   │
│  └──────────────────┬──────────────────────────────┘   │
└────────────────────┬┴──────────────────────────────────┘
                     │
                     │ HTTPS (Etsy API v3)
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Etsy API                                │
└─────────────────────────────────────────────────────────┘
```

### Core Components

1. **MCP Server**: Python-based MCP server using the official `mcp` SDK
2. **Tool Handlers**: Individual functions that map MCP tool calls to CLI functionality
3. **Authentication Manager**: Handles OAuth tokens and automatic refresh within MCP context
4. **Resource Providers**: Expose Etsy shop data as MCP resources for context
5. **Prompt Templates**: Optional pre-defined prompts for common workflows

---

## Proposed MCP Tools

### Tool Categories and Mapping

The MCP server will expose the following tools, organized by functional category:

#### 1. Authentication & Setup (2 tools)

| MCP Tool | CLI Command | Description | Parameters |
|----------|-------------|-------------|------------|
| `etspi_authenticate` | `auth` | Initialize OAuth 2.0 flow and obtain tokens | `api_key`, `persist_tokens?` |
| `etspi_get_user_info` | `user` | Get authenticated user information | `user_id?`, `query?` |

#### 2. Shop Discovery & Information (2 tools)

| MCP Tool | CLI Command | Description | Parameters |
|----------|-------------|-------------|------------|
| `etspi_get_shop` | `shop-get` | Get shop details by ID, user ID, or name | `shop_id?`, `user_id?`, `shop_name?`, `query?` |
| `etspi_find_shop_listings` | `shop-find` | Search listings within a shop with filters | `shop_id*`, `section_id?`, `state?`, `keywords?`, `sort_on?`, `sort_order?`, `include?`, `limit?`, `offset?`, `query?` |

#### 3. Listing Management (4 tools)

| MCP Tool | CLI Command | Description | Parameters |
|----------|-------------|-------------|------------|
| `etspi_get_listing` | `listing-get` | Retrieve a specific listing by ID | `listing_id*`, `include?`, `format?`, `query?` |
| `etspi_create_draft_listing` | `draft` | Create a new draft listing from JSON data | `shop_id*`, `listing_data*` |
| `etspi_update_listing` | `listing-update` | Update an existing listing | `shop_id*`, `listing_id*`, `listing_data*` |
| `etspi_delete_listing` | `listing-delete` | Delete a listing (with confirmation) | `listing_id*`, `confirm?` |

#### 4. Inventory Management (2 tools)

| MCP Tool | CLI Command | Description | Parameters |
|----------|-------------|-------------|------------|
| `etspi_get_listing_inventory` | `listing-get-iv` | Get inventory details including variants, SKUs, prices | `listing_id*`, `format?`, `query?` |
| `etspi_update_listing_inventory` | `listing-update-iv` | Update inventory for a listing | `listing_id*`, `inventory_data*` |

#### 5. Image Management (3 tools)

| MCP Tool | CLI Command | Description | Parameters |
|----------|-------------|-------------|------------|
| `etspi_get_listing_images` | `image-get` | Get all images or a specific image for a listing | `listing_id*`, `image_id?`, `query?` |
| `etspi_upload_listing_image` | `image-upload` | Upload or update a listing image | `shop_id*`, `listing_id*`, `image_file*`, `image_id?`, `rank?`, `alt_text?`, `overwrite?`, `watermark?` |
| `etspi_delete_listing_image` | `image-delete` | Delete a listing image | `listing_id*`, `image_id*`, `confirm?` |

#### 6. Video Management (3 tools)

| MCP Tool | CLI Command | Description | Parameters |
|----------|-------------|-------------|------------|
| `etspi_get_listing_videos` | `video-get` | Get all videos or a specific video for a listing | `listing_id*`, `video_id?`, `query?` |
| `etspi_upload_listing_video` | `video-upload` | Upload or update a listing video | `shop_id*`, `listing_id*`, `video_file*`, `video_id?` |
| `etspi_delete_listing_video` | `video-delete` | Delete a listing video | `shop_id*`, `listing_id*`, `video_id*`, `confirm?` |

#### 7. Digital File Management (3 tools)

| MCP Tool | CLI Command | Description | Parameters |
|----------|-------------|-------------|------------|
| `etspi_get_listing_files` | `file-get` | Get digital files associated with a listing | `shop_id*`, `listing_id*`, `file_id?`, `query?` |
| `etspi_upload_listing_file` | `file-upload` | Upload or associate a digital file with a listing | `shop_id*`, `listing_id*`, `file_path?`, `file_id?`, `rank?` |
| `etspi_delete_listing_file` | `file-delete` | Delete a digital file from a listing | `shop_id*`, `listing_id*`, `file_id*`, `confirm?` |

#### 8. Listing Properties (2 tools)

| MCP Tool | CLI Command | Description | Parameters |
|----------|-------------|-------------|------------|
| `etspi_get_listing_properties` | `prop-get` | Get custom properties for a listing | `shop_id*`, `listing_id*`, `property_id?`, `format?`, `query?` |
| `etspi_update_listing_property` | `prop-update` | Update a specific listing property | `shop_id*`, `listing_id*`, `property_id*`, `property_data*` |

**Total: 21 MCP Tools**

*Note: Parameters marked with `*` are required, others are optional. `query?` refers to JMESPath query support.*

### Enhanced Tools (Future Expansion)

Additional tools that could be built on top of existing functionality:

- `etspi_bulk_create_listings`: Create multiple listings from an array
- `etspi_bulk_update_listings`: Update multiple listings
- `etspi_clone_listing`: Clone an existing listing with modifications
- `etspi_get_taxonomy`: Get Etsy taxonomy for categorization
- `etspi_search_listings_by_keywords`: Advanced multi-shop search

---

## Authentication Strategy

### Challenge

MCP servers run in a different context than interactive CLIs. The OAuth 2.0 flow requires:
1. Opening a browser for user authorization
2. Running a local HTTPS server to catch the redirect
3. Managing token persistence across MCP sessions

### Proposed Solutions

#### Option 1: Pre-Authenticated Tokens (Recommended for Phase 1)

**Approach:**
- Users authenticate once using the existing `etspi auth` CLI command
- MCP server reads tokens from `~/.etspi/auth.env`
- MCP server handles automatic token refresh using refresh tokens
- On refresh, tokens are updated in the auth.env file

**Pros:**
- Simplest to implement
- Reuses existing auth infrastructure
- Works immediately with current auth flow
- Secure token storage

**Cons:**
- Requires users to authenticate outside MCP
- Not fully integrated into LLM workflow

**Implementation:**
```python
class EtspiMCPServer:
    def __init__(self):
        self.auth_config = self._load_auth_config()
        self.etsy_api = None

    def _load_auth_config(self):
        """Load authentication from ~/.etspi/auth.env"""
        config_path = Path.home() / ".etspi" / "auth.env"
        if not config_path.exists():
            raise AuthenticationError("No auth.env found. Run 'etspi auth' first.")
        return dotenv_values(config_path)

    def _get_etsy_api(self):
        """Get or create EtsyAPI instance with token refresh"""
        if not self.etsy_api:
            self.etsy_api = EtsyAPI(
                keystring=self.auth_config['key'],
                token=self.auth_config['token'],
                refresh_token=self.auth_config['refresh_token'],
                expiry=int(self.auth_config['expiry']),
                token_saver=self._save_refreshed_tokens
            )
        return self.etsy_api

    def _save_refreshed_tokens(self, token, refresh_token, expiry):
        """Callback to persist refreshed tokens"""
        config_path = Path.home() / ".etspi" / "auth.env"
        # Update auth.env file
```

#### Option 2: MCP Resource-Based Auth (Future Enhancement)

**Approach:**
- Expose an `etspi://auth/status` resource showing authentication state
- Provide an `etspi_authenticate` tool that guides users through OAuth
- Tool returns authorization URL for user to visit
- User provides callback code back to tool
- Tool completes token exchange

**Pros:**
- Fully integrated into MCP/LLM workflow
- Users never leave the AI interface

**Cons:**
- More complex to implement
- Requires careful UX design for multi-step flow
- May need MCP protocol extensions for interactive flows

#### Recommended Approach

**Phase 1:** Implement Option 1 (pre-authenticated tokens)
- Simple, secure, and leverages existing infrastructure
- Document the auth requirement clearly

**Phase 2:** Add Option 2 for seamless in-MCP authentication
- Enhance user experience
- Enable fully autonomous agent workflows

---

## Implementation Approach

### Technology Stack

**Core Dependencies:**
- `mcp` - Official MCP SDK for Python
- `click` - Already used by CLI (shared dependency)
- `python-dotenv` - Already used (shared dependency)
- Existing `etspi` package (all current dependencies)

**Development Dependencies:**
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `mcp-dev-tools` - MCP testing utilities

### Project Structure

```
etspi-cli/
├── etspi/
│   ├── cli.py                          # Existing CLI entry point
│   ├── commands/                       # Existing CLI commands
│   ├── etsyv3/                        # Existing Etsy API wrapper
│   └── mcp/                           # NEW: MCP server implementation
│       ├── __init__.py
│       ├── server.py                  # Main MCP server class
│       ├── tools/                     # MCP tool handlers
│       │   ├── __init__.py
│       │   ├── auth_tools.py         # Authentication tools
│       │   ├── shop_tools.py         # Shop discovery tools
│       │   ├── listing_tools.py      # Listing CRUD tools
│       │   ├── inventory_tools.py    # Inventory management tools
│       │   ├── media_tools.py        # Image/video/file tools
│       │   └── property_tools.py     # Property management tools
│       ├── resources/                 # MCP resource providers
│       │   ├── __init__.py
│       │   └── shop_resources.py     # Shop data as resources
│       ├── prompts/                   # Optional prompt templates
│       │   ├── __init__.py
│       │   └── workflow_prompts.py   # Pre-defined workflow prompts
│       ├── auth.py                    # Authentication manager for MCP
│       ├── schemas.py                 # Pydantic schemas for tool parameters
│       └── utils.py                   # Shared utilities
├── tests/
│   ├── cli/                           # Existing CLI tests
│   └── mcp/                           # NEW: MCP tests
│       ├── test_server.py
│       ├── test_tools.py
│       └── test_auth.py
├── examples/                          # NEW: Example configurations
│   ├── claude_desktop_config.json    # Claude Desktop MCP config
│   └── mcp_usage_examples.md         # Usage documentation
├── pyproject.toml                     # Update with MCP dependencies
└── README-MCP.md                      # NEW: MCP-specific documentation
```

### Core Implementation Files

#### 1. `etspi/mcp/server.py` - Main MCP Server

```python
"""
ETSPI MCP Server - Main entry point for Model Context Protocol server
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from .auth import EtspiAuthManager
from .tools import register_all_tools
from .resources import register_all_resources

class EtspiMCPServer:
    """MCP Server for Etsy shop management"""

    def __init__(self):
        self.server = Server("etspi-mcp")
        self.auth_manager = EtspiAuthManager()
        self.etsy_api = None

        # Register tools and resources
        register_all_tools(self.server, self)
        register_all_resources(self.server, self)

    def get_etsy_api(self):
        """Get authenticated EtsyAPI instance"""
        if not self.etsy_api:
            auth_config = self.auth_manager.get_auth_config()
            self.etsy_api = EtsyAPI(
                keystring=auth_config['key'],
                token=auth_config['token'],
                refresh_token=auth_config['refresh_token'],
                expiry=auth_config['expiry'],
                token_saver=self.auth_manager.save_tokens
            )
        return self.etsy_api

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

def main():
    """Entry point for MCP server"""
    server = EtspiMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
```

#### 2. `etspi/mcp/tools/listing_tools.py` - Example Tool Implementation

```python
"""
Listing management tools for MCP
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field
from typing import Optional, List
import json

class GetListingParams(BaseModel):
    """Parameters for etspi_get_listing tool"""
    listing_id: int = Field(description="The Etsy listing ID to retrieve")
    include: Optional[List[str]] = Field(
        default=None,
        description="Additional data to include (Shipping, Images, Shop, User, Translations, Inventory, Videos)"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )

class CreateDraftListingParams(BaseModel):
    """Parameters for etspi_create_draft_listing tool"""
    shop_id: int = Field(description="The Etsy shop ID")
    listing_data: dict = Field(description="JSON object containing listing details")

def register_listing_tools(server: Server, mcp_server):
    """Register listing management tools"""

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="etspi_get_listing",
                description=(
                    "Retrieve detailed information about a specific Etsy listing by ID. "
                    "Can optionally include related data like images, shipping info, inventory, etc. "
                    "Supports JMESPath queries for response filtering."
                ),
                inputSchema=GetListingParams.model_json_schema()
            ),
            Tool(
                name="etspi_create_draft_listing",
                description=(
                    "Create a new draft listing in an Etsy shop. "
                    "The listing_data should contain all required fields per Etsy API: "
                    "title, description, price, quantity, taxonomy_id, etc."
                ),
                inputSchema=CreateDraftListingParams.model_json_schema()
            ),
            # ... more listing tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls"""

        if name == "etspi_get_listing":
            params = GetListingParams(**arguments)
            etsy_api = mcp_server.get_etsy_api()

            try:
                result = etsy_api.get_listing(
                    listing_id=params.listing_id,
                    includes=params.include
                )

                # Apply JMESPath query if provided
                if params.query:
                    import jmespath
                    result = jmespath.search(params.query, result)

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as ex:
                return [TextContent(
                    type="text",
                    text=f"Error retrieving listing: {str(ex)}"
                )]

        elif name == "etspi_create_draft_listing":
            params = CreateDraftListingParams(**arguments)
            etsy_api = mcp_server.get_etsy_api()

            try:
                # Use existing request model
                from etspi.etsyv3.models.listing_request import CreateDraftListingRequest

                listing_request = CreateDraftListingRequest(params.listing_data)
                result = etsy_api.create_draft_listing(
                    shop_id=params.shop_id,
                    listing=listing_request
                )

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as ex:
                return [TextContent(
                    type="text",
                    text=f"Error creating draft listing: {str(ex)}"
                )]
```

#### 3. `etspi/mcp/auth.py` - Authentication Manager

```python
"""
Authentication manager for ETSPI MCP server
"""
from pathlib import Path
from dotenv import dotenv_values, set_key
from typing import Dict
import time

class EtspiAuthManager:
    """Manages authentication for ETSPI MCP server"""

    def __init__(self):
        self.auth_file = Path.home() / ".etspi" / "auth.env"
        self._ensure_auth_file_exists()

    def _ensure_auth_file_exists(self):
        """Ensure auth file and directory exist"""
        if not self.auth_file.parent.exists():
            raise FileNotFoundError(
                "Auth directory not found. Please run 'etspi auth' first to set up authentication."
            )

        if not self.auth_file.exists():
            raise FileNotFoundError(
                "Auth config not found. Please run 'etspi auth -tF' to authenticate with Etsy."
            )

    def get_auth_config(self) -> Dict[str, str]:
        """Load authentication configuration"""
        config = dotenv_values(self.auth_file)

        required_keys = ['key', 'token', 'refresh_token', 'expiry']
        missing_keys = [key for key in required_keys if key not in config]

        if missing_keys:
            raise ValueError(
                f"Auth config is missing required keys: {', '.join(missing_keys)}"
            )

        return {
            'key': config['key'],
            'token': config['token'],
            'refresh_token': config['refresh_token'],
            'expiry': int(config['expiry'])
        }

    def save_tokens(self, token: str, refresh_token: str, expiry: int):
        """Save refreshed tokens back to auth.env"""
        set_key(self.auth_file, 'token', token)
        set_key(self.auth_file, 'refresh_token', refresh_token)
        set_key(self.auth_file, 'expiry', str(expiry))

    def is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        try:
            config = self.get_auth_config()
            return int(config['expiry']) > int(time.time())
        except (FileNotFoundError, ValueError, KeyError):
            return False
```

### Entry Point Configuration

Add to `pyproject.toml`:

```toml
[tool.poetry.scripts]
etspi = "etspi.cli:cli"
etspi-mcp = "etspi.mcp.server:main"  # NEW: MCP server entry point
```

---

## Technical Considerations

### 1. Asynchronous vs Synchronous

**Challenge:** MCP servers use async/await, but the existing `EtsyAPI` class uses synchronous `requests` library.

**Solutions:**

**Option A: Async Wrapper (Recommended)**
```python
import asyncio
from functools import wraps

def async_wrapper(sync_func):
    """Wrap synchronous function for async context"""
    @wraps(sync_func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_func, *args, **kwargs)
    return wrapper

# Usage in tool handler
async def call_tool(name, arguments):
    etsy_api = mcp_server.get_etsy_api()
    result = await async_wrapper(etsy_api.get_listing)(listing_id=123)
```

**Option B: Migrate to HTTPX (Future)**
- Replace `requests` with `httpx` (supports both sync and async)
- Minimal changes to existing code
- Better long-term solution

**Recommendation:** Use Option A initially, plan Option B for future major version.

### 2. File Handling (Images, Videos, Files)

**Challenge:** MCP protocol has specific handling for binary data and file resources.

**Solutions:**

**For File Uploads:**
```python
class UploadImageParams(BaseModel):
    shop_id: int
    listing_id: int
    image_data: str = Field(description="Base64-encoded image data")
    # OR
    image_uri: str = Field(description="URI to image file (file://, http://, etc.)")
    rank: Optional[int] = None
    alt_text: Optional[str] = None

# In tool handler
import base64
from pathlib import Path

if params.image_data:
    # Decode base64
    image_bytes = base64.b64decode(params.image_data)
elif params.image_uri:
    # Handle different URI schemes
    if params.image_uri.startswith('file://'):
        path = Path(params.image_uri[7:])
        image_bytes = path.read_bytes()
    elif params.image_uri.startswith('http'):
        # Download from URL
        response = requests.get(params.image_uri)
        image_bytes = response.content
```

**For File Downloads:**
- Return image URLs in tool responses
- Optionally: Expose images as MCP resources with `blob://` URIs

### 3. Error Handling and User Feedback

**Best Practices:**

```python
# Structured error responses
try:
    result = etsy_api.some_operation()
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "data": result
        }, indent=2)
    )]
except EtsyAPIException as ex:
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": False,
            "error": {
                "type": ex.__class__.__name__,
                "message": str(ex),
                "code": getattr(ex, 'code', None)
            }
        }, indent=2)
    )]
```

### 4. JMESPath Query Support

**Implementation:**

```python
def apply_jmespath_query(data: dict, query: str):
    """Apply JMESPath query to data if provided"""
    if not query:
        return data

    import jmespath
    try:
        result = jmespath.search(query, data)
        return result if result is not None else data
    except jmespath.exceptions.JMESPathError as ex:
        raise ValueError(f"Invalid JMESPath query: {ex}")

# In tool handlers
result = etsy_api.get_shop(shop_id=params.shop_id)
filtered_result = apply_jmespath_query(result, params.query)
```

### 5. Rate Limiting and Caching

**Considerations:**

- Etsy API has rate limits (exact limits TBD from Etsy docs)
- MCP servers may be called frequently by LLMs
- Implement request caching for read operations

**Suggested Approach:**

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedEtsyAPI:
    """Wrapper around EtsyAPI with caching"""

    def __init__(self, etsy_api):
        self.api = etsy_api
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)

    def get_with_cache(self, cache_key, api_call, *args, **kwargs):
        """Get data with caching"""
        now = datetime.now()

        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if now - cached_time < self._cache_ttl:
                return cached_data

        # Call API
        result = api_call(*args, **kwargs)
        self._cache[cache_key] = (result, now)
        return result
```

### 6. Configuration Management

**MCP Server Configuration:**

Create a `mcp_config.json` in `~/.etspi/`:

```json
{
  "cache_enabled": true,
  "cache_ttl_seconds": 300,
  "auto_token_refresh": true,
  "verbose_logging": false,
  "default_includes": ["Images"],
  "max_results_per_query": 100
}
```

---

## Benefits and Use Cases

### Key Benefits

1. **Natural Language Shop Management**
   - "Show me all active listings in my shop"
   - "Create a new listing for a handmade ceramic mug priced at $25"
   - "Update the description of listing 12345 to include care instructions"

2. **Intelligent Automation**
   - Bulk operations: "Create 10 listings from this CSV file"
   - Conditional updates: "Update prices for all listings with 'vintage' in the title"
   - Data analysis: "Show me my 5 most expensive listings"

3. **Reduced Learning Curve**
   - No need to memorize CLI syntax
   - Conversational interface for non-technical users
   - Context-aware suggestions from LLM

4. **Enhanced Productivity**
   - Complex multi-step workflows in single requests
   - AI-assisted listing optimization (titles, descriptions, tags)
   - Automated routine tasks (daily price updates, seasonal description changes)

5. **Integration with AI Workflows**
   - Use Claude Code or other AI agents for shop management
   - Combine with other MCP tools (image generation, content writing)
   - Build autonomous shop management agents

### Use Case Examples

#### Use Case 1: Listing Creation Assistant

**User:** "I have 5 products to list. They're all handmade candles in different scents. Can you help me create listings?"

**AI Agent Flow:**
1. Gathers product details through conversation
2. Calls `etspi_get_shop` to get shop_id
3. For each product:
   - Constructs listing JSON with title, description, price, etc.
   - Calls `etspi_create_draft_listing`
   - Confirms creation with user
4. Returns summary of created listings

#### Use Case 2: Inventory Audit

**User:** "Show me all listings that are low on inventory (less than 5 items)"

**AI Agent Flow:**
1. Calls `etspi_find_shop_listings` to get all active listings
2. For each listing:
   - Calls `etspi_get_listing_inventory`
   - Checks quantity
3. Filters and presents low-inventory items
4. Optionally suggests restock actions

#### Use Case 3: Seasonal Update Campaign

**User:** "Update all winter-themed listings to include '20% off' in the title and a sale banner in the description"

**AI Agent Flow:**
1. Calls `etspi_find_shop_listings` with keyword filter "winter"
2. For each matching listing:
   - Calls `etspi_get_listing` to get current data
   - Modifies title and description
   - Calls `etspi_update_listing` with changes
3. Reports results and any errors

#### Use Case 4: Media Management

**User:** "Add this product image to listing 12345 as the first image"

**AI Agent Flow:**
1. User provides image (via file path, URL, or inline)
2. Calls `etspi_upload_listing_image` with rank=1
3. Confirms upload success
4. Optionally shows updated listing images

#### Use Case 5: Shop Analytics

**User:** "What's the average price of my active listings by category?"

**AI Agent Flow:**
1. Calls `etspi_find_shop_listings` for all active listings
2. Uses JMESPath or local processing to group by taxonomy/category
3. Calculates averages
4. Presents formatted results (could even generate charts if integrated with visualization tools)

---

## Development Phases

### Phase 1: Core Infrastructure (Week 1-2)

**Goals:**
- Set up MCP server scaffolding
- Implement authentication manager
- Create 3-5 basic tools (auth, shop, listing retrieval)
- Establish testing framework

**Deliverables:**
- Working MCP server executable (`etspi-mcp`)
- Authentication using existing CLI auth
- Tools: `etspi_get_user_info`, `etspi_get_shop`, `etspi_get_listing`, `etspi_find_shop_listings`
- Basic tests and documentation
- Example Claude Desktop configuration

**Success Criteria:**
- MCP server runs and responds to tool calls
- Can retrieve shop and listing information via MCP
- Tokens automatically refresh when needed

### Phase 2: CRUD Operations (Week 3-4)

**Goals:**
- Implement listing management tools
- Add inventory management
- Implement error handling and validation

**Deliverables:**
- Tools: `etspi_create_draft_listing`, `etspi_update_listing`, `etspi_delete_listing`
- Tools: `etspi_get_listing_inventory`, `etspi_update_listing_inventory`
- Comprehensive error messages
- Pydantic schemas for all tools
- Integration tests

**Success Criteria:**
- Can create, update, and delete listings via MCP
- Can manage inventory and variants
- Proper error handling and user feedback

### Phase 3: Media Management (Week 5-6)

**Goals:**
- Implement image, video, and file tools
- Handle binary data and file uploads
- Add resource providers for media

**Deliverables:**
- Tools: All image, video, and file management tools (9 tools)
- File handling utilities (base64, URI schemes)
- MCP resources for listing images
- Media upload examples and documentation

**Success Criteria:**
- Can upload/download/delete images, videos, and files
- Supports multiple file input methods
- Efficient handling of large binary data

### Phase 4: Properties & Advanced Features (Week 7-8)

**Goals:**
- Implement property management tools
- Add advanced query and filtering
- Optimize performance (caching, async)
- Add prompt templates

**Deliverables:**
- Tools: `etspi_get_listing_properties`, `etspi_update_listing_property`
- Enhanced JMESPath query support across all tools
- Request caching layer
- Pre-defined workflow prompts
- Performance benchmarks

**Success Criteria:**
- Can manage listing properties
- Response times improved via caching
- Comprehensive prompt library for common tasks

### Phase 5: Testing, Documentation & Release (Week 9-10)

**Goals:**
- Comprehensive testing
- Complete documentation
- Release preparation

**Deliverables:**
- Full test coverage (>80%)
- README-MCP.md with complete usage guide
- Example workflows and use cases
- Video tutorial (optional)
- PyPI release (v1.1.0 with MCP support)

**Success Criteria:**
- All tests passing
- Documentation complete and reviewed
- Successfully tested with Claude Desktop and other MCP clients
- Ready for public release

---

## Testing Strategy

### Unit Tests

**Test Coverage:**

1. **Authentication Tests** (`test_auth.py`)
   - Load auth config from file
   - Save refreshed tokens
   - Handle missing/invalid auth files
   - Token expiry validation

2. **Tool Tests** (`test_tools.py`)
   - Parameter validation (Pydantic schemas)
   - Tool handler logic
   - Response formatting
   - Error handling

3. **Utility Tests** (`test_utils.py`)
   - JMESPath query application
   - File handling (base64, URIs)
   - Data transformations

### Integration Tests

**Test Scenarios:**

1. **End-to-End Workflows**
   - Create draft listing → Get listing → Update listing → Delete listing
   - Get shop → Find listings → Get listing details
   - Upload image → Get images → Delete image

2. **Authentication Flow**
   - Initial auth check
   - Token refresh trigger
   - Token persistence

3. **Error Scenarios**
   - Invalid parameters
   - API errors (404, 403, etc.)
   - Network failures
   - Rate limiting

### MCP Protocol Tests

**Using MCP Test Utilities:**

```python
from mcp.test import MCPTestClient
import pytest

@pytest.mark.asyncio
async def test_get_listing_tool():
    """Test etspi_get_listing tool via MCP protocol"""
    async with MCPTestClient() as client:
        # Initialize connection
        await client.initialize()

        # List available tools
        tools = await client.list_tools()
        assert any(tool.name == "etspi_get_listing" for tool in tools)

        # Call tool
        result = await client.call_tool(
            "etspi_get_listing",
            {"listing_id": 12345, "include": ["Images"]}
        )

        # Verify response
        assert result.isSuccess
        assert "listing_id" in result.content[0].text
```

### Manual Testing Checklist

- [ ] Install in Claude Desktop
- [ ] Authenticate with real Etsy account
- [ ] Execute each tool at least once
- [ ] Test error scenarios (invalid IDs, missing params)
- [ ] Test file uploads with various formats
- [ ] Test JMESPath queries
- [ ] Verify token refresh works automatically
- [ ] Test multi-step workflows (create → update → delete)
- [ ] Test with large result sets (pagination)
- [ ] Monitor API rate limits

---

## Documentation Plan

### User Documentation

1. **README-MCP.md**
   - What is ETSPI MCP?
   - Installation instructions
   - Authentication setup
   - Configuration for Claude Desktop, Cline, and other MCP clients
   - Basic usage examples
   - Troubleshooting

2. **examples/mcp_usage_examples.md**
   - Example prompts for each tool
   - Multi-step workflow examples
   - Advanced use cases
   - Best practices

3. **API Reference**
   - Complete tool catalog with parameters and examples
   - Schema documentation
   - Error codes and handling

### Developer Documentation

1. **CONTRIBUTING-MCP.md**
   - How to add new tools
   - Testing guidelines
   - Code style
   - PR process

2. **Architecture Documentation**
   - System architecture diagram
   - Data flow
   - Authentication flow
   - Extension points

---

## Security Considerations

### Token Management

1. **Storage Security**
   - Tokens stored in `~/.etspi/auth.env` with appropriate file permissions (600)
   - No tokens in logs or error messages
   - Secure token refresh callback

2. **MCP Context**
   - MCP server runs locally (stdio transport)
   - No network exposure of tokens
   - Tokens never sent to LLM context

### Input Validation

1. **Parameter Validation**
   - Pydantic schemas validate all inputs
   - Type checking and range validation
   - Sanitize file paths to prevent directory traversal

2. **API Request Validation**
   - Reuse existing `EtsyAPI` validation
   - Verify shop_id ownership before mutations
   - Confirm destructive operations

### Rate Limiting

1. **Protection Mechanisms**
   - Implement request throttling
   - Cache read operations
   - Warn on excessive tool usage

---

## Future Enhancements

### Phase 6+ (Future Roadmap)

1. **Advanced Automation**
   - Scheduled tasks (price updates, seasonal changes)
   - Webhook support for Etsy events
   - Multi-shop management

2. **Analytics & Reporting**
   - Sales analytics tools
   - Inventory forecasting
   - Performance dashboards

3. **AI-Enhanced Features**
   - Listing optimization (SEO, descriptions)
   - Image tagging and alt-text generation
   - Competitor analysis

4. **Collaboration**
   - Team access controls
   - Shared tool configurations
   - Audit logs

5. **Extended Integrations**
   - Integration with shipping providers
   - Print-on-demand services
   - Accounting software

---

## Success Metrics

### Adoption Metrics
- Number of MCP server installations
- Active monthly users
- Tool usage frequency by tool type

### Performance Metrics
- Average tool response time
- API error rate
- Token refresh success rate
- Cache hit rate

### User Satisfaction
- GitHub stars and community feedback
- Issue resolution time
- Feature request volume

---

## Conclusion

The addition of an MCP server to `etspi-cli` will transform it from a powerful command-line tool into an AI-first shop management platform. By exposing existing functionality through MCP tools, we enable:

- **Natural language interaction** with Etsy shop data
- **Intelligent automation** of routine tasks
- **Enhanced productivity** through AI-assisted workflows
- **Broader accessibility** for non-technical shop owners

The phased implementation approach ensures we can deliver value incrementally while maintaining code quality and thorough testing. By leveraging the existing, well-designed CLI infrastructure, we minimize duplicated effort and maintain consistency across both interfaces.

**Next Steps:**
1. Review and approve this plan
2. Set up development branch and project structure
3. Begin Phase 1 implementation
4. Iterate based on feedback and testing

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Author:** AI Assistant (Claude)
**Status:** Draft for Review
