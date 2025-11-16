# ETSPI MCP Server

**Model Context Protocol (MCP) server for Etsy shop management**

The ETSPI MCP server enables AI assistants like Claude to manage Etsy shops and listings through natural language. It exposes 21 MCP tools that map to the etspi-cli commands, allowing LLMs to perform all shop management tasks conversationally.

---

## Table of Contents

- [What is ETSPI MCP?](#what-is-etspi-mcp)
- [Features](#features)
- [Installation](#installation)
- [Authentication Setup](#authentication-setup)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

---

## What is ETSPI MCP?

The Model Context Protocol (MCP) is an open standard that enables AI assistants to connect to external tools and data sources. The ETSPI MCP server implements this protocol to provide:

- **Natural language shop management**: Use conversational AI to manage your Etsy shop
- **21 specialized tools**: Complete coverage of shop, listing, inventory, and media operations
- **Automatic token refresh**: Seamless authentication with automatic token management
- **Rich error handling**: Clear, actionable error messages
- **JMESPath query support**: Advanced filtering and data transformation

---

## Features

### Shop & Listing Discovery
- Get shop information by ID, user, or name
- Search listings with advanced filters (state, section, keywords)
- Sort and paginate results

### Listing Management (CRUD)
- Create draft listings with full detail
- Update existing listings
- Delete listings (with confirmation)
- Get listing details with optional includes (images, shipping, inventory, etc.)

### Inventory Management
- Get listing inventory (variants, SKUs, prices, quantities)
- Update inventory in bulk
- Transform data for easy modification

### Media Management
- **Images**: Upload, retrieve, and delete listing images with rank, alt-text, watermark support
- **Videos**: Upload, retrieve, and delete listing videos
- **Files**: Manage digital files for digital product listings

### Property Management
- Get listing properties (customizable attributes)
- Update property values (size, color, material, etc.)

---

## Installation

### Prerequisites

- Python 3.12 or higher
- `etspi` CLI installed (for initial authentication)
- An Etsy API key (from Etsy Developer Portal)

### Install ETSPI with MCP Support

```bash
# Clone the repository
git clone https://github.com/sov2000/etspi-cli.git
cd etspi-cli

# Install with Poetry
poetry install

# Or install with pip
pip install -e .
```

This will install both the `etspi` CLI and the `etspi-mcp` server.

---

## Authentication Setup

The MCP server uses pre-authenticated tokens from the CLI. You must authenticate once using the CLI before using the MCP server.

### Step 1: Authenticate with Etsy

```bash
# Run the auth command to authenticate with Etsy
etspi auth -tF

# This will:
# 1. Generate an authorization URL
# 2. Open your browser for OAuth consent
# 3. Capture the authorization code via local HTTPS server
# 4. Exchange code for access/refresh tokens
# 5. Save tokens to ~/.etspi/auth.env
```

### Step 2: Verify Authentication

```bash
# Test that authentication works
etspi user

# You should see your Etsy user information
```

### Step 3: Start Using MCP

Once authenticated, the MCP server will automatically use the saved tokens from `~/.etspi/auth.env`.

**Authentication File Location**: `~/.etspi/auth.env`

**Token Auto-Refresh**: The MCP server automatically refreshes tokens before they expire and saves them back to the auth file.

---

## Configuration

### Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "etspi": {
      "command": "etspi-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

### Cline (VS Code Extension)

Add to your Cline MCP settings:

```json
{
  "mcpServers": {
    "etspi": {
      "command": "etspi-mcp",
      "args": []
    }
  }
}
```

### Other MCP Clients

The server uses stdio transport and can be configured in any MCP-compatible client:

```json
{
  "command": "etspi-mcp",
  "args": [],
  "transport": "stdio"
}
```

---

## Available Tools

The ETSPI MCP server provides 21 tools organized into categories:

### Authentication & User (1 tool)

- **`etspi_get_user_info`**: Get authenticated user information or specific user details

### Shop Discovery (2 tools)

- **`etspi_get_shop`**: Get shop by ID, user ID, or name search
- **`etspi_find_shop_listings`**: Search/filter listings within a shop

### Listing Management (4 tools)

- **`etspi_get_listing`**: Get listing details by ID
- **`etspi_create_draft_listing`**: Create new draft listing
- **`etspi_update_listing`**: Update existing listing
- **`etspi_delete_listing`**: Delete a listing

### Inventory Management (2 tools)

- **`etspi_get_listing_inventory`**: Get inventory details (variants, SKUs, prices)
- **`etspi_update_listing_inventory`**: Update inventory in bulk

### Image Management (3 tools)

- **`etspi_get_listing_images`**: Get all images or specific image
- **`etspi_upload_listing_image`**: Upload/update listing image
- **`etspi_delete_listing_image`**: Delete listing image

### Video Management (3 tools)

- **`etspi_get_listing_videos`**: Get all videos or specific video
- **`etspi_upload_listing_video`**: Upload/update listing video
- **`etspi_delete_listing_video`**: Delete listing video

### File Management (3 tools)

- **`etspi_get_listing_files`**: Get digital files for listing
- **`etspi_upload_listing_file`**: Upload/associate digital file
- **`etspi_delete_listing_file`**: Delete digital file

### Property Management (2 tools)

- **`etspi_get_listing_properties`**: Get listing properties
- **`etspi_update_listing_property`**: Update property values

---

## Usage Examples

### Example 1: Getting Shop Information

**Prompt to AI:**
```
Show me information about my Etsy shop
```

**What the AI does:**
1. Calls `etspi_get_user_info` to get your user ID
2. Calls `etspi_get_shop` with your user ID
3. Presents shop details in readable format

### Example 2: Creating a New Listing

**Prompt to AI:**
```
Create a new draft listing for a handmade ceramic mug.
Price: $25, Quantity: 10, Title: "Handmade Blue Ceramic Mug",
Description: "Beautiful handmade ceramic mug in ocean blue glaze"
```

**What the AI does:**
1. Gathers required fields (who_made, when_made, taxonomy_id)
2. Constructs listing_data JSON
3. Calls `etspi_create_draft_listing` with shop_id and listing_data
4. Returns created listing details

### Example 3: Finding Low Inventory Items

**Prompt to AI:**
```
Show me all active listings with less than 5 items in stock
```

**What the AI does:**
1. Calls `etspi_find_shop_listings` with state="Active"
2. For each listing, calls `etspi_get_listing_inventory`
3. Filters locally for quantity < 5
4. Presents filtered list

### Example 4: Bulk Price Update

**Prompt to AI:**
```
Increase prices by 10% for all listings with "vintage" in the title
```

**What the AI does:**
1. Calls `etspi_find_shop_listings` with keywords="vintage"
2. For each listing:
   - Calculates new price (+10%)
   - Calls `etspi_update_listing` with new price
3. Reports results and any errors

### Example 5: Managing Images

**Prompt to AI:**
```
Upload this image to listing 123456 as the first image
[Provides image file path or URL]
```

**What the AI does:**
1. Calls `etspi_upload_listing_image` with:
   - listing_id: 123456
   - image_uri: [file path or URL]
   - rank: 1
2. Confirms upload success

### Example 6: Using JMESPath Queries

**Prompt to AI:**
```
Get all my active listings and show just the ID, title, and price
```

**What the AI does:**
1. Calls `etspi_find_shop_listings` with:
   - state: "Active"
   - query: "results[*].{id: listing_id, title: title, price: price.amount}"
2. Returns filtered, transformed results

---

## Troubleshooting

### "Auth directory not found" Error

**Problem**: MCP server can't find `~/.etspi/` directory

**Solution**: Run `etspi auth -tF` first to authenticate with the CLI

### "Auth config not found" Error

**Problem**: `~/.etspi/auth.env` file doesn't exist

**Solution**: Run `etspi auth -tF` to create the auth file

### "Auth config is missing required keys" Error

**Problem**: Auth file is incomplete or corrupted

**Solution**:
1. Delete `~/.etspi/auth.env`
2. Run `etspi auth -tF` again

### Token Expired / Unauthorized Errors

**Problem**: Access token has expired

**Solution**: The server should auto-refresh. If not:
1. Run `etspi user` from CLI to trigger refresh
2. Restart MCP server

### "Unknown tool" Errors

**Problem**: Tool name misspelled or doesn't exist

**Solution**: Check tool name against the [Available Tools](#available-tools) list. All tools are prefixed with `etspi_`.

### MCP Server Won't Start

**Problem**: Server crashes on startup

**Solution**:
1. Check that Python 3.12+ is installed: `python --version`
2. Verify etspi-mcp is installed: `which etspi-mcp`
3. Check authentication: `etspi user`
4. Run server manually to see errors: `etspi-mcp`

### File Upload Issues

**Problem**: Image/video/file uploads fail

**Solution**:
- Ensure file exists and path is correct
- For base64 data, ensure it's properly encoded
- Check file size limits (Etsy has max file sizes)
- Verify you have write permissions for the shop

---

## Development

### Running Tests

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
pytest tests/mcp/

# Run with coverage
pytest --cov=etspi.mcp tests/mcp/
```

### Project Structure

```
etspi/mcp/
├── __init__.py
├── server.py              # Main MCP server
├── auth.py                # Authentication manager
├── utils.py               # Utility functions
├── schemas.py             # Pydantic schemas
└── tools/                 # Tool implementations
    ├── __init__.py
    ├── auth_tools.py
    ├── shop_tools.py
    ├── listing_tools.py
    ├── inventory_tools.py
    ├── media_tools.py
    └── property_tools.py
```

### Adding New Tools

1. **Define schema** in `schemas.py`:
```python
class MyNewToolParams(BaseModel):
    param1: str = Field(description="...")
    param2: Optional[int] = Field(default=None, description="...")
```

2. **Create tool handler** in appropriate `tools/*.py` file:
```python
async def handle_my_new_tool(etsy_api, arguments: dict) -> list:
    params = MyNewToolParams(**arguments)
    # ... implementation
```

3. **Add to TOOLS list**:
```python
TOOLS = [
    Tool(
        name="etspi_my_new_tool",
        description="...",
        inputSchema=MyNewToolParams.model_json_schema()
    ),
    # ... other tools
]
```

4. **Register in router**:
```python
async def handle_tool_call(tool_name: str, etsy_api, arguments: dict) -> list:
    if tool_name == "etspi_my_new_tool":
        return await handle_my_new_tool(etsy_api, arguments)
    # ...
```

5. **Update `tools/__init__.py`** to include new tool in aggregation

---

## Security Considerations

- **Token Storage**: Tokens are stored in `~/.etspi/auth.env` with file permissions 644 (readable by owner)
- **Local Execution**: MCP server runs locally on your machine, not in the cloud
- **No Token Exposure**: Tokens are never sent to LLMs or exposed in tool responses
- **Auto-Refresh**: Tokens are automatically refreshed to maintain security

---

## Support & Feedback

- **Issues**: [GitHub Issues](https://github.com/sov2000/etspi-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sov2000/etspi-cli/discussions)
- **Documentation**: [Main README](README.md)
- **MCP Specification**: [Model Context Protocol](https://modelcontextprotocol.io/)

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- Uses the [Etsy API v3](https://developers.etsy.com/documentation/)
- Powered by the `etspi` CLI tool

---

**Version**: 1.1.0
**Last Updated**: 2025-11-16
**Status**: Production Ready
