from ai_utils import *
from calendar_utils import *

import os
import json

import google.auth.exceptions
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from openai import OpenAI
from datetime import datetime, timedelta, timezone
import pytz

from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify
import time

load_dotenv()  # Load environment variables from .env file

# Load API keys and other sensitive information from environment variables
api_key = os.getenv('OPENAI_API_KEY')


# ------------------------------ Function selection ------------------------------- #
def execute_calendar_action(gpt_output):
    """
    Determine and execute the appropriate calendar action based on the LLM's output.

    Args:
        gpt_output (dict): Parsed output from the GPT model containing the action and parameters.

    Returns:
        str: Result of the executed action or an error message.
    """
    if gpt_output is None:
        return "Error: Failed to process GPT output."

    action = gpt_output.get("action")

    if action == "add_event":
        return add_event(gpt_output)
    elif action == "upcoming_events":
        return get_upcoming_events()
    elif action == "delete_event":
        event_id = gpt_output.get("params", {}).get("event_id")
        return delete_event(event_id)
    elif action == "update_event":
        event_id = gpt_output.get("params", {}).get("event_id")
        updated_data = gpt_output.get("params", {}).get("updated_data")
        return update_event(event_id, updated_data)
    else:
        return f"Unknown action: {action}"


# ----------------------------- Flask Application | UI ---------------------------- #

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    """ Render the main page for user interaction. """
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    """
        Handle user input from the web interface and process the command.

        Returns:
            JSON: Response message after executing the command.
    """
    user_input = request.form['user_input']
    print(user_input)
    time.sleep(1)

    ai_output = process_natural_language_command(user_input)
    print(ai_output)
    time.sleep(1)

    response = execute_calendar_action(ai_output)
    print(response)

    time.sleep(3)
    return response.replace("\n", "<br>")
    # return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=5003)
