from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool


tool = SerperDevTool()

@CrewBase
class InternetCrew:
    """Internet Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def internet_search_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["internet_search_agent"],
        )

    @task
    def internet_search_query_tasks(self) -> Task:
        return Task(
            config=self.tasks_config["internet_search_query_tasks"],
            tools = [tool]
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Internet Search Crew"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
