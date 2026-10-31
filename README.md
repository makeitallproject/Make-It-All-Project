# Make-It-All Project

> We must make this software; we must Make It All.

## Usage

### Requirements

- [Python](https://www.python.org/downloads/) (3.12 or newer)
- [uv](https://docs.astral.sh/uv/) (recommended)

### Option 1: run with `uv`

This is the easiest option. If you have `uv` installed, just run:

```bash
uv run make-it-all
```

### Option 2: make a virtual environment

If you don't want to use `uv`, you can make a virtual environment and use `pip`.

On Linux:

```bash
# Create virtual environment
python -m venv .venv
# Activate virtual environment
source .venv/bin/activate
# Install dependencies and enable the make-it-all command
pip install -e .
# Run the project
make-it-all
```

Or on Windows:

```powershell
# Create virtual environment
py -m venv .venv
# Activate it
.venv\Scripts\activate
# Install dependencies
py -m pip install -e .
# Run the project
make-it-all
```

### Option 3: without a virtual environment

If you already have `PyQt6` installed and you just want to run the program, you can. On Windows:

```powershell
py src/main.py
```

### Test the screens

Each screen can also be run on its own for quick previews, e.g.

```bash
# View the calendar screen
uv run src/screens/calendar.py
# View the kanban (board) screen
uv run src/screens/kanban.py
# View the forum (knowledge sharing) screen
uv run src/screens/forum.py
```

## Development and contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for information on development, code style, and project guidelines.
