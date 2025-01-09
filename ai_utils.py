from calendar_utils import *
from main import *
import json
from datetime import datetime, timedelta, timezone
import pytz
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

    try:
        with open('db.json') as db:
            events_data = json.load(db)
    except (FileNotFoundError, json.JSONDecodeError):
        events_data = []  # fallback if no db file

    # Converts the events into a string, so we can embed them in our prompt
    events_data_str = json.dumps(events_data, indent=2)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You are the middleman between the user and "
                                          "their google calendar. Your role is - Interpret the user's natural-language "
                                          "input. - Return a single JSON object with two keys: 'action' and 'params'. "
                                          "Possible actions: 1. 'add_event' 2. 'upcoming_events' 3. 'delete_event'"
                                          "4. 'update_event' The 'params' object must contain the fields required by "
                                          "that action: - For 'add_event': { 'summary': 'string', "
                                          "'start': { 'dateTime': 'ISO 8601 date/time' }, "
                                          "'end': { 'dateTime': 'ISO 8601 date/time' }} If no end time is provided by "
                                          "the user, default to 1 hour after start. "
                                          "- For 'upcoming_events': Can be empty or can include 'max_results' etc. "
                                          "Example: { 'max_results': 5 } "
                                          "- For 'delete_event': { 'event_id': 'the unique Google Calendar event ID'}"
                                          "- For 'update_event': { 'event_id': 'the event ID to update',"
                                          " 'updated_data': { 'summary': '...', 'start': { 'dateTime': '...' }, "
                                          "'end':   { 'dateTime': '...' }}}"
                                          " Only include the fields in 'updated_data' that need changing. "
                                          "Your local timezone is Mountain Time (America/Denver). "
                                          f"Right now it's {datetime.today()}. "
                                          "Below is the user's current event database in JSON format "
                                          "(i.e., the upcoming events you know about). "
                                          f"You may use it to find event IDs or cross-reference event times: "
                                          f"{events_data_str}"
                                          "IMPORTANT:- Output *only* valid JSON—no extra commentary or code fencing."
                                          "- Use this form exactly: {'action': 'one of: add_event | upcoming_events | "
                                          "delete_event | update_event','params': { ... }}"
                                          "On all the spots I used single quotes I want you to use double quotes"
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

