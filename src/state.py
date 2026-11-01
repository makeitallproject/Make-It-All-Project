"""Shared in-memory state for the prototype"""

from datetime import datetime

DEMO_USER = "Demo User"

_current_user = ""
_listeners = []


def get_user() -> str:
    """Return the signed-in user, or the demo user before login."""
    return _current_user or DEMO_USER


def set_user(user: str) -> None:
    """Remember the signed-in user for every screen."""
    global _current_user
    _current_user = user or ""


def is_completed(task: dict) -> bool:
    """A task is complete if it was marked done or sits in the Done column."""
    return task.get("completed", False) or task.get("column") == "Done"


def build_task(
    name: str,
    column: str,
    assignee: str | None = None,
    due: datetime | None = None,
    finished: datetime | None = None,
    subtasks: list[dict] | None = None,
) -> dict:
    """Build one task."""
    return {
        "name": name,
        "notes": "",
        "assignee": assignee,
        "due": due,
        "finished": finished,
        "column": column,
        "completed": column == "Done",
        "subtasks": [
            {"name": subtask["name"], "completed": subtask["completed"]}
            for subtask in subtasks or []
        ],
    }


tasks = [
    build_task(
        "Set up CI pipeline",
        "To Do",
        assignee="Tobi",
        due=datetime(2026, 11, 4, 17, 0),
        subtasks=[
            {"name": "Install GitHub Actions", "completed": False},
            {"name": "Add lint step", "completed": False},
        ],
    ),
    build_task(
        "Write project README",
        "To Do",
        assignee="Mish",
        due=datetime(2026, 11, 2, 12, 0),
    ),
    build_task(
        "Audit keyboard navigation across the calendar and forum screens",
        "To Do",
        assignee="Charles",
        due=datetime(2026, 11, 7, 9, 30),
        subtasks=[
            {"name": "List screens that need testing", "completed": True},
            {"name": "Document focus order", "completed": False},
            {"name": "Test with keyboard only", "completed": False},
        ],
    ),
    build_task(
        "Collect requirements from each team",
        "To Do",
        due=datetime(2026, 11, 10, 16, 0),
    ),
    build_task(
        "Document the printer setup for new starters",
        "To Do",
        assignee="Louis",
        due=datetime(2026, 11, 12, 11, 0),
        subtasks=[
            {"name": "Photograph the printer panel", "completed": False},
            {"name": "Add paper refill steps", "completed": False},
        ],
    ),
    build_task(
        "Design database schema",
        "In Progress",
        assignee="Kipras",
        due=datetime(2026, 10, 30, 15, 0),
        subtasks=[
            {"name": "Draft ER diagram", "completed": True},
            {"name": "Normalize tables", "completed": False},
        ],
    ),
    build_task(
        "Polish the forum reader pane",
        "In Progress",
        assignee="Mish",
        due=datetime(2026, 11, 1, 10, 0),
        subtasks=[
            {"name": "Fix long post titles", "completed": True},
            {"name": "Keep the reading measure at 700px", "completed": True},
            {"name": "Add paragraph spacing", "completed": False},
        ],
    ),
    build_task(
        "Wire up the task creation form",
        "In Progress",
        assignee="Evan",
        due=datetime(2026, 11, 3, 14, 30),
    ),
    build_task(
        "Replace hardcoded colours in the calendar stylesheet",
        "In Progress",
        assignee="Kipras",
        due=datetime(2026, 11, 5, 13, 0),
        subtasks=[
            {"name": "Audit hardcoded colours", "completed": False},
            {"name": "Use palette roles", "completed": False},
        ],
    ),
    build_task(
        "Scaffold repository",
        "Done",
        assignee="Tobi",
        finished=datetime(2026, 10, 20, 16, 45),
        subtasks=[
            {"name": "Init git repo", "completed": True},
            {"name": "Add pyproject.toml", "completed": True},
        ],
    ),
    build_task(
        "Build the forum screen",
        "Done",
        assignee="Mish",
        finished=datetime(2026, 10, 29, 17, 30),
        subtasks=[
            {"name": "Topic rail", "completed": True},
            {"name": "Post feed", "completed": True},
            {"name": "Reader pane", "completed": True},
        ],
    ),
    build_task(
        "Add the shared avatar widget",
        "Done",
        assignee="Kipras",
        finished=datetime(2026, 10, 27, 11, 15),
    ),
    build_task(
        "Move shared widgets into src/widgets",
        "Done",
        assignee="Mish",
        finished=datetime(2026, 10, 28, 15, 20),
        subtasks=[
            {"name": "Create widgets package", "completed": True},
        ],
    ),
    build_task(
        "Finish Team Project",
        "To Do",
        due=datetime(2026, 10, 30, 17, 0),
    ),
    build_task(
        "Team networking event",
        "Done",
        due=datetime(2026, 10, 18, 18, 0),
    ),
]


def add_task(task: dict) -> None:
    """Add a task to the shared store and tell every screen about it."""
    tasks.append(task)
    notify_changed()


def remove_task(task: dict) -> None:
    """Remove a task from the shared store and tell every screen."""
    tasks.remove(task)
    notify_changed()


def subscribe(listener) -> None:
    """Register a callback that runs whenever the task store changes."""
    _listeners.append(listener)


def unsubscribe(listener) -> None:
    """Stop calling a previously registered callback."""
    if listener in _listeners:
        _listeners.remove(listener)


def notify_changed() -> None:
    """Tell every registered screen that the task store changed."""
    for listener in list(_listeners):
        listener()
