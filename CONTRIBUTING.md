# Contributing and code style

## Making changes (branches and PRs)

To make a change, fix an issue, or add a feature, follow the GitHub flow:

1. Make a branch for your work, e.g. `git checkout -b add-calendar-screen`
2. Make your changes :D
3. Test your changes?
4. Create a [pull request](https://github.com/makeitallproject/Make-It-All-Project/pulls) (from your branch to `main`)
5. Optionally, request code review from fellow teammates & act on review comments
6. When it's ready, merge your PR (ideally using "squash and merge", see screenshot below)

![Screenshot of "Squash and merge" in GitHub UI](https://cdn.hackclub.com/01a163dc-6149-73a5-8232-6064815f0aea/squash.png)

For more information on how to actually do this, you can read [GitHub flow - docs.github.com](https://docs.github.com/en/get-started/using-github/github-flow).

To ensure we can keep track of changes, try to keep to one feature/change per PR.

## File structure

Let's use `snake_case` for most file names (e.g. `home_screen.py`), unless there's convention otherwise (e.g. `README.md`).

It's also helpful to organise source code and other files into folders. Our folder structure:

- `assets` - Contains images and other assets used by the app
- `docs` - Documentation can go here
- `src` - Python source (`.py`) files go here
  - `screens` - Code for the different screens, e.g. `calendar.py`
  - ... (more subfolders can be created as required)

## Code style

Write good code. You know the drill - sensible variable names, functions, error handling, comments _if needed_, etc.

As for formatting, follow [PEP 8](https://peps.python.org/pep-0008/), which is the standard for Python code. I recommend using the [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) extension for VSCode, or another tool to automatically format your code.
