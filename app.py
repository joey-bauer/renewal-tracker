import csv
import io
import re

import streamlit as st

from automator_logic import create_renewal_schedule
from database import (
    add_account, 
    add_tasks,
    get_all_accounts,
    get_tasks_for_account,
    initialize_database
    )

initialize_database()

page = st.sidebar.radio(
    "Navigation",
    ["Create Schedule", "All Accounts"]
)

if page == "Create Schedule":

    st.title("Renewal Tracker")
    st.write(
        "Create, organize, and export renewal schedules for your accounts."
    )

    account_name = st.text_input("Account Name")
    renewal_date = st.date_input("Renewal Date")

    st.subheader("Loss Runs")

    loss_run_options = st.multiselect(
        "When should loss runs be ordered?",
        options=[120, 90, 60, 30],
        default=[120, 30],
        format_func=lambda days: f"{days} days before renewal"
    )

    add_custom_loss_run = st.checkbox("Add a custom loss run date")

    custom_loss_run_days = None

    if add_custom_loss_run:
        custom_loss_run_days = st.number_input(
            "Custom number of days before renewal",
            min_value=1,
            value=75,
            step=1
        )

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

    if st.button("Create Schedule", type="primary"):

        selected_loss_run_days = loss_run_options.copy()

        if (add_custom_loss_run 
            and custom_loss_run_days not in selected_loss_run_days
        ):
            selected_loss_run_days.append(custom_loss_run_days)

        if not account_name.strip():
            st.error("Please enter an account name.")
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

            st.success(f"Renewal schedule created for {account_name}.")

            st.subheader("Renewal schedule")

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

elif page == "All Accounts":
    st.title("All Accounts")

    accounts = get_all_accounts()

    if not accounts:
        st.info("No accounts have been created yet.")
    else:
        account_table = []

        for account_id, account_name, renewal_date, created_at in accounts:
            account_table.append({
                "Account ID": account_id,
                "Account Name": account_name,
                "Renewal Date": renewal_date,
                "Created At": created_at
            })

        st.dataframe(
            account_table,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Account Details")

        selected_account = st.selectbox(
            "Select an account",
            options=accounts,
            format_func=lambda account:(
                f"{account[1]} - Renewal: {account[2]}"
            )
        )

        selected_account_id = selected_account[0]
        selected_account_name = selected_account[1]
        selected_renewal_date = selected_account[2]

        st.write(f"**Account:** {selected_account_name}")
        st.write(f"**Renewal Date:** {selected_renewal_date}")

        tasks = get_tasks_for_account(selected_account_id)

        if not tasks:
            st.info("No tasks have been saved for this account.")
        else:
            task_table = []

            for task_id, task_name, due_date, status in tasks:
                task_table.append({
                    "Task": task_name,
                    "Due Date": due_date,
                    "Status": status
                })

            st.dataframe(
                task_table,
                use_container_width=True,
                hide_index=True
            )