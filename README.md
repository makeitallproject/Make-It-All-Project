# Make-It-All Project

> We must make this software; we must Make It All.

## Usage

### Requirements

- [Python](https://www.python.org/downloads/) (3.12 or newer)
- [uv](https://docs.astral.sh/uv/)

### Test the screens

```bash
# View the login screen, this is the entry point of the program
uv run src/screens/login_screen.py
# View the calendar screen (cannot be directly viewed currently, go through the login page instead)
uv run src/screens/calendar.py
# View the kanban (board) screen
uv run src/screens/kanban.py
# View the forum (knowledge sharing) screen
uv run src/screens/forum.py
# View the task creation screen
uv run src/screens/task.py
```

## Development and contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for information on development, code style, and project guidelines.
