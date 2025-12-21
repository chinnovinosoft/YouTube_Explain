import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
import os 
os.environ["OPENAI_API_KEY"] = ""  

async def main():
    # MCP Client Configuration
    client = MultiServerMCPClient(
        {
            "customer-postgres-mcp": {
                "transport": "stdio",
                "command": "python",
                "args": [
                    "/Users/praveenreddy/Youtube_Repo/YouTube_Explain/MCP_LangGraph/MCP_Server/server_qs.py"
                ],
            }
        }
    )

    tools = await client.get_tools()
    print("=== Tools from MCP ===",tools)

    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0
    )

    agent = create_agent(
        model=llm,
        tools=tools
    )

    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Get customer details for customer id 1"
                }
            ]
        }
    )

    print("\n=== MCP + OpenAI Response ===")
    # print(response)
    for msg in response["messages"]:
        if isinstance(msg, AIMessage):
            final_ai_message = msg.content

    print(final_ai_message)

if __name__ == "__main__":
    asyncio.run(main())
