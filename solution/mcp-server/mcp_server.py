import os
from typing import Any
import logging
import traceback
from functools import partial

from fastmcp import FastMCP
from mangum import Mangum
import requests

from .tools import register_search_tools


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def call_eregs_api(endpoint: str, auth: str = None, params: dict = None, method: callable = requests.get) -> dict:
    api = os.environ.get("EREGS_API_URL_V3")
    if not api:
        logger.error("EREGS_API_URL_V3 environment variable is not set")
        raise Exception("EREGS_API_URL_V3 environment variable is not set")
    headers = {"Authorization": auth} if auth else {}
    response = method(f"{api}{endpoint}", headers=headers, params=params)
    if response.status_code != 200:
        logger.error(f"Error calling eRegs API at endpoint {endpoint}: {response.status_code} - {response.text}")
        raise Exception(f"Failed to call eRegs API at endpoint {endpoint}")
    return response.json()


def create_app(auth):
    mcp = FastMCP(name="eregs-mcp-server")
    mcp_app = mcp.http_app(stateless_http=True)
    call_eregs = partial(call_eregs_api, auth=auth)

    register_search_tools(mcp, call_eregs)

    @mcp.tool
    async def hello_world(name: str) -> str:
        """
        A simple tool that returns a greeting message.
        
        Args:
            name (str): The name of the person to greet.
        Returns:
            str: A greeting message.
        """
        return f"Hello, {name}!"

    @mcp.tool
    async def list_titles() -> list[int]:
        """
        A simple tool that returns a list of titles contained in eRegs.
        
        Returns:
            list[int]: A list of titles as integers.
        """
        data = call_eregs("titles")
        return [item["number"] for item in data.get("results", [])]

    
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
