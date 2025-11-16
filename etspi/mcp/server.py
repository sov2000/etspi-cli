"""
ETSPI MCP Server - Main entry point for Model Context Protocol server

This server exposes Etsy shop management functionality through MCP tools,
allowing LLMs and AI agents to interact with the Etsy API through natural language.
"""
import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from .auth import EtspiAuthManager, AuthenticationError
from .tools import ALL_TOOLS, handle_tool_call
from etspi.etsyv3.etsy_api import EtsyAPI


class EtspiMCPServer:
    """MCP Server for Etsy shop management"""

    def __init__(self):
        """Initialize the MCP server"""
        self.server = Server("etspi-mcp")
        self.auth_manager = None
        self.etsy_api = None

        # Initialize auth manager
        try:
            self.auth_manager = EtspiAuthManager()
        except AuthenticationError as ex:
            print(f"Authentication Error: {ex}", file=sys.stderr)
            print("\nPlease run 'etspi auth -tF' first to authenticate with Etsy.", file=sys.stderr)
            sys.exit(1)

        # Register MCP handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools():
            """Return list of available tools"""
            return ALL_TOOLS

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Handle tool calls"""
            # Ensure EtsyAPI is initialized
            etsy_api = self._get_etsy_api()

            # Route to appropriate tool handler
            return await handle_tool_call(name, etsy_api, arguments)

    def _get_etsy_api(self) -> EtsyAPI:
        """
        Get or create authenticated EtsyAPI instance

        Returns:
            EtsyAPI instance with current authentication

        Raises:
            AuthenticationError: If authentication config is invalid
        """
        if not self.etsy_api:
            auth_config = self.auth_manager.get_auth_config()

            self.etsy_api = EtsyAPI(
                keystring=auth_config['key'],
                token=auth_config['token'],
                refresh_token=auth_config['refresh_token'],
                expiry=auth_config['expiry'],
                token_saver=self._save_refreshed_tokens
            )

        return self.etsy_api

    def _save_refreshed_tokens(self, token: str, refresh_token: str, expiry: int):
        """
        Callback to persist refreshed tokens

        Called automatically by EtsyAPI when tokens are refreshed.

        Args:
            token: New access token
            refresh_token: New refresh token
            expiry: Token expiration timestamp
        """
        if self.auth_manager:
            self.auth_manager.save_tokens(token, refresh_token, expiry)

    async def run(self):
        """Run the MCP server using stdio transport"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """
    Entry point for MCP server

    This is called when running: etspi-mcp
    """
    try:
        server = EtspiMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nShutting down ETSPI MCP server...", file=sys.stderr)
        sys.exit(0)
    except Exception as ex:
        print(f"Fatal error: {ex}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
