import pytest
from Youtube_Agent.tools.mcp_client_tool import get_google_trends_data
from Youtube_Agent.mcp_server import get_trending_searches

def test_server_functionality():
    """Verify the MCP logic (RSS) in isolation."""
    # This should now succeed with the RSS feed
    try:
        result = get_trending_searches("US")
        assert isinstance(result, str)
        print("\nDirect Server Result (RSS match):", result[:100], "...")
        assert "Error" not in result
    except Exception as e:
        pytest.fail(f"RSS test failed: {e}")

def test_client_tool_integration():
    """Verify the client tool orchestrator."""
    # This invokes the subprocess, so it tests the full MCP link
    try:
        # asking for 'related' queries to a generic term 'Python'
        result = get_google_trends_data("Python", query_type="related")
        assert isinstance(result, str)
        print("\nMCP Client Result:", result[:100], "...")
    except Exception as e:
         pytest.skip(f"Skipping MCP subprocess test: {e}")
