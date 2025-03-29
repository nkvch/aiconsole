from mcp.server.fastmcp import FastMCP
import asyncio
from typing import AsyncGenerator, Optional
from aiconsole.core.assets.materials.material import Material
import threading

class MCPPythonCodeInterpreter:
    def __init__(self):
        self.mcp_server: Optional[FastMCP] = None
        self._execute_tool = None
        self._initialized = False
        self._server_thread: Optional[threading.Thread] = None  # Track server thread
        self._server_stop_event = threading.Event()  # For graceful shutdown

    async def initialize(self, use_mcp: bool = False) -> None:
        """Initialize the MCP server if enabled"""
        if use_mcp and not self._initialized:
            self._setup_mcp_server()
            await self._start_mcp_server()
            self._initialized = True

    async def run(self, code: str, materials: list[Material]) -> AsyncGenerator[str, None]:
        """Execute code through MCP and yield results"""
        if not self._execute_tool:
            raise RuntimeError("MCP tool not initialized - call initialize(use_mcp=True) first")

        try:
            result = await self._execute_tool(code)
            yield result
        except Exception as e:
            yield f"MCP Execution Error: {str(e)}"

    def terminate(self) -> None:
        """Clean up MCP server resources"""
        if self._server_thread and self._server_thread.is_alive():
            self._server_stop_event.set()  # Signal shutdown
            self._server_thread.join(timeout=1.0)  # Wait briefly
            
            if self._server_thread.is_alive():
                # Force termination if graceful shutdown failed
                self._server_thread = None

        if self.mcp_server and hasattr(self.mcp_server, 'shutdown'):
            self.mcp_server.shutdown()
            
        self.mcp_server = None
        self._execute_tool = None
        self._initialized = False
        self._server_stop_event.clear()

    def _setup_mcp_server(self):
        """Initialize the MCP server and register tools"""
        self.mcp_server = FastMCP("Python API Tools")
        
        @self.mcp_server.tool()
        async def execute_python(code: str) -> str:
            try:
                exec_locals = {}
                exec(code, {'__builtins__': __builtins__}, exec_locals)
                return str(exec_locals.get('result', "Code executed successfully"))
            except Exception as e:
                return f"Execution Error: {str(e)}"
        
        self._execute_tool = execute_python

    async def _start_mcp_server(self):
        """Start the MCP server with proper thread management"""
        if not self.mcp_server:
            return

        try:
            if asyncio.iscoroutinefunction(self.mcp_server.run):
                await self.mcp_server.run()
            else:
                # Modified thread handling
                def run_server():
                    try:
                        self.mcp_server.run()
                    except Exception as e:
                        print(f"Server error: {str(e)}")
                    finally:
                        self._server_stop_event.set()

                self._server_thread = threading.Thread(
                    target=run_server,
                    daemon=True  # Critical for test cleanup
                )
                self._server_thread.start()
                
                # Wait briefly to confirm server started
                await asyncio.sleep(0.1)
                if not self._server_thread.is_alive():
                    raise RuntimeError("Server thread failed to start")

        except Exception as e:
            self.terminate()
            raise RuntimeError(f"Server startup failed: {str(e)}")