import calendar
from html import escape
from datetime import date, datetime, timedelta

import streamlit as st

from database import get_all_tasks

from views.calendar_helpers import get_task_style

def render_calendar_view():
    """Display renewal tasks in list and monthly calendar views."""

    st.title("Renewal Calendar")
    
    task_list_tab, month_view_tab = st.tabs([
        "Task List",
        "Month View"
    ])

    all_tasks = get_all_tasks()

    # Build a task list showing each task's timing relative to today
    with task_list_tab:
            if not all_tasks:
                st.info("No renewal tasks have been created yet.")

            else:
                calendar_table = []
                today = date.today()

                for (
                    task_id,
                    account_name,
                    task_name,
                    due_date,
                    status
                ) in all_tasks:

                    due_date_object = datetime.strptime(
                        due_date,
                        "%Y-%m-%d"
                    ).date()

                    # Categorize each task based on its status and due date
                    if status == "Completed":
                        timing = "🟢 Completed"

                    elif due_date_object < today:
                        timing = "🔴 Overdue"

                    elif due_date_object == today:
                        timing = "🟠 Due Today"

                    elif due_date_object <= today + timedelta(days=7):
                        timing = "🟡 Due Soon"

                    else:
                        timing = "🔵 Upcoming"

                    calendar_table.append({
                        "Account": account_name,
                        "Task": task_name,
                        "Due Date": due_date_object,
                        "Status": status,
                        "Timing": timing
                    })

                st.dataframe(
                    calendar_table,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Due Date": st.column_config.DateColumn(
                            "Due Date",
                            format="MMM D, YYYY"
                        ),
                        "Status": st.column_config.TextColumn(
                            "Status"
                        ),
                        "Timing": st.column_config.TextColumn(
                            "Timing"
                        )
                    }
                )

    # Build the monthly calendar view and let the user choose a month and year
    with month_view_tab:
        today = date.today()

        month_column, year_column = st.columns(2)

        with month_column:
            selected_month_name = st.selectbox(
                "Month",
                list(calendar.month_name)[1:],
                index=today.month - 1
            )

        with year_column:
            selected_year = st.number_input(
                "Year",
                min_value=2020,
                max_value=2100,
                value=today.year,
                step=1
            )

        selected_month = list(
            calendar.month_name
        ).index(selected_month_name)

        st.subheader(
            f"{selected_month_name} {selected_year}"
        )

        # Create and display the seven weekday columns
        weekday_names = [
            "Sunday",   
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]

        weekday_columns = st.columns(7)

        for column, weekday_name in zip(
            weekday_columns,
            weekday_names
        ):
            column.markdown(
                f'<div style="text-align: center; font-weight: 700;">{weekday_name}</div>',
                unsafe_allow_html=True,
            )

        # generate the weeks and days for the selected month
        sunday_calendar = calendar.Calendar(
            firstweekday=calendar.SUNDAY
        )

        month_weeks = sunday_calendar.monthdayscalendar(
            int(selected_year),
            selected_month
        )

        # Group all renewal tasks by their due date for calendar placement
        tasks_by_date = {}

        for (
            task_id,
            account_name,
            task_name,
            due_date,
            status
        ) in all_tasks:

            task_due_date = datetime.strptime(
                due_date,
                "%Y-%m-%d"
            ).date()

            tasks_by_date.setdefault(
                task_due_date,
                []
            ).append({
                "task_id": task_id,
                "account_name": account_name,
                "task_name": task_name,
                "status": status
            })

        # Build each week and day cell in the monthly calendar
        for week in month_weeks:
            day_columns = st.columns(7)

            for column, day_number in zip(
                day_columns,
                week
            ):
                with column:
                    if day_number == 0:
                        with st.container(
                            height=140,
                            border=False
                        ):
                            st.write("")

                    else:
                        calendar_date = date(
                            int(selected_year),
                            selected_month,
                            day_number
                        )

                        tasks_for_day = tasks_by_date.get(
                            calendar_date,
                            []
                        )

                        with st.container(
                            height=140,
                            border=True,
                            key=f"calendar_tile_{selected_year}_{selected_month}_{day_number}"
                        ):  
                            st.markdown(f"**{day_number}**")

                            # Display each day's tasks with status indicator
                            for task in tasks_for_day:
                                if task["status"] == "Completed":
                                    status_icon = "🟢"
                                    task_color = "#2E8B57"

                                elif calendar_date < date.today():
                                    status_icon = "🔴"
                                    task_color = "#D64545"

                                elif calendar_date == date.today():
                                    status_icon = "🟠"
                                    task_color = "#E58220"

                                elif calendar_date <= (
                                    date.today() + timedelta(days=7)
                                ):
                                    status_icon = "🟡"
                                    task_color = "#D4AC0D"

                                else:
                                    status_icon = "🔵"
                                    task_color = "#357ABD"

                                style = get_task_style(task["task_name"])

                                account_name = escape(task["account_name"])
                                task_label = escape(style["label"])

                                st.markdown(
                                    f"""
                                    <div class="calendar-task"
                                        style="border-left-color: {task_color};">
                                        <div>{status_icon} <strong>{account_name}</strong></div>
                                        <div>{task_label}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
