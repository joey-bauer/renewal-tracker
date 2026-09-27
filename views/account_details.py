import pandas as pd
import streamlit as st

from database import (
    add_custom_task,
    delete_account,
    delete_task,
    get_account_by_id,
    get_tasks_for_account,
    update_task_status,
)

def render_account_details(account_id):
    """Display an account and allow its tasks"""

    selected_account = get_account_by_id(account_id)
    
    # Handle cases where the selected account no longer exists
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

        if st.button("Back to Dashboard"):
            st.session_state.selected_account_id = None
            st.rerun()

        st.title(selected_account_name)
        st.write(f"**Renewal Date:** {selected_renewal_date}")

        # Load and display all renewal tasks for the selected account
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

            # Let the user edit task statuses directly in the table
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
                    "Task ID",
                    "Task",
                    "Due Date"
                ],
                use_container_width=True,
                hide_index=True,
                key=f"task_editor_{selected_account_id}"
            )

            # Save any status changes back to the database
            if st.button("Save Task Changes"):
                for task in edited_task_table.to_dict("records"):
                    update_task_status(
                        task["Task ID"],
                        task["Status"]
                    )

                st.success("Task changes saved.")
                st.rerun()

        # Allow the user to add a custom task to the selected account
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

        # Allow user to delete task (with confirmation)
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
                    "Delete Selected Task",
                    disabled=not confirm_task_delete,
                    key=f"delete_task_button_{selected_account_id}"
                ):
                    delete_task(task_to_delete[0])
                    st.rerun()

        # Allow the user to confirm and permanently delete the selected account
        st.divider()
        st.subheader("Delete Account")

        confirm_delete = st.checkbox(
            f"I understand that deleting {selected_account_name} "
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