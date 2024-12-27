from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

tool = SerperDevTool()
# uv add matplotlib -- to add matplotlib module 
# crew defines the strategy for task execution, agent collaboration, and the overall workflow.
@CrewBase
class CrewAiCrews():
	"""CrewAiCrews crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	step = 1

	def callback_func(self):
		self.step = self.step + 1
		print(f"Step {self.step} executed. Details: ")

	def callback_task_func(self):
		print(f"Task {self.step} executed. Details: ")

	@agent
	def agent_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['manager_agent'],
			verbose=True,
			llm = ChatOpenAI()
		)
	
	@agent
	def stock_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['stock_researcher'],
			verbose=True
		)

	@agent
	def sp_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['sp_researcher'],
			verbose=True
		)
	
	@agent
	def data_preparer(self) -> Agent:
		return Agent(
			config=self.agents_config['data_preparer'],
			verbose=True
		)
	
	@agent
	def data_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['data_analyst'],
			verbose=True,
			allow_code_execution=True,
			code_execution_mode='unsafe',
		)

	@task
	def stock_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['stock_research_task'],
			tools = [tool]
		)

	@task
	def sp_data_task(self) -> Task:
		return Task(
			config=self.tasks_config['sp_data_task'],
			tools = [tool]
		)
	
	@task
	def data_preparation_task(self) -> Task:
		return Task(
			config=self.tasks_config['data_preparation_task'],
			tools = [tool],
			output_file='stock_data.txt',
			context = [self.stock_research_task()]
		)
	
	@task
	def comparison_and_graph_task(self) -> Task:
		return Task(
			config=self.tasks_config['comparison_and_graph_task'],
			context = [self.data_preparation_task(),self.sp_data_task()],
			output_file='final_analysis.txt',
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the CrewAiCrews crew"""

		return Crew(
			agents=self.agents, 
			tasks=self.tasks, 
			process=Process.sequential,
			verbose=True,
			full_output=True,
			step_callback = self.callback_func(), #executes after each step.... It's useful for tracking progress or logging every action an agent performs, such as tool invocations, decisions, or task completions.
			#One step of an agent's task (a single action or tool call).
			task_callback = self.callback_task_func(), #executes after each task....
			#The entire task (after all actions or tool calls are finished).
			manager_agent = self.agent_manager(),
			output_log_file = "logs.txt"

		)
