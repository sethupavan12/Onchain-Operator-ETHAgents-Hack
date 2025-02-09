from pydantic import BaseModel, Field
from langchain_community.tools import DuckDuckGoSearchRun

class WebSearchInput(BaseModel):
    """Input argument schema for web search action."""
    query: str = Field(
        ...,
        description="The search query to look up",
        example="What is the capital of France?"
    )

WEB_SEARCH_PROMPT = """
This tool performs a web2 search using DuckDuckGo and returns relevant results.
Use this when you need to find current or factual information from the web.

Don't use this tool for anything about web3 like finding tokens etc.
Unless it is about finding some info about something that can be found easily.
Don't bother with this tool.

Example:
Input: {
    "query": "What is the capital of France?"
}
"""

def web_search_tool(query: str) -> str:
    """Perform a web search using DuckDuckGo.

    Args:
        query (str): The search query to look up.

    Returns:
        str: The search results.
    """
    try:
        search = DuckDuckGoSearchRun()
        result = search.invoke(query)
        return result
    except Exception as e:
        return f"Failed to perform web search: {str(e)}"