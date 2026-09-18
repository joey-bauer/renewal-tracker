from datetime import datetime, timedelta
import csv

def choose_task_days(task_name, default_days):
    print()
    print(f"{task_name}:")
    print(f"1. Use the default of {default_days} days before renewal.")
    print(f"2. Enter a custom number of days")

    while True:
        choice = input("Choose option 1 or 2: ").strip()

        if choice == "1":
            return default_days
        elif choice == "2":
            while True:
                try:
                    custom_days = int(input("How many days before renewal? ").strip())

                    if custom_days > 0:
                        return custom_days
                    
                    print("Please enter a number greater than 0.")

                except ValueError:
                    print("Please enter a whole number, such as 75")
        else: 
            print("Invalid choice. Please enter 1 or 2.")

def choose_yes_or_no(question):
    while True:
        choice = input(f"{question} (yes/no): ").strip().lower()

        if choice in ["yes", "y"]:
            return True
        if choice in ["no", "n"]:
            return False
        print("Please enter yes or no.")

def choose_loss_run_days():
    print()
    print("Order loss runs:")
    print("You may select more than one option.")

    selected_days = []

    if choose_yes_or_no("Order loss runs 120 days before renewal?"):
        selected_days.append(120)

    if choose_yes_or_no("Order loss runs again 30 days before renewal?"):
        selected_days.append(30)

    if choose_yes_or_no("Add a custom loss run date?"):
        while True:
            try:
                custom_days = int(input("How many days before renewal? ").strip())

                if custom_days <= 0:
                    print("Please enter a number greater than 0")
                elif custom_days in selected_days:
                    print("That option has already been selected.")
                else:
                    selected_days.append(custom_days)
                    break
            except ValueError:
                print("Please enter a whole number, such as 75.")

    if not selected_days:
        print("You must select at least one loss run date.")
        return choose_loss_run_days()

    return selected_days

def create_renewal_schedule(
    renewal_date,
    loss_run_days,
    exposure_workbook_days,
    submission_days,
    underwriter_days
):
    renewal_tasks = []
    for days in loss_run_days:
        renewal_tasks.append(["Order loss runs", renewal_date - timedelta(days=days)])

    renewal_tasks.extend([
        ["Send Exposure Workbook to client", renewal_date - timedelta(days=exposure_workbook_days)],
        ["Send submissions", renewal_date - timedelta(days=submission_days)],
        ["Follow up with underwriters", renewal_date - timedelta(days=underwriter_days)],
        ["Policy renewal", renewal_date]
])

    renewal_tasks.sort(key=lambda task: task[1])

    return renewal_tasks

# Get the account name
while True:
    account_name = input("Enter the account name: ").strip()

    if account_name:
        break
    print("Account name cannot be empty.")

# Get the renewal date
while True:
    renewal_date_text = input("Enter the renewal date (YYYY-MM-DD): ").strip()

    try:
        renewal_date = datetime.strptime(
            renewal_date_text,
            "%Y-%m-%d"
        )
        break
    except ValueError:
        print("Invalid date. Please use YYYY-MM-DD, such as 2026-01-01.")

# Choose the loss run dates
loss_run_days = choose_loss_run_days()

# Choose the number of days for the other tasks
exposure_workbook_days = choose_task_days("Send Exposure Workbook to client", 90)
submission_days = choose_task_days("Send submissions", 60)
underwriter_days = choose_task_days("Follow up with underwriters", 30)

# Create renewal schedule
renewal_tasks = create_renewal_schedule(
    renewal_date,
    loss_run_days,
    exposure_workbook_days,
    submission_days,
    underwriter_days
)

# Display the schedule
print()
print(f"Renewal schedule for {account_name}")

for task_name, task_date in renewal_tasks:
    print(f"{task_name}: {task_date.strftime('%Y-%m-%d')}")

# Save the schedule
with open("renewal_tracker.csv", "a", newline="") as file:
    writer = csv.writer(file)

    for task_name, task_date in renewal_tasks:
        writer.writerow([
            account_name,
            task_name,
            task_date.strftime("%Y-%m-%d"),
            "Not started"
        ])



print()
print(f"Renewal schedule saved successfully!")