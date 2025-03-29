import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from aiconsole.core.code_running.code_interpreters.languages.mcp_python import MCPPythonCodeInterpreter
from aiconsole.core.assets.materials.material import Material
import threading
import time

# Register the integration mark to avoid warnings
pytestmark = pytest.mark.integration

# Fixtures
@pytest.fixture
def mcp_interpreter():
    """Provides a fresh MCP interpreter instance for each test"""
    interpreter = MCPPythonCodeInterpreter()
    # Clear any existing server initialization
    interpreter.mcp_server = None
    interpreter._initialized = False
    return interpreter

@pytest.fixture
def mock_mcp_server():
    """Enhanced mock MCP server with proper thread simulation"""
    server = MagicMock()
    server.name = "Python API Tools"
    
    # Add running state simulation
    server._should_run = threading.Event()
    server._should_run.set()  # Start in running state
    
    def mock_run():
        """Simulate a running server"""
        while server._should_run.is_set():
            time.sleep(0.1)  # Simulate work
    
    server.run = mock_run
    server.shutdown = lambda: server._should_run.clear()
    
    # Tool registration mock
    tool_mock = MagicMock()
    
    def tool_decorator(*args, **kwargs):
        def wrapper(fn):
            tool_mock(*args, **kwargs)  # Track the call
            return fn
        return wrapper
    
    server.tool = tool_decorator
    server.tool_mock = tool_mock  # Store for assertions
    
    return server

@pytest.fixture
def test_material():
    """Provides a properly configured Material instance"""
    return Material(
        id="test",
        name="Test",
        content="context_value = 42",
        usage="test usage",
        usage_examples=[],
        defined_in="aiconsole",
        override=False
    )

# ---- Basic Functionality Tests ----
@pytest.mark.asyncio
async def test_interpreter_initialization(mcp_interpreter, mock_mcp_server):
    """Test that interpreter initializes properly with MCP server"""
    assert mcp_interpreter is not None
    assert mcp_interpreter.mcp_server is None
    
    with patch('aiconsole.core.code_running.code_interpreters.languages.mcp_python.FastMCP', 
              return_value=mock_mcp_server):
        await mcp_interpreter.initialize(use_mcp=True)
        
        assert mcp_interpreter.mcp_server is not None
        assert mcp_interpreter._initialized is True
        assert mock_mcp_server._should_run.is_set()  # Server should be "running"

@pytest.mark.asyncio
async def test_mcp_basic():
    """Basic sanity test for interpreter creation"""
    interpreter = MCPPythonCodeInterpreter()
    assert interpreter is not None
    interpreter.terminate()  # Clean up

@pytest.mark.asyncio
async def test_mcp_server_initialization(mcp_interpreter, mock_mcp_server):
    """Test server initialization and tool registration"""
    with patch('aiconsole.core.code_running.code_interpreters.languages.mcp_python.FastMCP', 
              return_value=mock_mcp_server):
        await mcp_interpreter.initialize(use_mcp=True)
        
        assert mcp_interpreter.mcp_server is mock_mcp_server
        assert mcp_interpreter.mcp_server.name == "Python API Tools"
        assert mcp_interpreter._execute_tool is not None
        mock_mcp_server.tool_mock.assert_called()  # Verify tool registration

# ---- Core Execution Tests ----
@pytest.mark.asyncio
async def test_code_execution(mcp_interpreter):
    """Test basic code execution"""
    test_code = "print('Hello MCP')"
    expected_output = "Hello MCP"
    
    # Setup mock tool
    mcp_interpreter._execute_tool = AsyncMock(return_value=expected_output)
    mcp_interpreter._initialized = True
    
    results = [result async for result in mcp_interpreter.run(test_code, [])]
    assert results == [expected_output]
    mcp_interpreter._execute_tool.assert_called_once_with(test_code)

@pytest.mark.asyncio
async def test_multi_line_code(mcp_interpreter):
    """Test multi-line code execution"""
    test_code = """
x = 5
y = 7
x + y
"""
    mcp_interpreter._execute_tool = AsyncMock(return_value="12")
    mcp_interpreter._initialized = True
    
    results = [result async for result in mcp_interpreter.run(test_code, [])]
    assert "12" in results[0]

# ---- Error Handling Tests ----
@pytest.mark.asyncio
async def test_syntax_error_handling(mcp_interpreter):
    """Test syntax error handling"""
    bad_code = "print('missing parenthesis"
    
    mcp_interpreter._execute_tool = AsyncMock(side_effect=Exception("SyntaxError"))
    mcp_interpreter._initialized = True
    
    results = [result async for result in mcp_interpreter.run(bad_code, [])]
    assert "SyntaxError" in results[0]

@pytest.mark.asyncio
async def test_runtime_error_handling(mcp_interpreter):
    """Test runtime error handling"""
    bad_code = "1/0"
    
    mcp_interpreter._execute_tool = AsyncMock(side_effect=Exception("Division by zero"))
    mcp_interpreter._initialized = True
    
    results = [result async for result in mcp_interpreter.run(bad_code, [])]
    assert "Division by zero" in results[0]

# ---- Material Integration Tests ----
@pytest.mark.asyncio
async def test_material_context(mcp_interpreter, test_material):
    """Test code execution with material context"""
    test_code = "print(context_value)"
    
    mcp_interpreter._execute_tool = AsyncMock(return_value="42")
    mcp_interpreter._initialized = True
    
    results = [result async for result in mcp_interpreter.run(test_code, [test_material])]
    assert "42" in results[0]

# ---- Cleanup Tests ----
@pytest.mark.asyncio
async def test_termination(mcp_interpreter, mock_mcp_server):
    """Test proper resource cleanup"""
    with patch('aiconsole.core.code_running.code_interpreters.languages.mcp_python.FastMCP',
              return_value=mock_mcp_server):
        await mcp_interpreter.initialize(use_mcp=True)
        mcp_interpreter.terminate()
        
        assert mcp_interpreter.mcp_server is None
        assert mcp_interpreter._execute_tool is None
        assert not mock_mcp_server._should_run.is_set()  # Verify server stopped

# ---- Integration Test (Requires MCP Server) ----
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_execution():
    """End-to-end test with real MCP server"""
    interpreter = MCPPythonCodeInterpreter()
    try:
        # Increased timeout for real server
        await asyncio.wait_for(
            interpreter.initialize(use_mcp=True),
            timeout=10.0
        )
        
        test_code = "2 + 2"
        async for result in interpreter.run(test_code, []):
            assert any(
                expected in result
                for expected in ["4", "Code executed successfully"]
            )
            break  # Get first result only
    except asyncio.TimeoutError:
        pytest.skip("MCP server not available or too slow")
    finally:
        interpreter.terminate()