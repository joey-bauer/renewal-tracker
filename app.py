# Built-in Python modules used for CSV creation,
# text handling, account name cleanup, and calendar calculations.
import csv
import io
import re
import calendar

# Third party libraries used for tables and the web interface.
import pandas as pd
import streamlit as st

# Date tools used throughout the app.
from datetime import datetime, date, timedelta

# Project functions.
from automator_logic import create_renewal_schedule
from views.add_account import render_add_account
from views.dashboard import render_dashboard
from views.account_details import render_account_details
from views.calendar_view import render_calendar_view

from database import(
    add_account, 
    account_exists,
    add_custom_task,
    add_tasks,
    delete_account,
    delete_task,
    get_account_by_id,
    get_all_accounts,
    get_all_tasks,
    get_tasks_for_account,
    initialize_database,
    update_task_status
    )


def load_css(file_path):
    with open(file_path, encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True
        )


# Configure the overall Streamlit page.
st.set_page_config(
    page_title="Renewal Tracker",
    page_icon="📅",
    layout="wide"
)


load_css("styles.css")

# Override Streamlit's default page margins so the calendar
# can use more of the available screen width
st.markdown(
    """
    <style>
        .block-container {
            max-width: 100%;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Create the SQLite tables if they do not already exist
initialize_database()

# Store which account the user has selected.
# None means the user is currently viewing the main Dashboard.
if "selected_account_id" not in st.session_state:
    st.session_state.selected_account_id = None

# Create the sidebar navigation and store the selected page
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Account", "Calendar"]
)

# -----------------------
# ADD ACCOUNT PAGE
# -----------------------
if page == "Add Account":
    render_add_account()
    
# Display all accounts and their overall renewal progress
elif (
    page == "Dashboard"
    and st.session_state.selected_account_id is None
):
    render_dashboard()

# Display the selected account and its renewal details
elif (
    page == "Dashboard"
    and st.session_state.selected_account_id is not None
):  
    render_account_details(st.session_state.selected_account_id)

# Display all renewal tasks in list and monthly calendar views          
elif page == "Calendar":
    render_calendar_view()
    