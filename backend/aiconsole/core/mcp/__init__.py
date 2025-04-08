import asyncio
import os
from pathlib import Path

from aiconsole.core.mcp.client import initialize_mcp_client, cleanup_mcp_client

# Get the path to the MCP server script
SERVER_SCRIPT_PATH = str(Path(__file__).parent / "server.py")

async def initialize_mcp():
    """Initialize the MCP server and client"""
    await initialize_mcp_client(SERVER_SCRIPT_PATH)

async def cleanup_mcp():
    """Clean up the MCP server and client"""
    await cleanup_mcp_client() 