import asyncio
import httpx

from a2a.client import (
    A2ACardResolver,
    Client,
    ClientConfig,
    ClientFactory,
    create_text_message_object,
)

from a2a.types import TransportProtocol
from a2a.utils.message import get_message_text


SERVER_URL = "http://localhost:9999"


def print_welcome_message():
    print("Travel Planner Client")
    print("Type a request like:")
    print("book flight from Hyderabad to Goa")
    print("book hotel in Goa")
    print("book cab in Goa")
    print("Type 'exit' to quit")


def get_user_query():
    return input("\n> ")


async def interact_with_server(client: Client):

    while True:

        # getting user input
        user_input = get_user_query()

        if user_input.lower() == "exit":
            print("bye!")
            break

        try:
            # creating a message object with the user input to send to the server. A2A server expects the message to be in a specific message format.
            request = create_text_message_object(content=user_input)

            async for response in client.send_message(request):
                task, _ = response

                print(get_message_text(task.artifacts[-1]))

        except Exception as e:
            print("Error:", e)


async def main():

    print_welcome_message()

    #asynchronous client connection to interact with server
    async with httpx.AsyncClient() as httpx_client:

        # creating a resolver to fetch the agent card from the server
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=SERVER_URL
        )

        try:
            agent_card = await resolver.get_agent_card()
            print("agent_card : ",agent_card) 
            
            # configuring the client connection with the fetched AgentCard and supported transports protocols (HTTP JSON and JSON-RPC in this case)
            config = ClientConfig(
                httpx_client=httpx_client,
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json
                ],
                # we are fetching the response in a streaming manner
                streaming=agent_card.capabilities.streaming,
            )
            # creating the client with the above configuration and fetched agent card
            client = ClientFactory(config).create(agent_card)

        except Exception as e:
            print("Error initializing client:", e)
            return

        await interact_with_server(client)


if __name__ == "__main__":
    asyncio.run(main())