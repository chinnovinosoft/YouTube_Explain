import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import traceback
from anthropic import Anthropic
from dotenv import load_dotenv

#to load values/secrets from .env file
load_dotenv() 

class MCPClient:
    def __init__(self):
        # client session to communicate with the server --> Why we need session is, 
        # Without a session, the client would have to create a new connection for every request
        self.session: Optional[ClientSession] = None
        # The AsyncExitStack helps manage async resources (like database connections, network sessions, 
        # or file handlers) by ensuring they are properly opened and closed.
        # It automatically cleans up resources when they are no longer needed.
        # Even if an error occurs, it ensures proper resource cleanup to prevent leaks.
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        
        command = "python"
        # helps to start the server by specifying the command
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        # It starts the server, sets up communication streams (IO), and creates a session to talk to the server.
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        print("Entered Processed Query")
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        response = await self.session.list_tools()

        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        print("Intital Claude response --> ",response)

        # Process response and handle tool calls
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    # async and await handle tasks that take time, like reading files, making network requests,
    # or communicating with a server, without blocking the rest of the program.
    # async makes a function run in the background without stopping the main program.
    # await tells Python to wait for a slow task to finish before moving to the next step.

    await client.connect_to_server(sys.argv[1])
    await client.chat_loop()

if __name__ == "__main__":
    import sys
    # asyncio is a Python library that allows your program to run multiple tasks at the same time without
    # waiting for one task to finish before starting another.
    # Instead of waiting for one task to finish, it switches to another task if we have multiple tasks, making the program faster.
    asyncio.run(main())
