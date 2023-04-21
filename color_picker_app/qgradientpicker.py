
from PySide6.QtGui import QScreen, QColor, QStandardItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QComboBox,
    QPushButton,
    QLineEdit,
    QLabel
)

from functools import partial
from enum import Enum
import qdarktheme
import qgradient


class ColorType(Enum):
    RGB = 1,
    HEX = 2,
    GRADIENT_POINTS = 3


class QGradientPicker(QDialog):

    accepted = Signal()

    def __init__(self, parent=None):
        super(QGradientPicker, self).__init__(parent)

        self.gradient = [(0.0, '#000000'), (1.0, '#ffffff')]

        self.initUI()

    def initUI(self):
        # Widget configs.
        self.setWindowTitle("Gradient Picker")
        self.setWindowPosition()
        # self.setStyleSheet(qdarktheme.load_stylesheet())

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        grid1 = QGridLayout()
        grid2 = QGridLayout()

        gbox1 = QGroupBox(self)
        gbox2 = QGroupBox(self)

        # -- Widgets.

        applyBtn = QPushButton("Apply")
        cancelBtn = QPushButton("Cancel")
        resetBtn = QPushButton("Reset")

        self.gradSlider = qgradient.QtGradientSlider()
        self.colorbox = QComboBox()

        self.rLabel = QLabel("R")
        self.gLabel = QLabel("G")
        self.bLabel = QLabel("B")
        self.hexLabel = QLabel("#")

        self.rInput = QLineEdit()
        self.gInput = QLineEdit()
        self.bInput = QLineEdit()
        self.hexInput = QLineEdit()

        self.rInput.setAlignment(Qt.AlignCenter)
        self.gInput.setAlignment(Qt.AlignCenter)
        self.bInput.setAlignment(Qt.AlignCenter)
        self.hexInput.setAlignment(Qt.AlignCenter)

        self.rInput.setDisabled(True)
        self.gInput.setDisabled(True)
        self.bInput.setDisabled(True)
        self.hexInput.setDisabled(True)

        # -- Signals
        resetBtn.clicked.connect(
            partial(self.callback, "reset_button_pressed"))

        applyBtn.clicked.connect(
            partial(self.callback, "apply_button_pressed"))

        cancelBtn.clicked.connect(
            partial(self.callback, "cancel_button_pressed"))

        self.gradSlider.gradientPointChanged.connect(
            partial(self.callback, "gradient_point_added"))

        self.colorbox.activated.connect(
            partial(self.callback, 'colorbox_index_changed'))
        self.updateColorBox()

        # -- Layout.
        gbox1.setTitle("Gradient Control")
        gbox2.setTitle("Color Info")

        gbox1.setLayout(grid1)
        gbox1.setFixedSize(200, 100)
        grid1.setVerticalSpacing(10)
        grid1.addWidget(self.gradSlider, 0, 0, 1, 0)
        grid1.addWidget(self.colorbox, 1, 0, Qt.AlignLeft)
        grid1.addWidget(resetBtn, 1, 1, alignment=Qt.AlignRight)
        hbox.addWidget(gbox1, alignment=Qt.AlignTop)

        gbox2.setLayout(grid2)
        gbox2.setFixedWidth(130)
        grid2.addWidget(self.rLabel, 0, 0, alignment=Qt.AlignCenter)
        grid2.addWidget(self.rInput, 0, 1)
        grid2.addWidget(self.gLabel, 1, 0, alignment=Qt.AlignCenter)
        grid2.addWidget(self.gInput, 1, 1)
        grid2.addWidget(self.bLabel, 2, 0, alignment=Qt.AlignCenter)
        grid2.addWidget(self.bInput, 2, 1)
        grid2.addWidget(self.hexLabel, 3, 0, alignment=Qt.AlignCenter)
        grid2.addWidget(self.hexInput, 3, 1)
        grid2.addWidget(applyBtn, 4, 0)
        grid2.addWidget(cancelBtn, 4, 1)
        hbox.addWidget(gbox2)

        self.setLayout(hbox)

    def getGradient(self, mode=None):
        # Gets the second index from tuple.
        # HEX Colors.
        # RGB Colors.
        gradient_points = [tup[0] for tup in self.gradSlider._gradient]
        hex_colors = [tup[1] for tup in self.gradSlider._gradient]
        rgb_colors = [ColorHelper.hex2rgb(tup) for tup in hex_colors]

        # Type checking
        if mode and not isinstance(mode, ColorType):
            raise TypeError('color mode must be an instance of ColorType Enum')

        if mode == ColorType.GRADIENT_POINTS:
            return gradient_points

        elif mode == ColorType.HEX:
            return hex_colors

        elif mode == ColorType.RGB:
            return rgb_colors

        else:
            return self.gradSlider._gradient

    def setGradient(self, gradient):
        self.gradSlider._gradient = gradient

    def updateColorBox(self):
        self.colorbox.clear()
        hex_colors = self.getGradient(mode=ColorType.HEX)

        for _, color in enumerate(hex_colors):
            item = QStandardItem(color.upper())
            item.setForeground(QColor(color))
            self.colorbox.model().appendRow(item)

    def updateInfoLabels(self):
        index = self.colorbox.currentIndex()
        hex_color = self.getGradient(mode=ColorType.HEX)[index]
        r, g, b = self.getGradient(mode=ColorType.RGB)[index]

        self.hexInput.setText(hex_color)
        self.rInput.setText(str(r))
        self.gInput.setText(str(g))
        self.bInput.setText(str(b))

    def callback(self, param, args=None):

        if param == "gradient_point_added":
            self.updateColorBox()

        elif param == "colorbox_index_changed":
            self.updateInfoLabels()

        elif param == "reset_button_pressed":
            points = self.getGradient(ColorType.GRADIENT_POINTS)
            _ = [self.gradSlider.removeStopAtPosition(
                i) for i in range(1, len(points)-1)]
            self.updateInfoLabels()

        elif param == "apply_button_pressed":
            self.accepted.emit()
            self.close()

        elif param == "cancel_button_pressed":
            self.setGradient([(0.0, '#000000'), (1.0, '#ffffff')])
            self.close()

        else:
            pass

    def setWindowPosition(self):
        # Function for positioning main frame to the center of primary screen.
        qtRect = self.frameGeometry()
        centerPoint = QScreen.availableGeometry(
            QApplication.primaryScreen()).center()
        qtRect.moveCenter(centerPoint)
        self.move(qtRect.topLeft())


class ColorHelper:
    def __init__(self):
        pass

    @staticmethod
    def hex2rgb(hex):
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb2hex(rgb):
        r, g, b = rgb
        return '#%02x%02x%02x' % (r, g, b)
