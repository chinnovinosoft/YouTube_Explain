#!/usr/bin/env python
import sys
import warnings
from pydantic import BaseModel
from crew_ai_tasks.crew import CrewAiTasks


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """
    Run the crew.
    """
    inputs = {
        'query': 'What is the name of the student who won the cups in last few years from Indian Institute of Technology Delhi'
    }
    crew_instance  = CrewAiTasks().crew()
    result = crew_instance.kickoff(inputs=inputs)
    
    print("**********************")
    print(crew_instance.tasks)
    print("**********************")
    for task in crew_instance.tasks:
        task_output = task.output
        print(f"Task Description: {task_output.description}")
        print(f"Task Summary: {task_output.summary}")
        print(f"Raw Output: {task_output.raw}")
        print(f"Task Agent: {task_output.agent}")
        print(f"Task Name: {task.name}")
    # print(crew_instnace.tasks['analyze_csv_task'].result)
    
    print('--->> result ',result)
    # print("*********output pydantic*************")
    # print("Type 1------->")
    # college_name = result["college_name"]
    # query_response = result["query_response"]
    # print("college_name:", college_name)
    # print("query_response:", query_response)

    # print("Type 2 ---------->")
    # print("Accessing Properties - Option 2")
    # college_name = result.pydantic.college_name
    # query_response = result.pydantic.query_response
    # print("college_name:", college_name)
    # print("query_response:", query_response)

    # print("Type 3  ---------->")
    # output_dict = result.to_dict()
    # college_name = output_dict["college_name"]
    # query_response = output_dict["query_response"]
    # print("college_name:", college_name)
    # print("query_response:", query_response)

    # print("**********output json************")
    # college_name = result["college_name"]
    # query_response = result["query_response"]
    # print("college_name:", college_name)
    # print("query_response:", query_response)




# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs"
#     }
#     try:
#         CrewAiTasks().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         CrewAiTasks().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs"
#     }
#     try:
#         CrewAiTasks().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")
