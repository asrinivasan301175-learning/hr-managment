from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

MCP_URL = "http://127.0.0.1:8001/mcp"


async def call_mcp_tool(
    tool_name: str,
    arguments: dict,
):
    async with streamable_http_client(MCP_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            if result.isError:
                raise RuntimeError(
                    f"MCP tool failed: {result.content}"
                )

            return [
                item.text
                if hasattr(item, "text")
                else str(item)
                for item in result.content
            ]
