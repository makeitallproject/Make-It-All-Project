"""Date and progress text shared by the task screens."""

from datetime import datetime


def format_date(day: datetime) -> str:
    """Short day and month, e.g. 4 Nov."""
    return f"{day.day} {day.strftime('%b')}"


def format_datetime(day: datetime) -> str:
    """Full date and time, e.g. 4 Nov 2026, 17:00."""
    return f"{day.day} {day.strftime('%b %Y, %H:%M')}"


def is_overdue(task: dict) -> bool:
    """An unfinished task is overdue once its due date has passed."""
    due = task.get("due")
    return due is not None and task.get("finished") is None and due < datetime.now()


def meta_text(task: dict) -> str:
    """Due or finished date, or an empty string when neither is set."""
    finished = task.get("finished")
    if finished is not None:
        return f"Done {format_date(finished)}"

    due = task.get("due")
    if due is None:
        return ""
    if is_overdue(task):
        return f"Overdue · {format_date(due)}"
    return f"Due {format_date(due)}"


def meta_tooltip(task: dict) -> str:
    """Full date for the compact text in meta_text."""
    finished = task.get("finished")
    if finished is not None:
        return f"Finished {format_datetime(finished)}"

    due = task.get("due")
    if due is None:
        return ""
    if is_overdue(task):
        return f"Was due {format_datetime(due)}"
    return f"Due {format_datetime(due)}"


def subtask_word(count: int) -> str:
    return "subtask" if count == 1 else "subtasks"


def progress_text(done: int, total: int) -> str:
    """Human-readable progress, e.g. 2 of 3 subtasks done."""
    return f"{done} of {total} {subtask_word(total)} done"
