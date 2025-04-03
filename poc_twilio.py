# poc_twilio.py
# Last modified: 4/2/25
# Authors: Claire Becker, Claire Williams, Olivia Byun, Zoe Gu
#
# This file contains endpoints for sending a message through the Twilio
# Messaging API. It also prepends the user's prompt and passes it through to
# the chat engine, generating a response to be sent to the user.

import logging
import unicodedata
from twilio.rest import Client
from fastapi import FastAPI, Request
from langchain_community.llms import CTransformers
from app import response
from urllib.parse import parse_qs
from dotenv import dotenv_values
from rag_utils_manatee import create_chat_engine
import math

config = dotenv_values(".env")

# dependencies:
# pip install fastapi uvicorn twilio python-dotenv langchain-community
# may have to use pip3 depending on what you have

# TROUBLESHOOTING
# if having issues with ngrok not found, ngrok may need to be moved to /usr/bin
    # download ngrok from internet (insert link)
    # run command: sudo unzip ~/Downloads/ngrok-v3-stable-darwin-arm64.zip -d /usr/local/bin
    # run command: sudo cp ngrok /usr/local/bin
# after running these commands, you should now be able to run ngrok

# HOW TO RUN:
# uvicorn poc_twilio:app --reload
# ngrok http 8000
    # need to paste in authentication code (after logging in online) to terminal
        # ngrok config add-authtoken ________
    # take forwarding link from ngrok http 8000 command and paste into twilio sandbox
    # we can go to local host to see POSTs

# WHATSAPP SANDBOX
    # enter join code and send to chatbot to connect to sandbox
    # syntax: join <joincode>

# TO DO's:
# add to documentation - to create vectors, look at the manatee_rag_playground.ipynb code
# figure out how to bypass/workaround 1600 character Twilio limit
    # while loop: split into multiple messages
# use with multiple phones at a time
# encoding error when we use an apostrophe?
    # preprocessing?
# only prepend queries sometimes - prompt engineering
# set up our own .env
# push changes to GitHub
# dealing with irrelevant queries
# connect with Forest Green to see how their implementation works
# figure out how use all data from different from folders (not just verbs)
    # come back to this later

app = FastAPI()

TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_NUMBER = ""

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)
twilio_number = TWILIO_NUMBER 

# @app.post("/")
# async def welcome():
#     send_message("+", "HI I AM MESSAGE")
#     return "Hi"

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# llm = CTransformers(model="openhermes-2-mistral-7b.Q8_0.gguf", model_type= "llama")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    try: 
        # ensure phone number is in valid format
        if not validate_phone_number(to_number):
            logger.error(f"Cannot send message to invalid number: {to_number}")
            return {"error": "Invalid phone number"}
        
        # create message to send via Twilio API
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"{to_number}"
            )
        logger.info("Validating phone number")
       
        # Regular expression to validate the phone number
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")

@app.post("/")
async def reply(question:Request):
    logger.info(f"reply function called")
    
    form_data = await question.form()
    
    # obtain sender's phone number
    sender = form_data.get("From", "").rstrip()
    logger.info(f"Incoming message from {sender}.")

    # check that sender has correct format
    if not sender.startswith("whatsapp:"):
        logger.error(f"Invalid sender number format: {sender}")
        return {"error": "Invalid sender number format"}
    
    # removing non ascii characters
    incoming_message = form_data.get("Body", "")
    incoming_message = unicodedata.normalize("NFKD", incoming_message).encode("ascii", "ignore").decode()

    try:
        logger.info("Raw body: {raw_body}")

        chat_engine = create_chat_engine()
        logger.error("created chat engine")
        prepend = "I am going to give you a query to generate a lesson plan. Here are some general guidelines, but if the query says something contradicting this, go with the query. The lessons are taught in only English. Make sure that every new topic has a question posed alongside it. Questions are insightful and appropriate. Make sure the lesson has appropriate icebreakers at the beginning and asks students about their day, lessons maintain a friendly atmosphere. Generate 3 or more specific sets of practice problems. Create a brief introduction to the topic. The lesson plan should contain 5 or more specific examples. The lesson plan should have the following sections: Objective, Warm-up, Introduction, Explanation, Examples, Practice Problems, Interactive Activity, and Conclusion. Based on these guidelines, generate a lesson plan given the following topic: "
        logger.error("created prepend")

        rag_response = chat_engine.chat(prepend + incoming_message)
        logger.error("created rag_response")

        reply = str(rag_response)

        reply_arr = []
        for i in range(math.ceil(len(reply) / float(1600))):
            reply_arr.append(reply[i * 1600 : ((i + 1) * 1600)])
            logger.error(f"reply array: {reply_arr}")

        # reply2
        logger.error("created reply")
        logger.info("sending message to: {sender}")
        for reply in reply_arr:
            send_message(sender, reply)
        # send_message(sender, reply)
        # reply2
        # logger.error("created reply")        
        
        # logger.error("sent message")
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        send_message(sender, "wait")
    return 

def validate_phone_number(phone_number):
    try:
        phone_number_info = client.lookups.phone_numbers(phone_number).fetch(type="carrier")
        logger.info(f"Valid number: {phone_number_info.phone_number}")
        return True
    except Exception as e:
        logger.error(f"Invalid phone number: {phone_number} - Error: {str(e)}")
        return False