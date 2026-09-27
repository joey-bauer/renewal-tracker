TASK_STYLES = {
    "Order loss runs": {
        "label": "Loss runs",
    },
    "Send Exposure Workbook to Client": {
        "label": "Workbook",
    },
    "Send Submissions": {
        "label": "Submission",
    },
    "Follow up with Underwriters": {
        "label": "Follow-up",
    },
    "Policy Renewal": {
        "label": "Renewal",
    },
}

def get_task_style(task_name):
    """Return a short label for a calendar task."""
    return TASK_STYLES.get(
        task_name,
        {"label": task_name},
    )