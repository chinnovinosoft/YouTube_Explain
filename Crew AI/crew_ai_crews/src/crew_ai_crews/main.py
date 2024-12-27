#!/usr/bin/env python
import sys
import warnings

from crew_ai_crews.crew import CrewAiCrews

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'stock': 'NVIDIA'
    }
    result = CrewAiCrews().crew().kickoff(inputs=inputs)
    print('result ---->>>>> ',result)

