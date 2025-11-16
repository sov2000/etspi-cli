"""
Inventory management tools for ETSPI MCP server
"""
from mcp.types import Tool, TextContent
from ..schemas import GetListingInventoryParams, UpdateListingInventoryParams
from ..utils import (
    apply_jmespath_query,
    format_success_response,
    format_error_response,
    to_json_string
)
from etspi.etsyv3.models import UpdateListingInventoryRequest


# Tool definitions
TOOLS = [
    Tool(
        name="etspi_get_listing_inventory",
        description=(
            "Get inventory details for a listing including variants, SKUs, prices, and quantities. "
            "Can transform response to update format for easy modification. "
            "Supports JMESPath queries for filtering."
        ),
        inputSchema=GetListingInventoryParams.model_json_schema()
    ),
    Tool(
        name="etspi_update_listing_inventory",
        description=(
            "Update inventory for a listing including products, pricing, quantities, and SKUs. "
            "The inventory_data should include products array with offerings, "
            "and optional price_on_property, quantity_on_property, sku_on_property arrays."
        ),
        inputSchema=UpdateListingInventoryParams.model_json_schema()
    )
]


async def handle_get_listing_inventory(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_get_listing_inventory tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = GetListingInventoryParams(**arguments)

    try:
        # Get listing inventory
        result = etsy_api.get_listing_inventory(listing_id=params.listing_id)

        # Transform format if requested
        if params.format_as_update:
            update_request = UpdateListingInventoryRequest(result)
            result = update_request.get_dict()

        # Apply JMESPath query if provided
        if params.query:
            result = apply_jmespath_query(result, params.query)

        response = format_success_response(result)

        return [TextContent(
            type="text",
            text=to_json_string(response)
        )]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(
            type="text",
            text=to_json_string(response)
        )]


async def handle_update_listing_inventory(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_update_listing_inventory tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = UpdateListingInventoryParams(**arguments)

    try:
        # Create inventory update request object
        inventory_request = UpdateListingInventoryRequest(params.inventory_data)

        # Update listing inventory
        # Note: The EtsyAPI update_listing_inventory method needs shop_id
        # We'll need to get it from the listing first
        listing = etsy_api.get_listing(listing_id=params.listing_id)
        shop_id = listing.get('shop_id')

        if not shop_id:
            raise ValueError("Unable to determine shop_id for listing")

        result = etsy_api.update_listing_inventory(
            shop_id=shop_id,
            listing_id=params.listing_id,
            inventory=inventory_request
        )

        response = format_success_response(result)

        return [TextContent(
            type="text",
            text=to_json_string(response)
        )]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(
            type="text",
            text=to_json_string(response)
        )]


# Tool call router
async def handle_tool_call(tool_name: str, etsy_api, arguments: dict) -> list:
    """
    Route tool calls to appropriate handler

    Args:
        tool_name: Name of tool being called
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    if tool_name == "etspi_get_listing_inventory":
        return await handle_get_listing_inventory(etsy_api, arguments)
    elif tool_name == "etspi_update_listing_inventory":
        return await handle_update_listing_inventory(etsy_api, arguments)

    return [TextContent(
        type="text",
        text=to_json_string(format_error_response(
            ValueError(f"Unknown tool: {tool_name}")
        ))
    )]
