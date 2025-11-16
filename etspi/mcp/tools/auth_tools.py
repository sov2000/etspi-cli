"""
Authentication tools for ETSPI MCP server
"""
from mcp.types import Tool, TextContent
from ..schemas import GetUserInfoParams
from ..utils import apply_jmespath_query, format_success_response, format_error_response, to_json_string


# Tool definitions
TOOLS = [
    Tool(
        name="etspi_get_user_info",
        description=(
            "Get information about an Etsy user. "
            "If user_id is not provided, returns information about the authenticated user. "
            "Can be used to verify authentication status and get user details."
        ),
        inputSchema=GetUserInfoParams.model_json_schema()
    )
]


async def handle_get_user_info(etsy_api, arguments: dict) -> list:
    """
    Handle etspi_get_user_info tool call

    Args:
        etsy_api: EtsyAPI instance
        arguments: Tool arguments

    Returns:
        List of TextContent responses
    """
    params = GetUserInfoParams(**arguments)

    try:
        # Get user info
        if params.user_id:
            result = etsy_api.get_user(user_id=params.user_id)
        else:
            result = etsy_api.get_authenticated_user()

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
    if tool_name == "etspi_get_user_info":
        return await handle_get_user_info(etsy_api, arguments)

    return [TextContent(
        type="text",
        text=to_json_string(format_error_response(
            ValueError(f"Unknown tool: {tool_name}")
        ))
    )]
