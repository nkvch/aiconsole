import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_log = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None

    async def connect_to_server(self, server_script_path: str):
        """Connect to the MCP server
        
        Args:
            server_script_path: Path to the server script
        """
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        _log.info("Connected to MCP server with tools: %s", [tool.name for tool in tools])

    async def execute_code(self, code: str, language: str = "python") -> str:
        """Execute code using the MCP server
        
        Args:
            code: The code to execute
            language: The programming language (default: python)
        """
        if not self.session:
            raise RuntimeError("MCP client not connected to server")
            
        if language == "python":
            result = await self.session.call_tool("execute_python_code", {"code": code, "language": language})
        elif language == "applescript":
            result = await self.session.call_tool("execute_applescript", {"code": code})
        else:
            raise ValueError(f"Unsupported language: {language}")
            
        return result.content

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

# Global MCP client instance
mcp_client = MCPClient()

async def initialize_mcp_client(server_script_path: str):
    """Initialize the global MCP client
    
    Args:
        server_script_path: Path to the MCP server script
    """
    await mcp_client.connect_to_server(server_script_path)

async def cleanup_mcp_client():
    """Clean up the global MCP client"""
    await mcp_client.cleanup() 