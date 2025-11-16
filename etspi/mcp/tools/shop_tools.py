"""
Shop discovery and search tools for ETSPI MCP server
"""
from mcp.types import Tool, TextContent
from ..schemas import GetShopParams, FindShopListingsParams
from ..utils import (
    apply_jmespath_query,
    format_success_response,
    format_error_response,
    to_json_string,
    build_include_list
)


# Tool definitions
TOOLS = [
    Tool(
        name="etspi_get_shop",
        description=(
            "Get information about an Etsy shop. "
            "Can retrieve shop by ID, find shops by user ID, or search shops by name. "
            "Provide one of: shop_id, user_id, or shop_name."
        ),
        inputSchema=GetShopParams.model_json_schema()
    ),
    Tool(
        name="etspi_find_shop_listings",
        description=(
            "Search and filter listings within a specific Etsy shop. "
            "Supports filtering by section, state, keywords, and sorting. "
            "Can include additional data like images, inventory, shipping info, etc."
        ),
        inputSchema=FindShopListingsParams.model_json_schema()
    )
]


async def handle_get_shop(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_get_shop tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = GetShopParams(**arguments)

    try:
        result = None

        if params.shop_id:
            # Get specific shop by ID
            result = etsy_api.get_shop(shop_id=params.shop_id)

        elif params.user_id:
            # Get shops for a user
            result = etsy_api.get_user_shops(user_id=params.user_id)

        elif params.shop_name:
            # Search shops by name
            result = etsy_api.find_shops(
                keywords=params.shop_name,
                limit=params.limit,
                offset=params.offset
            )

        else:
            raise ValueError("Must provide one of: shop_id, user_id, or shop_name")

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


async def handle_find_shop_listings(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_find_shop_listings tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = FindShopListingsParams(**arguments)

    try:
        # Validate and prepare includes
        includes = build_include_list(params.include)

        # Determine which API method to use based on parameters
        if params.section_id:
            # Search by section
            result = etsy_api.get_listings_by_shop_section_id(
                shop_id=params.shop_id,
                shop_section_id=params.section_id,
                limit=params.limit,
                offset=params.offset,
                sort_on=params.sort_on,
                sort_order=params.sort_order
            )

        elif params.keywords:
            # Search by keywords
            result = etsy_api.find_all_active_listings_by_shop(
                shop_id=params.shop_id,
                limit=params.limit,
                sort_on=params.sort_on,
                sort_order=params.sort_order,
                offset=params.offset,
                keywords=params.keywords
            )

        else:
            # Get all listings with optional state filter
            result = etsy_api.get_listings_by_shop(
                shop_id=params.shop_id,
                state=params.state,
                limit=params.limit,
                offset=params.offset,
                sort_on=params.sort_on,
                sort_order=params.sort_order,
                includes=includes
            )

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
    if tool_name == "etspi_get_shop":
        return await handle_get_shop(etsy_api, arguments)
    elif tool_name == "etspi_find_shop_listings":
        return await handle_find_shop_listings(etsy_api, arguments)

    return [TextContent(
        type="text",
        text=to_json_string(format_error_response(
            ValueError(f"Unknown tool: {tool_name}")
        ))
    )]
