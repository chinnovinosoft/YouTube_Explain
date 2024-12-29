from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from crewai.memory.short_term.short_term_memory import ShortTermMemory
from crewai.memory.long_term.long_term_memory import LongTermMemory
from crewai.memory.entity.entity_memory import EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from mem0 import MemoryClient
from mem0 import Memory


client = Memory() #MemoryClient(api_key="")

messages = [
	{"role": "user", "content": "Hi, I'm Praveen. I'm a vegetarian."},
	{"role": "assistant", "content": "Hello Praveen! That's good to be a vegitarian, Please tell me how can i assist you!!"},
	{"role": "user", "content": "I am planning to take my family to resturant tonight at Hyderabad, Gachibowli!!"}
]
client.add(messages, user_id="chinnareddy")

@CrewBase
class CrewAiMemory():
	"""CrewAiMemory crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def chatbot(self) -> Agent:
		return Agent(
			config=self.agents_config['chatbot'],
			verbose=True,
			# memory=True
		)

	@task
	def chat_task(self) -> Task:
		return Task(
			config=self.tasks_config['chat_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the CrewAiMemory crew"""

		# return Crew(
		# 	agents=self.agents, # Automatically created by the @agent decorator
		# 	tasks=self.tasks, # Automatically created by the @task decorator
		# 	process=Process.sequential,
		# 	verbose=True,
		# 	memory=True
		# )
	
		# return Crew(
    	# 	agents=self.agents, # Automatically created by the @agent decorator
		# 	tasks=self.tasks, # Automatically created by the @task decorator
		# 	process=Process.sequential,
    	# 	memory=True,
		# 	long_term_memory=LongTermMemory(
		# 		storage=LTMSQLiteStorage(
		# 			db_path="/Users/praveenreddy/crewai_2/memory/long_term/long_term_memory_storage.db"
		# 		)
		# 	),
		# 	short_term_memory=ShortTermMemory(
		# 		storage=RAGStorage(
		# 			type="short_term",
		# 			allow_reset=True,
		# 			embedder_config={
		# 				"provider": "openai",  # Specify the provider explicitly
		# 				"config":{
		# 					"model": "text-embedding-ada-002",  # Specify the model
		# 					"api_key": "", 
		# 				}
		# 			},
		# 			crew=self,  # Pass crew agents if needed
		# 			path="/Users/praveenreddy/crewai_2/memory/short_term",
		# 		),
		# 	),
		# 	entity_memory=EntityMemory(
		# 		storage=RAGStorage(
		# 			type="entities",
		# 			allow_reset=True,
		# 			embedder_config={
		# 				"provider": "openai",  # Specify the provider explicitly
		# 				"config":{
		# 					"model": "text-embedding-ada-002",  # Specify the model
		# 					"api_key": "sk-", 
		# 				}
		# 			},
		# 			crew=self,  # Pass crew agents if needed
		# 			path="/Users/praveenreddy/crewai_2/memory/entity",
		# 		),
		# 	),
		# 	verbose=True,
		# )
		return Crew(
			agents=self.agents, 
			tasks=self.tasks, 
			process=Process.sequential,
			verbose=True,
			memory=True,
			memory_config={
				"provider": "mem0",
				"config": {
					"user_id": "chinnareddy",
					"api_key": ""
			   },
			},
		)