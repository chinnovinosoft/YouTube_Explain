import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult


async def on_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
    print("\n" + params.message)
    choice = input("\nType yes or no: ").strip().lower()

    if choice == "yes":
        return ElicitResult(
            action="accept",
            content={"confirm": True},
        )

    if choice == "no":
        return ElicitResult(action="decline")

    return ElicitResult(action="cancel")


async def main():
    client = MultiServerMCPClient(
        {
            "customer": {
                "transport": "stdio",
                "command": "python",
                "args": ["/Users/praveenreddy/Youtube_Repo/YouTube_Explain/MCP_LangGraph/MCP_Server/server_elicitation.py"],
            }
        },
        callbacks=Callbacks(on_elicitation=on_elicitation),
    )

    tools = await client.get_tools()
    print("=== Tools from MCP ===",tools)
    response  = await tools[0].ainvoke(
        {
            "id": 100,
            "name": "Praveen",
            "city": "Hyderabad",
            "dob": "1996-04-12",
            "designation": "AI Engineer",
        }
    )

    print("\nRESULT:", response)

if __name__ == "__main__":
    asyncio.run(main())
