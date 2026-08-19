# eRegulations MCP Server

This service runs a FastMCP server in its own Lambda and exposes MCP tools that wrap eRegs APIs.

## What This Service Does

- Hosts an MCP server over HTTP (`FastMCP` + `Mangum`) in a Docker-based AWS Lambda.
- Forwards tool requests to eRegs v3 APIs using `EREGS_API_URL_V3`.
- Supports local development through `lambda-proxy` (`Dockerfile.local`) and Docker Compose.

Current tools:

- `hello_world(name)` -> returns a greeting string.
- `list_titles()` -> calls `/v3/titles` and returns title numbers.
- `search(...)` -> calls `/v3/content-search/` and returns normalized structured results.

## Code Layout

- `mcp_server.py`: Lambda handler, app creation, shared eRegs API call helper.
- `tools/search.py`: MCP `search` tool registration and result-shape normalization.
- `tools/utils.py`: utility helpers (currently HTML stripping).
- `Dockerfile`: production Lambda image.
- `Dockerfile.local`: local Lambda-proxy image for development.

## Runtime Configuration

Required env vars:

- `EREGS_API_URL_V3`: base URL for eRegs API v3 (must end with `/v3/`).

Optional/common:

- `LOG_LEVEL`: injected in deployed environments.

Auth behavior:

- The Lambda reads `Authorization` from inbound request headers and forwards it to eRegs API calls.
- Local development can hit a local eRegs stack without auth if eRegs is configured that way.

## Local Development

From `solution/`:

```bash
docker compose up -d --build mcp-server
```

Local MCP endpoint:

- `http://localhost:8002/mcp`

The compose service sets:

- `EREGS_API_URL_V3=http://host.docker.internal:8000/v3/`

so it can call the local Django service running on port `8000`.

## Manual Tool Testing (Python MCP Client)

From `solution/mcp-server/`:

```bash
uv sync
uv run python
```

In the Python shell:

```python
import asyncio
import fastmcp

async def async_call_func(func_name, *args, **kwargs):
    async with client:
        func = getattr(client, func_name)
        return await func(*args, **kwargs)

def call_func(func_name, *args, **kwargs):
    return asyncio.run(async_call_func(func_name, *args, **kwargs))

client = fastmcp.Client("http://localhost:8002/mcp")
call_func("list_tools")
call_func("call_tool", "hello_world", {"name": "You"})
call_func("call_tool", "list_titles")
call_func("call_tool", "search", {"query": "Medicaid"})
```

## Search Tool Contract

`search` accepts:

- `query` (required)
- `page` (default `1`)
- `page_size` (default `25`)
- `show_public` (default `True`)
- `show_regulations` (default `True`)
- `sort` (`relevance`, `date`, `-date`; default `relevance`)

Behavior notes:

- Internal documents are always excluded (`show_internal=False`).
- Returned headlines are cleaned of HTML tags before being returned to MCP clients.

## Deployment Notes

- The MCP server deploys as its own CDK stack (`McpServerStack`) with:
  - Docker Lambda (`solution/mcp-server/Dockerfile`)
  - API Gateway + WAF
  - Non-prod authorizer integration
- Deployed Lambda env includes `EREGS_API_URL_V3=<site-endpoint>v3/` so MCP tools call the matching environment's eRegs backend.

## Troubleshooting

- `EREGS_API_URL_V3 environment variable is not set`
  - Ensure the env var is defined in local compose or Lambda config.
- `Failed to call eRegs API at endpoint ...`
  - Verify the target eRegs service is reachable and auth headers are valid.
- MCP tool returns empty results
  - Confirm query/filter arguments and check whether target environment has indexed content.
