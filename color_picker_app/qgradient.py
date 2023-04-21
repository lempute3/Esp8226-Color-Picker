
from PySide6.QtWidgets import QWidget, QSizePolicy, QColorDialog
from PySide6.QtCore import Signal, QRect
from PySide6.QtGui import Qt, QPainter, QLinearGradient, QColor, QPen, QBrush, QPainterPath


class QtGradientSlider(QWidget):

    gradientChanged = Signal()
    gradientPointChanged = Signal()

    def __init__(self, gradient=None):
        super().__init__()

        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        if gradient:
            self._gradient = gradient
        else:
            self._gradient = [(0.0, '#000000'), (1.0, '#ffffff')]

        # Stop point handle sizes.
        self._stop_handle_w = 10
        self._stop_handle_h = 10

        self._drag_position = True

    def paintEvent(self, event):

        # Create the painter.
        qPainter = QPainter(self)

        # Create the painter path.
        qPainterPath = QPainterPath()

        # Get device width and height.
        devWidth = qPainter.device().width()
        devHeight = qPainter.device().height()

        # Sets colors to the linear horizontal gradient.
        linearGradient = QLinearGradient(0, 0, devWidth, 0)
        for stop, color in self._gradient:
            linearGradient.setColorAt(stop, QColor(color))

        # Set painter colors tools.
        qPainter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        qPainter.setBrush(QBrush(linearGradient))

        # Adjust bordersize and dimensions.
        qRect = QRect(0, 0, devWidth, devHeight)
        # qRect.adjust(15/2, 15/2, -10/2, -10/2)
        # qRect.setHeight(50)

        # Add the rect to path.
        qPainterPath.addRoundedRect(qRect, 10, 10)
        qPainter.setClipPath(qPainterPath)

        # Fill shape, draw the border and center the text.
        qPainter.fillPath(qPainterPath, qPainter.brush())
        qPainter.strokePath(qPainterPath, qPainter.pen())

        # Draw the stop handles.
        for stop, _ in self._gradient:

            qPainter.setPen(QPen(Qt.white))

            qPainter.drawLine(
                stop * devWidth, devHeight / 2 - self._stop_handle_h,
                stop * devWidth, devHeight / 2 + self._stop_handle_h
            )

            qPainter.setPen(QPen(Qt.red))

            qRect = QRect(
                stop * devWidth - self._stop_handle_w / 2,
                devHeight / 2 - self._stop_handle_h / 2,
                self._stop_handle_w,
                self._stop_handle_h
            )

            qPainter.drawRect(qRect)

        qPainter.end()

    def setGradient(self, gradient):
        assert all([0.0 <= stop <= 1.0 for stop, _ in gradient])
        self._gradient = gradient
        self._constrain_gradient()
        self._sort_gradient()
        self.gradientChanged.emit()
        self.gradientPointChanged.emit()

    def gradient(self):
        return self._gradient

    def _sort_gradient(self):
        self._gradient = sorted(self._gradient, key=lambda g: g[0])

    def _constrain_gradient(self):
        # Ensure values within valid range.
        self._gradient = [
            (max(0.0, min(1.0, stop)), color)
            for stop, color in self._gradient
        ]

    @property
    def _end_stops(self):
        return [0, len(self._gradient)-1]

    def addStop(self, stop, color=None):
        # Stop is a value 0...1, find the point to insert this stop
        # in the list.

        # Testing if this condition is true.
        assert 0.0 <= stop <= 1.0

        for n, g in enumerate(self._gradient):
            if g[0] > stop:
                # Insert before this entry, with specified or next color.
                self._gradient.insert(n, (stop, color or g[1]))
                break

        self._constrain_gradient()
        self.gradientChanged.emit()
        self.gradientPointChanged.emit()
        self.update()

    def removeStopAtPosition(self, n):
        if n not in self._end_stops:
            del self._gradient[n]
            self.gradientChanged.emit()
            self.gradientPointChanged.emit()
            self.update()

    def setColorAtPosition(self, n, color):
        if n < len(self._gradient):
            stop, _ = self._gradient[n]
            self._gradient[n] = stop, color
            self.gradientChanged.emit()
            self.gradientPointChanged.emit()
            self.update()

    def chooseColorAtPosition(self, n, current_color=None):
        dlg = QColorDialog(self)
        if current_color:
            dlg.setCurrentColor(QColor(current_color))

        if dlg.exec_():
            self.setColorAtPosition(n, dlg.currentColor().name())

    def _find_stop_handle_for_event(self, e, to_exclude=None):
        width = self.width()
        height = self.height()
        midpoint = height / 2

        # Are we inside a stop point? First check y.
        if (
            e.y() >= midpoint - self._stop_handle_h and
            e.y() <= midpoint + self._stop_handle_h
        ):

            for n, (stop, color) in enumerate(self._gradient):
                if to_exclude and n in to_exclude:
                    # Allow us to skip the extreme ends of the gradient.
                    continue
                if (
                    e.x() >= stop * width - self._stop_handle_w and
                    e.x() <= stop * width + self._stop_handle_w
                ):
                    return n

    def mousePressEvent(self, e):

        # We're in this stop point.
        if e.button() == Qt.RightButton:
            n = self._find_stop_handle_for_event(e)
            if n is not None:
                _, color = self._gradient[n]
                self.chooseColorAtPosition(n, color)

        elif e.button() == Qt.LeftButton:
            n = self._find_stop_handle_for_event(e, to_exclude=self._end_stops)
            if n is not None:
                # Activate drag mode.
                self._drag_position = n

        elif e.button() == Qt.MiddleButton:
            n = self._find_stop_handle_for_event(e)
            self.removeStopAtPosition(n)

    def mouseReleaseEvent(self, e):
        self._drag_position = None
        self._sort_gradient()

    def mouseMoveEvent(self, e):
        # If drag active, move the stop.
        if self._drag_position:
            stop = e.x() / self.width()
            _, color = self._gradient[self._drag_position]
            self._gradient[self._drag_position] = stop, color
            self._constrain_gradient()
            self.gradientChanged.emit()
            self.gradientPointChanged.emit()
            self.update()

    def mouseDoubleClickEvent(self, e):
        # Calculate the position of the click relative 0..1 to the width.
        n = self._find_stop_handle_for_event(e)
        if n:
            self._sort_gradient()  # Ensure ordered.
            # Delete existing, if not at the ends.
            if n > 0 and n < len(self._gradient) - 1:
                self.removeStopAtPosition(n)
        else:
            stop = e.x() / self.width()
            self.addStop(stop)
