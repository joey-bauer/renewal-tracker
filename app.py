import csv
import io
import re
import pandas as pd

import streamlit as st

from automator_logic import create_renewal_schedule
from database import (
    add_account, 
    account_exists,
    add_custom_task,
    add_tasks,
    delete_account,
    delete_task,
    get_account_by_id,
    get_all_accounts,
    get_tasks_for_account,
    initialize_database,
    update_task_status
    )

initialize_database()

def calculate_account_progress(tasks):
    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for task in tasks
        if task[3] == "Completed"
    )

    if total_tasks == 0:
        account_status = "No Tasks"
    elif completed_tasks == total_tasks:
        account_status = "Competed"
    elif completed_tasks > 0:
        account_status = "In Progress"
    else:
        account_status = "Not Started "

    return account_status, completed_tasks, total_tasks

if "selected_account_id" not in st.session_state:
    st.session_state.selected_account_id = None

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Account", "Calendar"]
)

if page == "Add Account":

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

            st.success(f"Renewal schedule created for {account_name}.")

            st.subheader("Renewal Schedule")

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

elif (
    page == "Dashboard"
    and st.session_state.selected_account_id is None
):
    st.title("All Accounts")

    accounts = get_all_accounts()

    if not accounts:
        st.info("No accounts have been created yet.")
    else:
        account_table = []

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

        for account_id, account_name, renewal_date, created_at in accounts:
            if st.button(
                f"{account_name} - Renewal: {renewal_date}",
                key=f"account_{account_id}"
            ):
                st.session_state.selected_account_id = account_id
                st.rerun()

elif (
    page == "Dashboard"
    and st.session_state.selected_account_id is not None
):
    selected_account = get_account_by_id(st.session_state.selected_account_id)

    if selected_account is None:
        st.error("This account could not be found.")

        if st.button("Back to Dashboard"):
            st.session_state.selected_account_id = None
            st.rerun()

    else:
        (
            selected_account_id,
            selected_account_name,
            selected_renewal_date,
            selected_created_at
        ) = selected_account

        if st.button  ("Back to Dashboard"):
            st.session_state.selected_account_id = None
            st.rerun()

        st.title(selected_account_name)
        st.write(f"**Renewal Date:** {selected_renewal_date}")
        
        st.subheader("Renewal Tasks")

        tasks = get_tasks_for_account(selected_account_id)

        if not tasks:
            st.info("No tasks have been saved for this account.")

        else:
            task_table = []

            for task_id, task_name, due_date, status in tasks:
                task_table.append({
                    "Task ID": task_id,
                    "Task": task_name,
                    "Due Date": due_date,
                    "Status": status
                })

            task_dataframe = pd.DataFrame(task_table)

            edited_task_table = st.data_editor(
                task_dataframe,
                column_config={
                    "Task ID": None,
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options= [
                            "Not Started",
                            "In Progress",
                            "Completed"
                        ],
                        required=True
                    )
                },
                disabled=[
                    "Tasks ID",
                    "Task",
                    "Due Date"
                ],
                use_container_width=True,
                hide_index=True,
                key=f"task_editor_{selected_account_id}"
            )

            if st.button("Save Task Changes"):
                for task in edited_task_table.to_dict("records"):
                    update_task_status(
                        task["Task ID"],
                        task["Status"]
                    )

                st.success("Task changes saved.")
                st.rerun()

                if st.button(
                    "Delete Selected Task",
                    disabled=not confirm_task_delete,
                    key=f"delete_task_button_{selected_account_id}"
                ):
                    delete_task(task_to_delete[0])
                    st.rerun()

        with st.expander("Add a Custom Task"):
            with st.form(
                key=f"add_task_form_{selected_account_id}",
                clear_on_submit=True
            ):
                custom_task_name = st.text_input("Task Name")
                custom_task_due_date = st.date_input("Due Date")

                add_task_submitted = st.form_submit_button(
                    "Add Task"
                )

                if add_task_submitted:
                    if not custom_task_name.strip():
                        st.error("Please enter a task name.")
                    else:
                        add_custom_task(
                            selected_account_id,
                            custom_task_name.strip(),
                            custom_task_due_date
                        )

                        st.rerun()

        if tasks:
            with st.expander("Delete a Task"):
                task_to_delete = st.selectbox(
                    "Select the task to delete",
                    options=tasks,
                    format_func=lambda task: (
                        f"{task[1]} - Due: {task[2]}"
                    ),
                    key=f"delete_task_select_{selected_account_id}"
                )

                confirm_task_delete = st.checkbox(
                    "I understand this task will be permanently deleted.",
                    key=f"confirm_task_delete_{selected_account_id}"
                )

                if st.button(
                    "Delete Seleceted Task",
                    disabled=not confirm_task_delete,
                    key=f"delete_task_button_{selected_account_id}"
                ):
                    delete_task(task_to_delete[0])
                    st.rerun()

        st.divider()
        st.subheader("Delete Account")

        confirm_delete = st.checkbox(
            f"I understand that adeleting {selected_account_name} "
            "will also delete all of its tasks.",
            key=f"confirm_delete_{selected_account_id}"
        )

        if st.button(
            "Delete Account",
            type="secondary",
            disabled=not confirm_delete
        ):
            delete_account(selected_account_id)

            st.session_state.selected_account_id = None

            st.rerun()

elif page == "Calendar":
    st.title("Calendar")
    st.info("The renewal calendar will be added here.")