from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class GoodFeedBackCrew:
    """GoodFeedBack Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def positive_feedback_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["positive_feedback_agent"],
        )

    @task
    def handle_positive_feedback_task(self) -> Task:
        return Task(
            config=self.tasks_config["handle_positive_feedback_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Crew that generates the Good Feedback Message"""

        return Crew(
            agents=self.agents,  
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
