from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from sqlalchemy import create_engine
import pandas as pd
from crewai.tools import tool
from sqlalchemy.sql import text

# engine = create_engine("postgresql+psycopg2://postgres:Pra123%401@localhost:5432/crewai")
engine = create_engine("postgresql+psycopg2://postgres:Pra123%401@localhost:5432/crewai", isolation_level="AUTOCOMMIT")

# Example: Test connection
try:
    with engine.connect() as connection:
        print("!!")
except Exception as e:
    print("Error:", e)

class FeedBackTools:
    @staticmethod
    @tool("Inserts an entry in the feedback_table")
    def db_insert(feedback_message: str, restaurant_name: str) -> str:
        """Inserts an entry in the feedback_table in PostgreSQL."""
        query = text("""
        INSERT INTO public.feedback_table (feedback_message, restaurant_name)
        VALUES (:feedback_message, :restaurant_name)
        """)
        try:
            with engine.connect() as connection:
                connection.execute(query, {
                    "feedback_message": feedback_message,
                    "restaurant_name": restaurant_name
                })
            return "Feedback successfully inserted into the database."
        except Exception as e:
            return f"Error inserting feedback: {e}"

@CrewBase
class BadFeedBackCrew:
    """BadFeedBack Crew"""
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # feedback_tools = FeedBackTools()

    @agent
    def negative_feedback_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["negative_feedback_agent"],
        )
    
    @agent
    def db_update_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["db_update_agent"],
        )
    
    @task
    def handle_negative_feedback_tasks(self) -> Task:
        return Task(
            config=self.tasks_config["handle_negative_feedback_tasks"],
        )
    
    @task
    def update_db_tasks(self) -> Task:
        return Task(
            config=self.tasks_config["update_db_tasks"],
            tools=[FeedBackTools.db_insert] 
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Crew that updates the DB when the feedback is negative"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
