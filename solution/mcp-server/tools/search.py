from typing import Annotated, Literal
from pydantic import Field

from fastmcp import FastMCP
import requests

from .utils import remove_html


def register_search_tools(mcp: FastMCP, call_eregs: callable):
    @mcp.tool(output_schema={
        "type": "object",
        "properties": {
            "page": {"type": "integer"},
            "count": {"type": "integer"},
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "summary": {"type": "string"},
                        "content": {"type": "string"},
                        "type": {"type": "string", "enum": ["resource", "reg_text"]},
                        "resource": {
                            "type": ["object", "null"],
                            "properties": {
                                "type": {"type": "string"},
                                "category": {"type": ["string", "null"]},
                                "cfr_citations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "document_id": {"type": "string"},
                                "title": {"type": "string"},
                                "date": {"type": "string"},
                                "url": {"type": "string"},
                            },
                        },
                        "reg_text": {
                            "type": ["object", "null"],
                            "properties": {
                                "reg_title": {"type": "string"},
                                "part": {"type": ["string", "null"]},
                                "part_title": {"type": ["string", "null"]},
                                "subpart": {"type": ["string", "null"]},
                                "subpart_title": {"type": ["string", "null"]},
                                "type": {"type": ["string", "null"]},
                                "id": {"type": ["string", "null"]},
                                "title": {"type": ["string", "null"]},
                            },
                        },
                    },
                },
            },
        },
    })
    async def search(
        query: Annotated[str, Field(description="The search query string.")],
        page: Annotated[int, Field(description="The page number for paginated results.")] = 1,
        page_size: Annotated[int, Field(description="The number of results per page.")] = 25,
        show_public: Annotated[bool, Field(description="Whether to include public documents in the search results.")] = True,
        show_regulations: Annotated[bool, Field(description="Whether to include regulations in the search results.")] = True,
        sort: Annotated[
            Literal["relevance", "date", "-date"],
            Field(description="The sort order for the search results.")
        ] = "relevance",
    ) -> dict:
        """
        A tool that performs a search query against the eRegs API and returns the results.
        """

        data = call_eregs("content-search/", method=requests.post, params={
            "q": query,
            "page": page,
            "page_size": page_size,
            "show_public": show_public,
            "show_regulations": show_regulations,
            "show_internal": False,  # internal documents are not relevant for this tool
            "sort": sort,
        })

        results = []
        for i in data.get("results", []):
            result = {
                "name": remove_html(i.get("name_headline", "")),
                "summary": remove_html(i.get("summary_headline", "")),
                "content": remove_html(i.get("content_headline", "")),
                "type": "resource" if i.get("resource") else "reg_text",
                "resource": None,
                "reg_text": None,
            }
            if i.get("reg_text"):
                reg_text = i["reg_text"]
                result["reg_text"] = {
                    "reg_title": reg_text["title"],
                    "part": reg_text["part_number"],
                    "part_title": reg_text["part_title"],
                    "subpart": reg_text["subpart_id"],
                    "subpart_title": reg_text["subpart_title"],
                    "type": reg_text["node_type"],
                    "id": reg_text["node_id"],
                    "title": reg_text["node_title"],
                }
            elif i.get("resource"):
                resource = i["resource"]
                result["resource"] = {
                    "type": resource["type"],
                    "category": resource.get("category", {}).get("name"),
                    "cfr_citations": [
                        f"{c['title']} CFR {c['part']} " + \
                            (f"Subpart {c['subpart_id']} " if c.get("subpart_id") else "") + \
                            (f"Section {c['section_id']}" if c.get("section_id") else "")
                        for c in resource.get("cfr_citations", [])
                    ],
                    "document_id": resource["document_id"],
                    "title": resource["title"],
                    "date": resource["date"],
                    "url": resource["url"],
                }
            results.append(result)

        return {
            "page": page,
            "count": data.get("count", 0),
            "results": results,
        }
