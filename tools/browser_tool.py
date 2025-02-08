import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from dotenv import load_dotenv
from pydantic import SecretStr
import os
# load_dotenv()
# api_key = os.getenv('GEMINI_API_KEY')
# if not api_key:
# 	raise ValueError('GEMINI_API_KEY is not set')

# llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(api_key))

@tool
def when_no_api_search_like_human(message: str):
    """
    Teaches how to do something visually using the internet on a browser.
    
    Great for when you want to find something but there is no API for it.
    Also great for when user doesn't know something but you can teach them how to do it visually.
    """
    async def async_tool_logic():
        llm = ChatOpenAI(model="gpt-4o-mini")
        browser = Browser(
                config=BrowserConfig(
                    headless=False,
		            # chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                    new_context_config=BrowserContextConfig(save_downloads_path=os.path.join(os.path.expanduser('~'), 'downloads'))
                )
            )

        browse_agent = Agent(
            task=message,
            llm=llm,
            browser=browser
        )
        
        result = await browse_agent.run()
        return result

    # Run the async logic in a synchronous context
    return asyncio.run(async_tool_logic())
