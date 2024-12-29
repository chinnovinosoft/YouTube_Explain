#!/usr/bin/env python
from random import randint

from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from litellm import completion
from .crews.budget_or_internet_check_crew.budget_or_internet_crew import UnionBudgetCheckCrew
from .crews.budget_response_crew.budget_crew import UnionBudgetCrew
from .crews.internet_response_crew.internet_crew import InternetCrew


class UnionBudgetState(BaseModel):
    query_type: str = ""
    query: str = ""


class UnionBudgetFlow(Flow[UnionBudgetState]):

    model = "gpt-4o-mini"

    @start()
    def greet_customer(self):
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": "Greet a customer in a very excited manner so that, He should always have smile on his face before asking us anything.",
                },
            ],
        )
        random_greet = response["choices"][0]["message"]["content"]
        print(f"***** %%%%%\n\n, {random_greet} ***** %%%%% \n\n")


    @listen(greet_customer)
    def generate_UnionBudget(self):
        # print("Generating UnionBudget")
        self.state.query  = input("Please feel to ask me anything related to UNION BUDGET : ")


    @listen(generate_UnionBudget)
    def trigger_crews(self):
        
        response = "No response generated due to an unknown query type."
        self.state.query_type = UnionBudgetCheckCrew().crew().kickoff(inputs={"query": self.state.query})
        print('Query Typeee ---->>>  ',self.state.query_type)
        if self.state.query_type['union_budget_flag'] =='union':
            print("You are asking UNION BUDGET related query, Let me answer you clearly !!\n\n\n")
            response = UnionBudgetCrew().crew().kickoff(inputs={"query": self.state.query})
        elif self.state.query_type['union_budget_flag'] =='NA':
            print("This is the query beyond my knowledge so, Let use the internet and answer the query\n\n\n")
            response = InternetCrew().crew().kickoff(inputs={"query": self.state.query})
        else:
            print("The query type is not recognized. Please ensure your input is valid.")

        
        print("\n\n Here is the Response \n\n")
        print(response)
        
        # return response
    


def kickoff():
    UnionBudget_flow = UnionBudgetFlow()
    UnionBudget_flow.kickoff()


def plot():
    UnionBudget_flow = UnionBudgetFlow()
    UnionBudget_flow.plot()


if __name__ == "__main__":
    kickoff()
