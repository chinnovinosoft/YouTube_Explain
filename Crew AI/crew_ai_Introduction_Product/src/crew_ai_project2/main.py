#!/usr/bin/env python
import sys
from crew_ai_project2.crew import ResumeBuilderCrew

def run():
  """
  Run the crew.
  """
  inputs = {
    'topic': 'Data Engineering'
  }
  ResumeBuilderCrew().crew().kickoff(inputs=inputs)
