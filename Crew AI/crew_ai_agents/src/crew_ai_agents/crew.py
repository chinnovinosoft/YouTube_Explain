from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

@CrewBase
class CricketAgent():
	"""CricketAgent crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@agent
	def stats_fetcher(self) -> Agent:
		return Agent(
			config=self.agents_config['stats_fetcher'],
			verbose=True,
			tools = [SerperDevTool()]
		)

	@agent
	def stats_calculator(self) -> Agent:
		return Agent(
			config=self.agents_config['stats_calculator'],
			verbose=True,
			# tools =[ChatOpenAI()]
		)

	@agent
	def graph_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['graph_creator'],
			verbose=True,
			allow_code_execution=True,
			code_execution_mode='unsafe',
		)
	
	@task
	def fetch_cricketer_scores_task(self) -> Task:
		return Task(
			config=self.tasks_config['fetch_cricketer_scores_task'],
		)

	@task
	def calculate_cricketer_averages_task(self) -> Task:
		return Task(
			config=self.tasks_config['calculate_cricketer_averages_task'],
			context = [self.fetch_cricketer_scores_task()],
			output_file='stats_for_crickter.txt'
		)

	@task
	def create_performance_graph_task(self) -> Task:
		return Task(
			config=self.tasks_config['create_performance_graph_task'],
			context = [self.calculate_cricketer_averages_task()],
			output_file='starts_grap.png'
		)
	
	@crew
	def crew(self) -> Crew:
		"""Creates the CricketAgent crew"""
		return Crew(
			agents=self.agents, 
			tasks=self.tasks, 
			process=Process.sequential,
			verbose=True,
		)

