from datetime import date, datetime, timedelta

import streamlit as st

from database import (
    get_all_accounts,
    get_all_tasks,
    get_tasks_for_account
)

def calculate_account_progress(tasks):
    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks
        if task[3] == "Completed"
    )

    has_in_progress_tasks = any(
        task[3] == "In Progress"
        for task in tasks
    )

    if total_tasks == 0:
        account_status = "No Tasks"
    elif completed_tasks == total_tasks:
        account_status = "Completed"
    elif completed_tasks > 0 or has_in_progress_tasks:
        account_status = "In Progress"
    else:
        account_status = "Not Started"

    return account_status, completed_tasks, total_tasks

def render_dashboard():
    """Display all accounts and their renewal progress."""

    st.title("All Accounts")
    
    # Load account and task data for the dashboard summary
    accounts = get_all_accounts()
    all_tasks = get_all_tasks()
    
    today = date.today()

    overdue_tasks = 0
    upcoming_tasks = 0

    for(
        task_id,
        account_name,
        task_name,
        due_date,
        status
    ) in all_tasks:

        if status == "Completed":
            continue

        due_date_object = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date()

        if due_date_object < today:
            overdue_tasks += 1

        elif due_date_object <= today + timedelta(days=7):
            upcoming_tasks += 1

    # Display the summary across four dashboard columns
    (
        accounts_column,
        overdue_column,
        upcoming_column,
    ) = st.columns(3)

    accounts_column.metric(
        "Total Accounts",
        len(accounts)
    )

    overdue_column.metric(
        "Overdue Tasks",
        overdue_tasks
    )

    upcoming_column.metric(
        "Due Next 7 Days",
        upcoming_tasks
    )

    if not accounts:
        st.info("No accounts have been created yet.")
    else:
        account_table = []

        # Get each account's tasks and calculate its progress
        for account_id, account_name, renewal_date, created_at in accounts:
            tasks = get_tasks_for_account(account_id)

            (
                account_status,
                completed_tasks,
                total_tasks,
            ) = calculate_account_progress(tasks)

            account_table.append({
                "Account ID": account_id,
                "Account Name": account_name,
                "Renewal Date": renewal_date,
                "Status": account_status,
                "Tasks Completed": f"{completed_tasks}/{total_tasks}"
            })

        st.dataframe(
            account_table,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Account Details")

        # Create account buttons and store the selected account in session state
        for account_id, account_name, renewal_date, created_at in accounts:
            if st.button(
                f"{account_name} - Renewal: {renewal_date}",
                key=f"account_{account_id}"
            ):
                st.session_state.selected_account_id = account_id
                st.rerun()
