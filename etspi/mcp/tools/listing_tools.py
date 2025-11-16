"""
Listing management tools for ETSPI MCP server
"""
from mcp.types import Tool, TextContent
from ..schemas import (
    GetListingParams,
    CreateDraftListingParams,
    UpdateListingParams,
    DeleteListingParams
)
from ..utils import (
    apply_jmespath_query,
    format_success_response,
    format_error_response,
    to_json_string,
    build_include_list
)
from etspi.etsyv3.models import CreateDraftListingRequest, UpdateListingRequest


# Tool definitions
TOOLS = [
    Tool(
        name="etspi_get_listing",
        description=(
            "Retrieve detailed information about a specific Etsy listing by ID. "
            "Can optionally include related data like images, shipping info, inventory, videos, etc. "
            "Supports transforming to draft or update format for easy modification. "
            "Supports JMESPath queries for response filtering."
        ),
        inputSchema=GetListingParams.model_json_schema()
    ),
    Tool(
        name="etspi_create_draft_listing",
        description=(
            "Create a new draft listing in an Etsy shop. "
            "The listing_data must contain required fields: quantity, title, description, price, "
            "who_made, when_made, taxonomy_id. Returns the created listing details."
        ),
        inputSchema=CreateDraftListingParams.model_json_schema()
    ),
    Tool(
        name="etspi_update_listing",
        description=(
            "Update an existing Etsy listing. "
            "Provide only the fields you want to update in listing_data. "
            "Returns the updated listing details."
        ),
        inputSchema=UpdateListingParams.model_json_schema()
    ),
    Tool(
        name="etspi_delete_listing",
        description=(
            "Delete an Etsy listing permanently. "
            "This action cannot be undone. Set confirm=true to skip confirmation."
        ),
        inputSchema=DeleteListingParams.model_json_schema()
    )
]


async def handle_get_listing(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_get_listing tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = GetListingParams(**arguments)

    try:
        # Validate and prepare includes
        includes = build_include_list(params.include)

        # Get listing
        result = etsy_api.get_listing(
            listing_id=params.listing_id,
            includes=includes
        )

        # Transform format if requested
        if params.format_as_draft:
            draft_request = CreateDraftListingRequest(result)
            result = draft_request.get_dict()
        elif params.format_as_update:
            update_request = UpdateListingRequest(result)
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


async def handle_create_draft_listing(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_create_draft_listing tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = CreateDraftListingParams(**arguments)

    try:
        # Create listing request object
        listing_request = CreateDraftListingRequest(params.listing_data)

        # Create draft listing
        result = etsy_api.create_draft_listing(
            shop_id=params.shop_id,
            listing=listing_request
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


async def handle_update_listing(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_update_listing tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = UpdateListingParams(**arguments)

    try:
        # Create update request object
        update_request = UpdateListingRequest(params.listing_data)

        # Update listing
        result = etsy_api.update_listing(
            shop_id=params.shop_id,
            listing_id=params.listing_id,
            listing=update_request
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


async def handle_delete_listing(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_delete_listing tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = DeleteListingParams(**arguments)

    try:
        if not params.confirm:
            return [TextContent(
                type="text",
                text=to_json_string({
                    "success": False,
                    "error": {
                        "type": "ConfirmationRequired",
                        "message": "Please set confirm=true to delete this listing. This action cannot be undone."
                    }
                })
            )]

        # Delete listing
        result = etsy_api.delete_listing(listing_id=params.listing_id)

        response = format_success_response({
            "listing_id": params.listing_id,
            "deleted": True,
            "message": "Listing deleted successfully"
        })

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
    if tool_name == "etspi_get_listing":
        return await handle_get_listing(etsy_api, arguments)
    elif tool_name == "etspi_create_draft_listing":
        return await handle_create_draft_listing(etsy_api, arguments)
    elif tool_name == "etspi_update_listing":
        return await handle_update_listing(etsy_api, arguments)
    elif tool_name == "etspi_delete_listing":
        return await handle_delete_listing(etsy_api, arguments)

    return [TextContent(
        type="text",
        text=to_json_string(format_error_response(
            ValueError(f"Unknown tool: {tool_name}")
        ))
    )]
