#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow.flow import Flow, listen, start, router, and_

from .crews.good_feedback.good_feedback_crew import GoodFeedBackCrew
from .crews.bad_feedback.bad_feedback_crew import BadFeedBackCrew
from .crews.neutral_feedback.neutral_feedback_crew import NeutralFeedBackCrew
from litellm import completion

class FoodReviewState(BaseModel):
    review_type: int = 1
    review: str = ""
    restaurant_name: str = ""


class FoodReviewFlow(Flow[FoodReviewState]):

    model = "gpt-4o-mini"

    @start()
    def generate_food_liner(self):
        # print("Starting flow")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": "Generate a 1 liner message about tasty food, which should bring smile on customer face after reading it",
                },
            ],
        )
 
        random_message = response["choices"][0]["message"]["content"]
        print(f"So************%%%%%%%%%%%%%%%%--->>, {random_message}")


    @listen(generate_food_liner)
    def take_review_input(self):
        self.state.review  = input("I am eager to hear the review of the food you just tasted?, Please comment along with resturant name ---> :) ")
        return self.state.review
    
    @listen(take_review_input)
    def categorize_review(self):
        # print("Categorising the Review into good, bad & neutral")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Here is the review user has provided : {self.state.review} , and you are the review categorizer, Please categorise it into any of the follwoing 3 --> good, neutral, bad. Respond with only any one of those 3 choices, no extra text. ",
                },
            ],
        )

        self.state.review_type = response["choices"][0]["message"]["content"]
        print(f"System has categorised the REWVIEW YOU HAVE GIVEN as :::>>>>>>>>>        {self.state.review_type}")

    @listen(take_review_input)
    def fetch_restaurant_name(self):
        # print("Fetching Resturant Name from Review")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Here is the review user has provided : {self.state.review} , and you are the resturant name extractor, Please extract resturant name from the review. Respond with only resturant name, no extra text. ",
                },
            ],
        )

        self.state.restaurant_name = response["choices"][0]["message"]["content"]
        print(f"So, Based on the review you gave, Resturant you have visited is  :::::::::::::::::::::::>> {self.state.restaurant_name}")


    @router(fetch_restaurant_name)
    @router(categorize_review)
    def second_method(self):
        if self.state.review_type == 'good':
            print("inside good")
            return "good"
        elif self.state.review_type == 'neutral':
            print("inside neutral")
            return "neutral"
        else:
            print("inside bad")
            return "bad"
    
    @listen("good")
    def good_feedback_method(self):
        # print("inside good_feedback_method")
        result = GoodFeedBackCrew().crew().kickoff()

    @listen("bad")
    def bad_feedback_method(self):
        # print("inside bad_feedback_method")
        result = BadFeedBackCrew().crew().kickoff(inputs={"review": self.state.review,"restaurant_name": self.state.restaurant_name})

    @listen("neutral")
    def neutral_feedback_method(self):
        # print("inside neutral_feedback_method")
        result = NeutralFeedBackCrew().crew().kickoff()


def kickoff():
    poem_flow = FoodReviewFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = FoodReviewFlow()
    poem_flow.plot()


if __name__ == "__main__":
    kickoff()
# Steps used to run the code 
# 1. crewai install
# 2. source .venv/bin/activate
# 3. uv add psycopg2-binary
# 4. crewai flow kickoff