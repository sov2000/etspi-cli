"""
MCP tool modules for ETSPI

Aggregates all tool definitions and handlers from individual tool modules.
"""
from . import auth_tools
from . import shop_tools
from . import listing_tools
from . import inventory_tools
from . import media_tools
from . import property_tools


# Aggregate all tool definitions
ALL_TOOLS = (
    auth_tools.TOOLS +
    shop_tools.TOOLS +
    listing_tools.TOOLS +
    inventory_tools.TOOLS +
    media_tools.TOOLS +
    property_tools.TOOLS
)


# Map tool names to their handler modules
TOOL_HANDLERS = {
    # Auth tools
    "etspi_get_user_info": auth_tools,

    # Shop tools
    "etspi_get_shop": shop_tools,
    "etspi_find_shop_listings": shop_tools,

    # Listing tools
    "etspi_get_listing": listing_tools,
    "etspi_create_draft_listing": listing_tools,
    "etspi_update_listing": listing_tools,
    "etspi_delete_listing": listing_tools,

    # Inventory tools
    "etspi_get_listing_inventory": inventory_tools,
    "etspi_update_listing_inventory": inventory_tools,

    # Media tools
    "etspi_get_listing_images": media_tools,
    "etspi_upload_listing_image": media_tools,
    "etspi_delete_listing_image": media_tools,
    "etspi_get_listing_videos": media_tools,
    "etspi_upload_listing_video": media_tools,
    "etspi_delete_listing_video": media_tools,
    "etspi_get_listing_files": media_tools,
    "etspi_upload_listing_file": media_tools,
    "etspi_delete_listing_file": media_tools,

    # Property tools
    "etspi_get_listing_properties": property_tools,
    "etspi_update_listing_property": property_tools,
}


async def handle_tool_call(tool_name: str, etsy_api, arguments: dict):
    """
    Route a tool call to the appropriate handler module

    Args:
        tool_name: Name of the tool being called
        etsy_api: EtsyAPI instance
        arguments: Tool arguments dict

    Returns:
        List of Content responses
    """
    handler_module = TOOL_HANDLERS.get(tool_name)

    if handler_module:
        return await handler_module.handle_tool_call(tool_name, etsy_api, arguments)

    # Unknown tool
    from ..utils import format_error_response, to_json_string
    from mcp.types import TextContent

    return [TextContent(
        type="text",
        text=to_json_string(format_error_response(
            ValueError(f"Unknown tool: {tool_name}")
        ))
    )]
