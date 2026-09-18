# Renewal Tracker

A Python-based renewal workflow application designed to help commercial insurance professionals organize and track the renewal process.

After developing an interest in learning Python and software creation fundamentals, I decided that I could hone my skills through creating something that would eventually help everyday commercial broker workflows. 
One recurring inconvenience I noticed is keeping standard dates and follow-ups organized across multiple accounts and renewal dates. The goal was to create a tool that could seamlessly upload important renewal dates and reminders to your calendar. A more advanced version would then upload these items directly to outside calendar software.
This project started as a command-line tool that generated renewal task dates, and has now evolved into a database-backed Streamlit application.

## Current Features
- Automated renewal schedules:
    Generates renewal tasks based on the account's renewal date and user determined lead times
- Account Management:
    Create and manage specific accounts and schedules
- Task Managment:
    Track renewal update and delete specific and standardized tasks across all accounts
- Progress Tracking
    Display current progress specific to the tasks and dates for each account
- Calendar
    View tasks in both list and monthly calendar formats
- CSV export
    Download renewal schedules for outside excel use
- Persistent Storage
    Use SQLite to store account data between application sessions

## Tech Stack
- Python
- Streamlit
- SQLite
- Pandas

## Project Software
- app.py
- database.py
- automator_logic.py
- renewal_tracker_cli.py

## Running Locally
- Clone repository
- Create virtual environment
- Install requirements
- Run Streamlit

## Project Development
- CLI prototype -> Streamlit -> SQLite -> current v1

## Future Development
Next steps would be talking to potential users, implementing UI, and developing API connection to outside software calendar applications like Outlook, Slack, Google, etc.
- User Feedback:
    The most useful next step would be gathering feedback from commercial insurance professionals to determine which features provide the most benefit. The goal is for it to save a broker some time, and keeping their schedule organized, but I want to make sure that it operates smoothly and does not feel like another task.
- Implementing UI:
    As it stands, the app is currently in default Streamlit format. Developing a professional and clean interface would provide more appeal. Eventual recreation in React and node.js would provide more creative options as well.
- API Progression:
    The best form of this app would most likely allow the user or AI to input account information which would then automatically update the user's calendar in any outside software.
    Ex. you assign accounts to a new AMs and their schedule auto populates important dates for each account. These dates can then be customized via the app or the calendar itself.