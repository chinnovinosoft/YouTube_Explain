from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from sqlalchemy import create_engine
import pandas as pd
from crewai.tools import tool
from sqlalchemy.sql import text

# engine = create_engine("postgresql+psycopg2://postgres:Pra123%401@localhost:5432/crewai")
engine = create_engine("postgresql+psycopg2://postgres:Pra123%401@localhost:5432/crewai", isolation_level="AUTOCOMMIT")

try:
    with engine.connect() as connection:
        print("Connected to PostgreSQL!")
except Exception as e:
    print("Error:", e)

query = text("""
        INSERT INTO public.feedback_table (feedback_message, restaurant_name)
        VALUES (:feedback_message, :restaurant_name)
        """)

# with engine.connect() as connection:
#         connection.execute(query, {
#             "feedback_message": "Hello",
#             "restaurant_name": "Hi"
#         })

# from sqlalchemy.sql import text

with engine.connect() as connection:
    query = text("""
        INSERT INTO public.feedback_table (feedback_message, restaurant_name)
        VALUES (:feedback_message, :restaurant_name)
    """)
    connection.execute(query, {
        "feedback_message": "Hello",
        "restaurant_name": "Hi"
    })
print("executed insert")