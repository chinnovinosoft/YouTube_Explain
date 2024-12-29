from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import json 
from pydantic import BaseModel


class UnionBudgetCheck(BaseModel):
    union_budget_flag: str


@CrewBase
class UnionBudgetCheckCrew:
    """UnionBudget Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def budget_query_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["budget_query_agent"],
        )
    

    @task
    def classify_budget_query_tasks(self) -> Task:
        return Task(
            config=self.tasks_config["classify_budget_query_tasks"],
            output_pydantic=UnionBudgetCheck,
        )

    
    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
