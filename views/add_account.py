import csv
import io
import re

import streamlit as st

from automator_logic import create_renewal_schedule
from database import account_exists, add_account, add_tasks

def render_add_account():
    """Display the account form and save its renewal schedule."""

    st.title("Renewal Tracker")

    account_name = st.text_input("Account Name")
    renewal_date = st.date_input("Renewal Date")

    st.subheader("Loss Runs")

    loss_run_options = st.multiselect(
        "When should loss runs be ordered?",
        options=[120, 90, 60, 30],
        default=[120, 30],
        format_func=lambda days: f"{days} days before renewal"
    )

    # Give the user the option to add an additional
    # custom loss run date.
    add_custom_loss_run = st.checkbox("Add a custom loss run date")

    custom_loss_run_days = None

    # Only show the number input if the checkbox is selected.
    if add_custom_loss_run:
        custom_loss_run_days = st.number_input(
            "Custom number of days before renewal",
            min_value=1,
            value=75,
            step=1
        )

    # Let the user control how many days before renewal
    # each major renewal task should be done.
    st.subheader("Other Renewal Tasks")

    exposure_workbook_days = st.number_input(
        "Send Exposure Workbook to Client",
        min_value=1,
        value=90,
        step=1
    )

    submission_days = st.number_input(
        "Send Submission",
        min_value=1,
        value=60,
        step=1
    )

    underwriter_days = st.number_input(
        "Follow up with Underwriters",
        min_value=1,
        value=30,
        step=1
    )

    # When the user clicks Create Schedule, validate the inputs,
    # save the account, generate its renewal tasks,
    # and save those tasks to the database.
    if st.button("Create Schedule", type="primary"):

        selected_loss_run_days = loss_run_options.copy()

        if (
            add_custom_loss_run 
            and custom_loss_run_days not in selected_loss_run_days
        ):
            selected_loss_run_days.append(custom_loss_run_days)

        if not account_name.strip():
            st.error("Please enter an account name.")
        elif account_exists(account_name.strip()):
            st.error("An account with this name already exists.")
        elif not selected_loss_run_days:
            st.error("Please select at least one loss run date.")
        else:
            account_id = add_account(
                account_name.strip(),
                renewal_date
            )
            renewal_tasks = create_renewal_schedule(
                renewal_date,
                selected_loss_run_days,
                exposure_workbook_days,
                submission_days,
                underwriter_days
            )

            add_tasks(account_id, renewal_tasks)

            # Show the newly created renewal schedule to the user
            # and prepare a downloadable CSV version of it.
            st.success(f"Renewal schedule created for {account_name}.")

            st.subheader("Renewal Schedule")

            # Convert the renewal task tuples into dictionaries
            # so Streamlit can display them as a clean table.
            schedule_table = []

            for task_name, task_date in renewal_tasks:
                schedule_table.append({
                    "Task": task_name,
                    "Due Date": task_date.strftime("%B %d %Y"),
                    "Status": "Not Started"
                })

            st.dataframe(
                schedule_table,
                use_container_width=True,
                hide_index=True
            )

        # Build CSV version of the schedule in memory and allow user to download.
            # Create a temporary text file in memory
            # that we can write CSV data into.
            csv_file = io.StringIO()

            fieldnames = [
                "Account Name",
                "Task",
                "Due Date",
                "Status"
            ]

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for task_name, task_date in renewal_tasks:
                writer.writerow({
                    "Account Name": account_name.strip(),
                    "Task": task_name,
                    "Due Date": task_date.strftime("%Y-%m-%d"),
                    "Status": "Not Started"
                })

            # Clean the account name so it can safely be used
            # as part of the downloaded CSV filename.
            safe_account_name = re.sub(
                r"[^a-zA-Z0-9]+",
                "_",
                account_name.strip()
            ).strip("_").lower()

            csv_filename = f"{safe_account_name}_renewal_schedule.csv"

            st.download_button(
                label="Download schedule as CSV",
                data=csv_file.getvalue(),
                file_name=csv_filename,
                mime="text/csv",
                on_click="ignore"
            )
