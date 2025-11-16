"""
Listing property management tools for ETSPI MCP server
"""
from mcp.types import Tool, TextContent
from ..schemas import GetListingPropertiesParams, UpdateListingPropertyParams
from ..utils import (
    apply_jmespath_query,
    format_success_response,
    format_error_response,
    to_json_string
)
from etspi.etsyv3.models import UpdateListingPropertyRequest


# Tool definitions
TOOLS = [
    Tool(
        name="etspi_get_listing_properties",
        description=(
            "Get custom properties for a listing. "
            "Properties are customizable attributes like size, color, material, etc. "
            "Can retrieve all properties or a specific property by ID. "
            "Supports transforming to update format and JMESPath queries."
        ),
        inputSchema=GetListingPropertiesParams.model_json_schema()
    ),
    Tool(
        name="etspi_update_listing_property",
        description=(
            "Update a specific listing property. "
            "The property_data should include value_ids, values, and/or scale_id. "
            "Used to modify customizable attributes of a listing."
        ),
        inputSchema=UpdateListingPropertyParams.model_json_schema()
    )
]


async def handle_get_listing_properties(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_get_listing_properties tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = GetListingPropertiesParams(**arguments)

    try:
        if params.property_id:
            # Get specific property
            result = etsy_api.get_listing_property(
                listing_id=params.listing_id,
                property_id=params.property_id
            )
        else:
            # Get all properties
            result = etsy_api.get_listing_properties(
                shop_id=params.shop_id,
                listing_id=params.listing_id
            )

        # Transform format if requested
        if params.format_as_update and params.property_id:
            update_request = UpdateListingPropertyRequest(result)
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


async def handle_update_listing_property(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_update_listing_property tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = UpdateListingPropertyParams(**arguments)

    try:
        # Create property update request object
        property_request = UpdateListingPropertyRequest(params.property_data)

        # Update property
        result = etsy_api.update_listing_property(
            shop_id=params.shop_id,
            listing_id=params.listing_id,
            property_id=params.property_id,
            property=property_request
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
    if tool_name == "etspi_get_listing_properties":
        return await handle_get_listing_properties(etsy_api, arguments)
    elif tool_name == "etspi_update_listing_property":
        return await handle_update_listing_property(etsy_api, arguments)

    return [TextContent(
        type="text",
        text=to_json_string(format_error_response(
            ValueError(f"Unknown tool: {tool_name}")
        ))
    )]
