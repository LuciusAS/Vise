This is a project that integrates a chat-like web interface with an LLM (e.g., OpenAI’s GPT) and Google Calendar.
You can type natural-language commands (e.g., “What do I have coming up?” or “Schedule a meeting tomorrow at 2 PM”) 
and the system will interpret them, then add/update/delete events from your Google Calendar.

Features

  Chat UI: Simple messaging interface (like texting) using HTML, CSS, and a bit of JavaScript.
  LLM-powered commands: Natural-language parsing to figure out what the user wants to do with their calendar.
  Google Calendar Integration:
  Add Events
  List Upcoming Events
  Update Events
  Delete Events

Quick Start

  Install: 
  git clone https://github.com/LuciusAS/Vise.git
  cd LuciusAS/Vise
  pip install -r requirements.txt
  
  Set up Google APIs and Keys:
  Set Up Google API & Keys
  
  Place your credentials.json (Google OAuth credentials) in the project folder.
  Make a .env file with your OpenAI API key and a Flask SECRET_KEY:
  
  OPENAI_API_KEY=YourOpenAIkey
  SECRET_KEY=some-secret-key

Run the App

  python main.py

On the first run you'll be asked to authenticate your Google account
Open http://127.0.0.1:5003 in your browser.

Usage

  Type a natural-language request (e.g., “What do I have coming up?”)
  Send the request.
  Vise will respond in the same interface, showing results or confirmation.

