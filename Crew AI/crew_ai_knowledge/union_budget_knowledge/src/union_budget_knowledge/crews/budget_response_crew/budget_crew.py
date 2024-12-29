from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
from PyPDF2 import PdfReader
from crewai_tools import SerperDevTool
from typing import Dict, Any
from PyPDF2 import PdfReader
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
#uv add moule name

class UnionBudgetKnowledgeSource(BaseKnowledgeSource):
    """Knowledge source that fetches union budget data from a PDF."""

    file_path: str  # Declare the file path as an attribute

    def load_content(self) -> Dict[Any, str]:
        """Extract content from the PDF file."""
        try:
            reader = PdfReader(self.file_path)

            # Extract text from all pages
            content = ""
            for page in reader.pages:
                content += page.extract_text()

            # Return as a dictionary with a key for the source
            return {self.file_path: content}
        except Exception as e:
            raise ValueError(f"Failed to load PDF content: {str(e)}")

    def add(self) -> None:
        """Process and store the PDF data on the Union Budget."""
        # Load content from the PDF
        content = self.load_content()

        # Process the extracted content
        for _, text in content.items():
            chunks = self._chunk_text(text)  # Assuming _chunk_text is defined in BaseKnowledgeSource
            self.chunks.extend(chunks)

        metadata_list = [
            {
                "source": "Union Budget PDF",
                "file_path": self.file_path,
                "chunk_index": idx,
                "description": "Union Budget Analysis for 2023-24",
            }
            for idx in range(len(self.chunks))
        ]

        # Save the processed content with metadata
        self.save_documents(metadata=metadata_list)

# Instantiate the knowledge source
union_data = UnionBudgetKnowledgeSource(
    file_path="/Users/praveenreddy/crewai_2/union_budget_knowledge/Union_Budget_Analysis-2023-24.pdf"
)


@CrewBase
class UnionBudgetCrew:
    """UnionBudget Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def union_budget_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["union_budget_agent"],
            knowledge_sources=[union_data],
        )

    @task
    def union_budget_query_tasks(self) -> Task:
        return Task(
            config=self.tasks_config["union_budget_query_tasks"],
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
