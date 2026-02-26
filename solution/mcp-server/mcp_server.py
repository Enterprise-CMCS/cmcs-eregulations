from typing import Any
import logging
import traceback

from fastmcp import FastMCP
from mangum import Mangum


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_app():
    mcp = FastMCP(name="eregs-mcp-server")
    mcp_app = mcp.http_app(stateless_http=True)

    @mcp.tool
    async def hello_world(name: str) -> str:
        """
        A simple tool that returns a greeting message.
        
        Args:
            name (str): The name of the person to greet.
        Returns:
            str: A greeting message.
        """
        logger.error("====== hello_world tool called with name: %s ======", name)
        return f"Hello, {name}!"
    
    return mcp_app


def handler(event: dict, context: Any) -> Any:
    logger.error(f"Received event: {event}")
    try:
        app = create_app()
        asgi_handler = Mangum(app, lifespan="on")
        return asgi_handler(event, context)
    except Exception as e:
        logger.error(f"Error in handler: {e}")
        logger.error(traceback.format_exc())
        raise
