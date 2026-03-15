from typing_extensions import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from dotenv import load_dotenv

load_dotenv() 

from a2a.utils import new_text_artifact

from agents import Runner

from agents_server.flight_agent import flight_agent
from agents_server.hotel_agent import hotel_agent
from agents_server.cab_agent import cab_agent


class TravelExecutor(AgentExecutor):

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue):

        if not context.message:
            raise Exception("No message provided")

        query = context.get_user_input().lower()

        if "flight" in query or "plain" in query:
            result = await Runner.run(flight_agent, input=query)

        elif "hotel" in query or "room" in query:
            result = await Runner.run(hotel_agent, input=query)

        elif "cab" in query or "car" in query:
            result = await Runner.run(cab_agent, input=query)

        else:
            response_text = "I can help with flight, hotel, or cab bookings."

            artifact = TaskArtifactUpdateEvent(
                context_id=context.context_id,
                task_id=context.task_id,
                artifact=new_text_artifact(
                    name="response",
                    text=response_text,
                ),
            )

            await event_queue.enqueue_event(artifact)

            status = TaskStatusUpdateEvent(
                context_id=context.context_id,
                task_id=context.task_id,
                status=TaskStatus(state=TaskState.completed),
                final=True,
            )

            await event_queue.enqueue_event(status)

            return

        # This block creates a response event that will be sent back to the client.
        artifact = TaskArtifactUpdateEvent(
            # Identifies the conversation context. Helps the system know which request this response belongs to.
            context_id=context.context_id,
            # Identifies the specific task being executed. Important when multiple tasks are running.
            task_id=context.task_id,
            artifact=new_text_artifact(
                name="response",
                text=result.final_output,
            ),
        )
        
        # This sends the actual content or output produced by the agent.
        await event_queue.enqueue_event(artifact)

        # After sending the response, the executor updates the task status.
        status = TaskStatusUpdateEvent(
            context_id=context.context_id,
            task_id=context.task_id,
            status=TaskStatus(state=TaskState.completed),
            final=True,
        )
        # This informs the client that the task execution has completed.
        await event_queue.enqueue_event(status)

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("cancel not supported")