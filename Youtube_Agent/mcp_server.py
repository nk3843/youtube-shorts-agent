from mcp.server.fastmcp import FastMCP
from pytrends.request import TrendReq
import pandas as pd

# Initialize FastMCP server
mcp = FastMCP("GoogleTrends")

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

@mcp.tool()
def get_trending_searches(region: str = "US") -> str:
    """
    Get the daily trending searches for a specific region (using RSS).
    
    Args:
        region: The region code (e.g., 'US', 'IN'). Defaults to 'US'.
    
    Returns:
        A string representation of the top trending searches.
    """
    import requests
    import xml.etree.ElementTree as ET

    try:
        # Fallback map for full names if agent passes them
        region_map = {
            "united_states": "US",
            "united_kingdom": "GB",
            "india": "IN"
        }
        geo = region_map.get(region.lower(), region.upper())
        
        url = f"https://trends.google.com/trending/rss?geo={geo}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Error fetching RSS feed. Status: {response.status_code}"
            
        root = ET.fromstring(response.content)
        items = root.findall(".//item")
        
        if not items:
            return "No trending items found in RSS feed."
            
        results = []
        for i, item in enumerate(items[:10]):
            title = item.find("title").text
            results.append(f"{i+1}. {title}")
            
        return "\n".join(results)

    except Exception as e:
        return f"Error fetching trending searches via RSS: {str(e)}"

@mcp.tool()
def get_interest_over_time(keywords: list[str]) -> str:
    """
    Get interest over time for a list of keywords.
    
    Args:
        keywords: A list of keywords to check (max 5).
        
    Returns:
        A summary of the interest over time.
    """
    try:
        if len(keywords) > 5:
            return "Error: You can only compare up to 5 keywords at a time."
            
        pytrends.build_payload(keywords, cat=0, timeframe='today 12-m', geo='', gprop='')
        data = pytrends.interest_over_time()
        
        if data.empty:
            return "No data found for these keywords."
            
        # Return the last 5 rows to show recent trend
        return data.tail(5).to_string()
    except Exception as e:
        return f"Error fetching interest over time: {str(e)}"

@mcp.tool()
def get_related_queries(keyword: str) -> str:
    """
    Get related queries for a specific keyword.
    
    Args:
        keyword: The keyword to find related queries for.
        
    Returns:
        A list of rising related queries.
    """
    try:
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
        related = pytrends.related_queries()
        
        if not related or keyword not in related or related[keyword]['rising'] is None:
            return f"No related queries found for '{keyword}'."
            
        # Return top 10 rising queries
        return related[keyword]['rising'].head(10).to_string(index=False)
    except Exception as e:
        return f"Error fetching related queries: {str(e)}"

if __name__ == "__main__":
    mcp.run()
