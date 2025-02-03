import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from browser_use import Agent

@tool
def when_no_api_search_like_human(message: str):
    """
    Finds information from the internet using a browser.
    
    Great for when you want to find something but there is no API.
    """
    async def async_tool_logic():
        llm = ChatOpenAI(model="gpt-4o-mini")
        browse_agent = Agent(
            task=message,
            llm=llm,
        )
        result = await browse_agent.run()
        return result

    # Run the async logic in a synchronous context
    return asyncio.run(async_tool_logic())
