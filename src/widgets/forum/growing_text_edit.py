from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPlainTextEdit

MIN_HEIGHT = 72
MAX_HEIGHT = 240
MAX_WINDOW_FRACTION = 0.30


class GrowingTextEdit(QPlainTextEdit):
    """Text box that gets taller as more lines added, up to a maximum height."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._resizing = False

        self.setFixedHeight(MIN_HEIGHT)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.textChanged.connect(self.refresh_height)

    def maximum_height(self) -> int:
        window = self.window()
        window_height = window.height() if window is not None else 900
        return max(
            MIN_HEIGHT,
            min(MAX_HEIGHT, int(window_height * MAX_WINDOW_FRACTION)),
        )

    def refresh_height(self) -> None:
        if self._resizing or self.viewport().height() <= 0:
            return

        chrome = self.height() - self.viewport().height()

        # QPlainTextDocumentLayout reports its height in lines, not pixels.
        # Multiply by the line height, add the document margin, and add the
        # frame/stylesheet padding that the viewport sits inside.
        lines = self.document().size().height()
        content = lines * self.fontMetrics().lineSpacing()
        content += 2 * self.document().documentMargin()
        wanted = int(content) + chrome + 2
        height = max(MIN_HEIGHT, min(wanted, self.maximum_height()))

        if height != self.height():
            self._resizing = True
            self.setFixedHeight(height)
            self._resizing = False

    def resizeEvent(self, event):  # type: ignore
        super().resizeEvent(event)
        self.refresh_height()
