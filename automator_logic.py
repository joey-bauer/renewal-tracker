from datetime import timedelta

def create_renewal_schedule(
    renewal_date,
    loss_run_days,
    exposure_workbook_days,
    submission_days,
    underwriter_days
):
    
    renewal_tasks = []

    for days in loss_run_days:
        renewal_tasks.append([
            "Order loss runs",
            renewal_date - timedelta(days=days)
        ])

    renewal_tasks.extend([
        ["Send Exposure Workbook to Client",renewal_date - timedelta(days=exposure_workbook_days)],
        ["Send Submissions",renewal_date - timedelta(days=submission_days)],
        ["Follow up with Underwriters",renewal_date - timedelta(days=underwriter_days)],
        ["Policy Renewal", renewal_date]
    ])

    renewal_tasks.sort(key=lambda task: task[1])

    return renewal_tasks