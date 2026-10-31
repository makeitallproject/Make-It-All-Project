"""A small round badge showing the initials of a person or topic."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel


def get_initials(name: str) -> str:
    """Return up to two initials of a name"""
    words = name.split()
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


class Avatar(QLabel):
    """A circular label with initials, sized to fit wherever it is used."""

    def __init__(self, name: str, size: int = 32, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: palette(midlight);
                color: palette(text);
                border-radius: {size // 2}px;
                font-size: {max(10, size // 3)}px;
                font-weight: bold;
            }}
            """
        )
        self.set_name(name)

    def set_name(self, name: str) -> None:
        """Update the badge when the person or topic changes."""
        self.setText(get_initials(name))
        self.setAccessibleName(f"{name} avatar")
