from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool,FileWriterTool

@CrewBase
class ResumeBuilderCrew():
  """ResumeBuilder crew"""

  @agent
  def resumebuilder(self) -> Agent:
    return Agent(
      config=self.agents_config['resumebuilder'],
      verbose=True,
      tools=[FileWriterTool()]
    )

  @agent
  def resumereviewandreconstruct(self) -> Agent:
    return Agent(
      config=self.agents_config['resumereviewandreconstruct'],
      verbose=True,
      tools=[FileWriterTool()]
    )

  @task
  def resumebuilder_task(self) -> Task:
    return Task(
      config=self.tasks_config['resumebuilder_task'],
    )

  @task
  def resumereviewandreconstruct_task(self) -> Task:
    return Task(
      config=self.tasks_config['resumereviewandreconstruct_task'],
      output_file='output/resume.txt' # This is the file that will be contain the final report.
    )

  @crew
  def crew(self) -> Crew:
    """Creates the ResumeBuilder crew"""
    return Crew(
      agents=self.agents,
      tasks=self.tasks, 
      process=Process.sequential,
      verbose=True,
    )
