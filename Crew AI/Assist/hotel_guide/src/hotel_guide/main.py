#!/usr/bin/env python
from random import randint

from pydantic import BaseModel
from typing import Literal
from crewai.flow.flow import Flow, listen, router, start, or_
from crewai import LLM
from src.hotel_guide.db import *
from crewai_tools import SerperDevTool
import json 

class ReceptionState(BaseModel):
    user_queries: list[str]=[]
    query_type: Literal[
        "reception_checkin",
        "reception_room_service",
        "local_information",
        "feedback_collection"
    ]="reception_checkin"

class QueryType(BaseModel):
    query_type: Literal[
        "reception_checkin",
        "reception_room_service",
        "local_information",
        "feedback_collection"
    ]="reception_checkin"

class HotelAssistFlow(Flow[ReceptionState]):

    @start()
    def know_user_query_type(self):
        print("Starting the Hotel Assist Flow")
        print(self.state.user_queries)
        print("================")
        user_told = self.state.user_queries[-1]
        
        # Store in state for use across the flow
        self.state.user_queries.append(user_told)
        print("User told:", user_told)

        llm = LLM(model="gpt-4o", response_format=QueryType)
        response = llm.call(
            "Analyze the following input and determine the type of query: "
            "You are a hotel receptionist. "
            "If the query is related to check-in then return 'reception_checkin'. "
            "If the query is related to room service then return 'reception_room_service'. "
            "If the query is related to local informatio dcx type of query as a string."
            f"Here is the user Query : {user_told}"
        )

        print("Response from LLM:", response, "--> ",type(json.loads(response)))
        res = json.loads(response)
        print("User query type determined:", res['query_type'])
        self.state.query_type = res['query_type']

    @router(know_user_query_type)
    def decider(self):
        if self.state.query_type == "reception_checkin":
            return "reception_checkin"
        elif self.state.query_type == "reception_room_service":
            return "reception_room_service"
        elif self.state.query_type == "local_information":
            return "local_information"
        elif self.state.query_type == "feedback_collection":
            return "feedback_collection"
        else:
            return "irrelevant_query"
        
    @listen("reception_checkin")
    def handle_checkin(self):
        print("Handling check-in")
        # Here you would implement the logic for handling check-in
        user_response = self.state.user_queries[-1]
        llm = LLM(model="gpt-4o")
        response = llm.call(
            "You are provided with user response to check-in query. "
            "You need to extract the phone number from the response. "
            "If the phone number is not found, return 'No phone number found'. "
            "If the phone number is found, return it as a string."
            "You need to just respond with the phone number or 'No phone number found'. "
            "Please do not respond with any other text or explanation. "
            f"The user response is : {user_response}"
        )
        # res =  json.loads(response)
        print("Extracted phone number:", response)
        phone_number = response
        if phone_number == "No phone number found":
            print("No phone number found in the response.")
            phone_number = input("Please provide your phone number to proceed with check-in: ")
        
        details = get_latest_booking_by_phone(
            host="localhost",
            port=5432,
            dbname="hotel_db",
            user="postgres",
            password="postgres",
            phone=phone_number
        )
        if details:
            room = details['room_number']
            checkout = details['check_out']
            price = details['price_per_night']
            res = f"Yes Sir, we have found your booking, You can check in to room number: {room} . \n Your check-out date is: {checkout} . \n Incase if you need to extend your stay, the price per night is: {price} rupees \n "
            print(res)
        else:
            res = "No booking found for phone:"+ f"{phone_number}"
            print(res)
        return res

    @listen("reception_room_service")
    def handle_room_service(self):
        print("Handling room service")
        user_response = self.state.user_queries[-1]
        res = "Sure sir, We will do it. Please relax while we process your details."
        print("User response for room service:", res)
        return res

    @listen("local_information")
    def handle_local_information(self):
        user_response = self.state.user_queries[-1]
        print("Handling local information request")
        tool = SerperDevTool(n_results=2)
        response = tool.run(search_query=f"{user_response} . The response should be short and concise.")
        print("Here is what you can consider : ", response)
        print("\n")
        organic_results = response.get("organic", [])
        result = organic_results[0] 
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        print(f"Title: {title}")
        print(f"Snippet: {snippet}\n")
        return snippet
    
    @listen("feedback_collection")
    def handle_feedback_collection(self):
        print("Handling feedback collection")
        user_response = self.state.user_queries[-1]
        res = "Thank you for your feedback! We appreciate your input and will use it to improve our services better."
        return res

    # @listen(or_(handle_checkin, handle_room_service, handle_local_information, handle_feedback_collection))
    # def greet_user(self):
    #     print("Greeting user")
    #     print("Thank you for reaching out to us. We wish to see you again soon. Have a great day ahead!")


def kickoff(text=None):
    
    hotel_flow = HotelAssistFlow()
    # hotel_flow.kickoff(inputs={
    #     "user_queries": ["Hey, I would like to check in. I have a reservation under the name Praveen with phone number 7675860617."]
    # })
    # hotel_flow.kickoff(inputs={
    #     "user_queries": ["Hey, I need some room service."]
    # })
    # hotel_flow.kickoff(inputs={
    #     "user_queries": ["Hey, I am new ti this City Hyderabad, can you please help me with the local places to spend time with my family for a day?"]
    # })
    return hotel_flow.kickoff(inputs={
        "user_queries": [f"{text}"]
    })


def plot():
    hotel_flow = HotelAssistFlow()
    hotel_flow.plot()


if __name__ == "__main__":
    kickoff()
