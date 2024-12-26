from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
from crewai_tools import CSVSearchTool
from pydantic import BaseModel
from crewai.tasks.task_output import TaskOutput


csv_tool = CSVSearchTool(csv='/Users/praveenreddy/crewai_2/crew_ai_tasks/data.csv')

class Output(BaseModel):
		college_name: str
		query_response: str


@CrewBase
class CrewAiTasks():
	"""CrewAiTasks crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	def callback_function(self,output: TaskOutput):
    	# Do something after the task is completed
    	# Example: Send an email to the manager , Updating DB 
		print(f"""
    	    Task completed!
    	    Task: {output.description}
    	    Output: {output.raw}
    	""")


	@agent
	def csv_analyzer(self) -> Agent:
		return Agent(
			config=self.agents_config['csv_analyzer'],
			verbose=True
		)

	@task
	def analyze_csv_task(self) -> Task:
		return Task(
			name='analyze_csv_task',
			config=self.tasks_config['analyze_csv_task'],
			tools=[csv_tool],
			# output_pydantic=Output
			# output_json= Output,
			# callback=self.callback_function
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the CrewAiTasks crew"""

		return Crew(
			agents=self.agents, 
			tasks=self.tasks, 
			process=Process.sequential,
			verbose=True,
		)
