from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

async def main():
    client = MultiServerMCPClient(
        {
            "prompts": {
                "transport": "stdio",
                "command": "python",
                "args": ["/Users/praveenreddy/Youtube_Repo/YouTube_Explain/MCP_LangGraph/MCP_Server/server_prompts.py"],
            }
        }
    )

    messages = await client.get_prompt("prompts", "summarize")

    for msg in messages:
        print(f"{msg.type}: {msg.content}")
    
    #2nd
    messages = await client.get_prompt(
        "prompts",
        "code_review",
        arguments={
            "language": "python",
            "focus": "security"
        }
    )
    for msg in messages:
        print(f"{msg.type}: {msg.content}")
if __name__ == "__main__":
    asyncio.run(main())
