from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy


class EllipsisLabel(QLabel):
    """Renders line of text, truncating with "…" upon overflow"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self._full_text = ""
        self.setWordWrap(False)
        self.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        self.setText(text)

    def setText(self, text: str) -> None:
        self._full_text = " ".join(text.split())
        self._apply_elision()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_elision()

    def minimumSizeHint(self) -> QSize:
        # Without this, QLabel refuses to shrink below the full text width.
        return QSize(0, super().minimumSizeHint().height())

    def _apply_elision(self) -> None:
        ELLIPSIS = "…"
        elided = self.fontMetrics().elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,
            max(0, self.contentsRect().width()),

        )
        # Avoid ellipsis right after a space
        if elided.endswith(" …"):
            elided = elided[:-1].rstrip() + ELLIPSIS
        if elided != self.text():
            super().setText(elided)
        self.setToolTip(self._full_text if elided != self._full_text else "")
