import os
from typing import Any
import logging
import traceback

from fastmcp import FastMCP
from mangum import Mangum
import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_app(auth):
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

    @mcp.tool
    async def list_titles() -> list[int]:
        """
        A simple tool that returns a list of titles contained in eRegs.
        
        Returns:
            list[int]: A list of titles as integers.
        """
        logger.error("====== list_titles tool called ======")
        api = os.environ.get("EREGS_API_URL_V3")
        if not api:
            logger.error("EREGS_API_URL_V3 environment variable is not set")
            raise Exception("EREGS_API_URL_V3 environment variable is not set")
        headers = {"Authorization": auth} if auth else {}
        response = requests.get(f"{api}titles", headers=headers)
        if response.status_code != 200:
            logger.error(f"Error fetching titles: {response.status_code} - {response.text}")
            raise Exception("Failed to fetch titles from eRegs API")
        return response.json()
    
    return mcp_app


def handler(event: dict, context: Any) -> Any:
    try:
        headers = event.get("headers", {})
        auth = headers.get("Authorization") or headers.get("authorization")
        app = create_app(auth)
        asgi_handler = Mangum(app, lifespan="on")
        return asgi_handler(event, context)
    except Exception as e:
        logger.error(f"Error in handler: {e}")
        logger.error(traceback.format_exc())
        raise
