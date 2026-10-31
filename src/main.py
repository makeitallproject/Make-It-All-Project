"""Entry point for the application"""

import signal
import sys

from PyQt6.QtWidgets import QApplication

from screens import calendar
from screens.login import LoginWindow


def main() -> int:
    # Make Ctrl+C in the terminal close the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("Make-It-All")

    # Initial window is login screen, then calendar screen
    window = LoginWindow()
    calendar_window = calendar.CalendarApp(window)
    calendar_window.hide()

    # For the prototype, we accept any username/password
    def on_login(username: str, _password: str) -> None:
        window.hide()
        calendar_window.set_user(username)
        calendar_window.showMaximized()

    # When login is clicked, go to the home screen (calendar)
    window.login_requested.connect(on_login)
    window.show()

    return app.exec()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
