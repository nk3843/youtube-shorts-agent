import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.adk.tools import FunctionTool

# Path to the server script
SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_server.py")

async def _run_mcp_tool(tool_name: str, arguments: dict):
    """
    Connects to the MCP server and runs a specific tool.
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
        env=os.environ.copy() # Pass current env to get PATH/Vars
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools to verify (optional, specific to debug)
            # tools = await session.list_tools()
            
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

async def get_google_trends_data(topic: str = "united_states", query_type: str = "trending") -> str:
    """
    Access Google Trends data to find viral topics.
    
    Args:
        topic: The region (e.g. 'united_states') if query_type is 'trending', 
               OR the keyword (e.g. 'Minecraft') if query_type is 'related' or 'interest'.
        query_type: One of 'trending' (daily trends), 'related' (related queries), or 'interest' (interest over time).
    
    Returns:
        The requested trends data as a string.
    """
    tool_map = {
        "trending": "get_trending_searches",
        "related": "get_related_queries",
        "interest": "get_interest_over_time"
    }
    
    if query_type not in tool_map:
        return "Error: Invalid query_type. Must be 'trending', 'related', or 'interest'."
        
    mcp_tool_name = tool_map[query_type]
    
    # Map arguments for the specific tool
    args = {}
    if query_type == "trending":
        args = {"region": topic}
    elif query_type == "interest":
        args = {"keywords": [topic]}
    elif query_type == "related":
        args = {"keyword": topic}
        
    try:
        # Await the async function directly
        return await _run_mcp_tool(mcp_tool_name, args)
    except Exception as e:
        return f"Error communicating with Trends MCP: {str(e)}"

# Define the tool for ADK
trends_tool = FunctionTool(get_google_trends_data)
