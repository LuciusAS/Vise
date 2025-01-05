Jarvis: GPT + Google Calendar Integration
This project integrates an LLM (Large Language Model) with the Google Calendar API,
allowing you to issue natural-language commands like “Show me my upcoming events” 
or “Schedule a meeting tomorrow at 10 AM” and have them executed automatically on your Google Calendar. 
It uses Python, Flask, and the OpenAI Python library.

Features
Natural Language Interface

Leverages an LLM (such as GPT-4o-mini) to parse user commands into structured JSON.
Google Calendar Actions

Add Event: Create new calendar events with optional start/end time.
List Upcoming Events: Fetch upcoming events from your primary calendar.
Update Event: Modify existing events (change title, time, etc.).
Delete Event: Remove events using their unique calendar event ID.
Flask-Based Web Interface

Simple HTML form to input commands.
Displays response messages directly on the page.
Token Management and OAuth 2.0

Refreshes Google OAuth tokens automatically.
Prompts you for re-authentication if the token expires.

Requirements
Python 3.8+
A Google Cloud Project with Calendar API enabled
A valid credentials.json (OAuth 2.0 Client ID)
An OpenAI API key (for GPT usage)
Installation
Clone the Repository

bash
Copy code
git clone https://github.com/LuciusAS/Vise.git
cd Vise
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Set Up Environment Variables
Create a file called .env in the project root and add your secrets:

makefile
Copy code
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=some_flask_secret
Add Google OAuth Credentials

Download credentials.json from your Google Cloud Console (make sure you’ve enabled the Google Calendar API).
Place credentials.json in the project root (ignore/omit from version control).

Usage
Run the Flask App

bash
Copy code
python main.py
Authenticate with Google Calendar

On the first run, the app will prompt you to sign in with your Google account.
It will save the access token in token.json.
Access the Web Interface

Open http://127.0.0.1:5003/ in your web browser.
Enter natural-language commands, such as:
What do I have coming up?
Schedule a meeting with John tomorrow at 9 AM
Delete my appointement 
The meeting with John will be at 11am
Review Responses

The responses will appear in the same webpage.
For “upcoming events,” it displays a formatted list (or “No upcoming events found.”).

How It Works
Flask Route:

POST /process in main.py handles the user’s text input (user_input).
LLM Prompt:

The text is sent to the process_natural_language_command function, which builds a prompt instructing GPT how to respond with valid JSON ({"action": ..., "params": {...}}).
Action Execution:

The JSON output is parsed by execute_calendar_action, which calls the appropriate function:
get_upcoming_events(calendar_service)
add_event(...)
delete_event(...)
update_event(...)
Google Calendar:

The googleapiclient.discovery library sends requests to the Calendar API using the user’s OAuth token.
If the token is expired or invalid, the app refreshes or re-authenticates.
