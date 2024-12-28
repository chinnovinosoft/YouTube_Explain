from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class NeutralFeedBackCrew:
    """NeutralFeedBack Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"


    @agent
    def neutral_feedback_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["neutral_feedback_agent"],
        )

    
    @task
    def handle_neutral_feedback_task(self) -> Task:
        return Task(
            config=self.tasks_config["handle_neutral_feedback_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Crew for Neutral Feedback which suggests few other resturants"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
