from __future__ import print_function
import os.path
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import google.auth.exceptions
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from openai import OpenAI
from datetime import datetime, timedelta, timezone
import pytz

# ------------------------- Configuration ------------------------- #
# Define the scope for Google Calendar API access
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Load API keys and other sensitive information from environment variables
api_key = os.getenv('OPENAI_API_KEY')


# ------------------------- Google Calendar Authentication ------------------------- #
def authenticate_google_calendar():
    """
        Authenticate the user with Google Calendar API.
        Handles token refresh and credential storage in 'token.json'.

        Returns:
            service: An authorized Google Calendar API service instance.
        """
    creds = None

    # Check if the token.json file with user credentials exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If credentials are invalid or expired, prompt the user to re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except google.auth.exceptions.RefreshError:
                print("Token has expired or being revoked. Removing token.json and re-authenticating")
                os.remove('token.json')  # Removes the invalid token file
                creds = None  # Resets creds to trigger re-authentication below
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Saves the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


# Initialize and build the service object
calendar_service = authenticate_google_calendar()


# ------------------------- Google Calendar Functions ------------------------- #
def get_upcoming_events(service, max_results=10):
    """
    Retrieve a list of upcoming events from the user's Google Calendar.

    Args:
        service: Authorized Google Calendar service instance.
        max_results (int): Maximum number of events to fetch.

    Returns:
        str: A formatted string of upcoming events.
    """
    # Get the current time in the correct timezone
    now = datetime.now(pytz.timezone('America/Denver')).isoformat()
    print(now)

    # Fetch events from the current time onwards
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,  # Only return events from the current time forward
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return 'No upcoming events found.'

    response = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        response.append(f"{start}: {event['summary']}")

    return "\n".join(response)


def add_event(gpt_output):
    """
    Add a new event to the user's Google Calendar.

    Args:
        event_data (dict): Event details parsed from user input.

    Returns:
        str: Confirmation message.
    """
    event_params = gpt_output["params"]
    if 'end' not in event_params:
        # Assuming start time is already set in event_params
        start_time = datetime.fromisoformat(event_params['start']['dateTime'])
        end_time = start_time + timedelta(hours=1)
        event_params['end'] = {'dateTime': end_time.isoformat()}
    calendar_service.events().insert(calendarId='primary', body=event_params).execute()
    return "Event created"


# TODO: Functions for delete_event and update_event
def delete_event(gpt_output):
    # Implementation for deleting an event
    pass


def update_event(gpt_output):
    # Implementation for updating an event
    pass


# ------------------------- Function selection ------------------------- #
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
        return get_upcoming_events(calendar_service)
    elif action == "delete_event":
        return delete_event(gpt_output)
    elif action == "update_event":
        return update_event(gpt_output)
    else:
        return f"Unknown action: {action}"


# ------------------------- OpenAI Integration ------------------------- #

client = OpenAI(api_key=api_key)


def process_natural_language_command(user_input):
    """
    Process a natural language command using OpenAI's GPT model.

    Args:
        user_input (str): The user's input command.

    Returns:
        dict: Parsed action and parameters for Google Calendar.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You are the middleman between the user and "
                                          "their google calendar. Your role is to interpret the user's input, "
                                          "extract and return as sole output 2 items in a python dictionary: action("
                                          "one of add_event or upcoming_events), params(fill the parameters "
                                          "needed to call"
                                          "from the google calendar API the method corresponding to the user's desired"
                                          f"action) My timezone is Mountain Time and this is today's date and time {datetime.now()} "
                                          f"and if there is no end time, assume it will last 1 hour."
                                          f" This second item will be used to execute the action on the user's google "
                                          "calendar. For your reference, this is a sample response you should output "
                                          ""
                                          "'{ 'action': add_event, 'params': 'summary': 'Physics class', "
                                          "'start': {'dateTime': '2024-11-23T11:00:00-07:00' }, "
                                          "'end': {'dateTime': '2024-11-23T12:00:00-07:00' }}}'. "
                                          "Except instead of single quotes as I used in the sample output, use double quotes"
             },

            {"role": "user", "content": user_input}
        ]
    )

    raw_content = response.choices[0].message.content
    print("Raw GPT response:", raw_content)
    print(type(raw_content))

    # Check if the response starts with the code block marker
    if raw_content.startswith("```"):
        # Removes both the starting "```python" and ending "```" markers
        cleaned_content = raw_content.replace("```python", "").replace("```", "").strip()
    else:
        # No markers, keep the raw content as it is
        cleaned_content = raw_content

    print(type(cleaned_content))

    try:
        return json.loads(cleaned_content)  # Parse the cleaned JSON content
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print("Cleaned Response content:", cleaned_content)
        return None


# user_input = "Schedule a meeting with John tomorrow at 10 AM"
# user_input = "I'll be going out with Liv at 10PM to the Hagia Sophia"
#user_input = "I have a 90min Maths test in 2 days at 9AM"

# Process the natural language command using GPT-4
# ai_output = process_natural_language_command(user_input)
# print("GPT-4 Output:", ai_output)

# Parse the GPT-4 output to determine the action and details
#action, title, date_time = parse_gpt_output(gpt_output)
#print(f"Action: {action}, Title: {title}, DateTime: {date_time}")

# Execute the corresponding calendar action
# execute_calendar_action(ai_output)


#|----------------------------- Flask Application | UI ----------------------------|

from flask import Flask, render_template, request, jsonify
import json
import time

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
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=5003)
