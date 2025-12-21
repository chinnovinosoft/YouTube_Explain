from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

async def main():
    client = MultiServerMCPClient(
        {
            "docs": {
                "transport": "stdio",
                "command": "python",
                "args": ["/Users/praveenreddy/Youtube_Repo/YouTube_Explain/MCP_LangGraph/MCP_Server/server_resources.py"], 
            }
        }
    )

    blobs = await client.get_resources(
        "docs",
        uris=["file://docs/leave_policy.txt"]
    )
    # print("=== Retrieved Blobs ===",blobs)

    for blob in blobs:
        print("URI:", blob.metadata["uri"])
        print("MIME:", blob.mimetype)
        print(blob.as_string())

if __name__ == "__main__":
    asyncio.run(main())
