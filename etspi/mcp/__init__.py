"""
ETSPI MCP Server

Model Context Protocol server for Etsy shop management.
Exposes etspi-cli functionality as MCP tools for AI assistants.
"""

__version__ = "1.1.0"

from .server import EtspiMCPServer, main

__all__ = ["EtspiMCPServer", "main"]
