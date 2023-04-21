from threading import Thread
from PySide6.QtGui import QScreen, QIcon, QRegularExpressionValidator, QPixmap
from PySide6.QtCore import Qt, Signal, QThread, QRegularExpression, QRunnable, Slot
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QTabWidget,
    QStatusBar,
    QPushButton,
    QColorDialog,
    QLineEdit,
    QSpinBox,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QAbstractSpinBox
)

from functools import partial
import pyqtgraph as pg
from qgradientpicker import QGradientPicker, ColorType
from client import Client, Animations
import qdarktheme
import config

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):

        # Main window configs.
        self.setWindowTitle("Color Picker")
        self.setStyleSheet(qdarktheme.load_stylesheet())
        self.setFixedSize(300, 250)
        self.setWindowPosition()

        # winIconPixmap = QPixmap(":/app_icon.png")
        # winIcon = QIcon(winIconPixmap)
        # # winIcon.addFile('logo.png')
        self.setWindowIcon(QIcon("logo.ico"))

        # Init widgets.
        self.setCentralWidget(TableWidget(self))
        self.createStatusBar()

    # Function for positioning main frame to the center of primary screen.
    def setWindowPosition(self):
        qtRect = self.frameGeometry()
        centerPoint = QScreen.availableGeometry(
            QApplication.primaryScreen()).center()
        qtRect.moveCenter(centerPoint)
        self.move(qtRect.topLeft())

    def createStatusBar(self):
        statusBar = QStatusBar()
        statusBar.showMessage("Status:  |")
        self.setStatusBar(statusBar)


class TableWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        # Init configs.
        _config = config.PickerConfigs("config.ini")
        _config.create()

        # External windows.
        self.gradientPickerDialog = QGradientPicker(self)
        self.colorPickerDialog = QColorDialog(self)

        # Global vars.
        self.staticColor = (0, 0, 0)
        self.staticColorHex = "#000000"
        self.gradientPoints = [(0.0), (1.0)] 
        self.gradientColors = [(0, 0, 0), (255, 255, 255)]

        self._udpIp = _config.get("settings", "default_udp_ip")
        self._udpPort = _config.get("settings", "default_udp_port")
        self._ledCount = _config.getint("settings", "default_leds_count")
        self._ledBrightness = _config.getint("settings", "default_leds_brightness")

        self.udpIp = self._udpIp
        self.udpPort = self._udpPort
        self.ledCount = self._ledCount
        self.ledBrightness = self._ledBrightness

        # Init client.
        self._client = Client(self.ledCount, self.ledBrightness, self.udpIp, self.udpPort)

        self.initUI()

    def initUI(self):
        # Window layout.
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Init tab screens.
        qtTabs = QTabWidget()
        self.controlTab = QWidget()
        self.musicTab = QWidget()
        self.animationTab = QWidget()
        self.settingsTab = QWidget()

        # Adds tabs.
        qtTabs.addTab(self.controlTab, "Control")
        qtTabs.addTab(self.musicTab, "Music")
        qtTabs.addTab(self.animationTab, "Animations")
        qtTabs.addTab(self.settingsTab, "Settings")

        # Init tabs UI.
        self.createControlTab()
        self.createMusicTab()
        self.createAnimationTab()
        self.createSettingsTab()

        self.updateColorLabel()
        self.updateGradientLabel()

        # Adding all tab widgets to layout.
        layout.addWidget(qtTabs)


    def createControlTab(self):

        # Init buttons.
        colorBtn = QPushButton("Set Color")
        gradBtn = QPushButton("Set Gradient")
        offBtn = QPushButton("Turn Off")

        # Button signals.
        colorBtn.clicked.connect(partial(self.callback, "show_color_dialog"))
        gradBtn.clicked.connect(partial(self.callback, "show_gradient_dialog"))
        offBtn.clicked.connect(partial(self.callback, "lights_off"))

        # Init labels.
        self.colorLabel = QLabel("")
        self.gradLabel = QLabel("")

        # Create control tab.
        self.controlTab.layout = QGridLayout()
        self.controlTab.layout.addWidget(colorBtn, 0, 0)
        self.controlTab.layout.addWidget(self.colorLabel, 0, 1)
        self.controlTab.layout.addWidget(gradBtn, 1, 0)
        self.controlTab.layout.addWidget(self.gradLabel, 1, 1)
        self.controlTab.layout.addWidget(offBtn, 2, 0, 1, 2)
        self.controlTab.setLayout(self.controlTab.layout)

    def createSettingsTab(self):
        
        # Init labels.
        ipLabel = QLabel("IP Address")
        brightnesslabel = QLabel("Led Brightness")
        ledsLabel = QLabel("Led Count")

        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        portRange = "(?:[0-9]?[0-9]?[0-9]?[0-9])"

        ipRegex = QRegularExpression("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
        portRegex = QRegularExpression("^" + portRange + "$")

        ipValidator = QRegularExpressionValidator(ipRegex, self)
        portValidator = QRegularExpressionValidator(portRegex, self)

        # Init inputs.
        self.ipInput = QLineEdit()
        self.portInput = QLineEdit()
        self.ledsInput = QSpinBox()
        self.brightnessInput = QSpinBox()

        self.ipInput.setFixedWidth(90)
        self.ipInput.setAlignment(Qt.AlignCenter)
        self.ipInput.setValidator(ipValidator) 
        self.ipInput.setText(self.udpIp)

        self.portInput.setToolTip("UDP Port")
        self.portInput.setAlignment(Qt.AlignCenter)  
        self.portInput.setValidator(portValidator)
        self.portInput.setText(self.udpPort)

        self.ledsInput.setAlignment(Qt.AlignCenter)
        self.ledsInput.setRange(0, 255)
        self.ledsInput.setValue(self.ledCount)

        self.brightnessInput.setAlignment(Qt.AlignCenter)
        self.brightnessInput.setRange(0, 100)  
        self.brightnessInput.setValue(self.ledBrightness)

        # Init buttons
        applyBtn = QPushButton("Apply")
        resetBtn = QPushButton("Reset")

        # Button signals.
        applyBtn.clicked.connect(partial(self.callback, "settings_apply"))
        resetBtn.clicked.connect(partial(self.callback, "settings_reset"))

        # Create settings tab.
        self.settingsTab.layout = QGridLayout()
        self.settingsTab.layout.setContentsMargins(15, 10, 15, 10)
        self.settingsTab.layout.addWidget(ipLabel, 0, 0)
        self.settingsTab.layout.addWidget(self.ipInput, 0, 1)
        self.settingsTab.layout.addWidget(self.portInput, 0, 2)
        self.settingsTab.layout.addWidget(ledsLabel, 2, 0)
        self.settingsTab.layout.addWidget(self.ledsInput, 2, 2)
        self.settingsTab.layout.addWidget(brightnesslabel, 3, 0)
        self.settingsTab.layout.addWidget(self.brightnessInput, 3, 2)
        self.settingsTab.layout.addWidget(applyBtn, 4, 0)
        self.settingsTab.layout.addWidget(resetBtn, 4, 2)
        self.settingsTab.setLayout(self.settingsTab.layout)

    def createMusicTab(self):
        pass

    def createAnimationTab(self):

        #Init Label.
        animationLabel = QLabel("Animations")

        # Init combobox.
        self.animationBox = QComboBox()
        self.animationBox.addItems([_.name for _ in Animations])

        #Init input.
        self.animationDelayInput = QDoubleSpinBox()
        self.animationDelayInput.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.animationDelayInput.setDecimals(2)
        self.animationDelayInput.setRange(0.01, 1)
        self.animationDelayInput.setValue(0.04)
        self.animationDelayInput.setToolTip("Animation Delay") 

        # Init buttons.
        self.startAnimationBtn = QPushButton("Start")
        self.stopAnimationBtn = QPushButton("Stop")
        self.stopAnimationBtn.setEnabled(False)

        # Button signals.
        self.startAnimationBtn.clicked.connect(partial(self.callback, "animation_start"))
        self.stopAnimationBtn.clicked.connect(partial(self.callback, "animation_stop"))

        self.animationTab.layout = QGridLayout()
        self.animationTab.layout.addWidget(animationLabel, 0, 0)
        self.animationTab.layout.addWidget(self.animationBox, 0, 1)
        self.animationTab.layout.addWidget(self.animationDelayInput, 0, 2)
        self.animationTab.layout.addWidget(self.startAnimationBtn, 1, 0)
        self.animationTab.layout.addWidget(self.stopAnimationBtn, 1, 1)
        self.animationTab.setLayout(self.animationTab.layout)

    def updateColorLabel(self):
        self.colorLabel.setStyleSheet(
            "border: 1px solid #2a2a49;"
            "background-color: %s;"
            "padding: 4px" % (self.staticColorHex))

    def updateGradientLabel(self):
        stops = ""
        for i, point in enumerate(self.gradientPoints):
            stops += " stop:%s rgb%s " % (str(point), str(self.gradientColors[i]))

        self.gradLabel.setStyleSheet(
            "border:1px solid #2a2a49;"
            "background:qlineargradient( x1:0 y1:0, x2:1 y2:0, %s);"
            "padding:4px" % (stops))

    def openColorDialog(self):
        self.colorPickerDialog.show()
        self.colorPickerDialog.accepted.connect(partial(self.callback, "color_accepted"))

    def openGradientDialog(self):
        self.gradientPickerDialog.show()
        self.gradientPickerDialog.accepted.connect(partial(self.callback, "gradient_accepted"))

    def callback(self, param):

        if param == "show_color_dialog":
            self.openColorDialog()

        elif param == "show_gradient_dialog":
            self.openGradientDialog()

        elif param == "color_accepted":
            self.staticColorHex = self.colorPickerDialog.selectedColor().name()
            self.staticColor = self.colorPickerDialog.selectedColor().getRgb()[:-1]
            self._client.setColor(self.staticColor)
            self.updateColorLabel()

        elif param == "gradient_accepted":
            self.gradientPoints = self.gradientPickerDialog.getGradient(mode=ColorType.GRADIENT_POINTS)
            self.gradientColors = self.gradientPickerDialog.getGradient(mode=ColorType.RGB)
            self.updateGradientLabel()

        elif param == "lights_off":
            self._client.setColor((0, 0, 0))

        elif param == "animation_start":
            animation = self.animationBox.currentText()
            delay = self.animationDelayInput.value()

            self._client.startAnimation(Animations.from_str(animation), delay)
            self.startAnimationBtn.setEnabled(False)
            self.stopAnimationBtn.setEnabled(True)
            self.controlTab.setEnabled(False)

        elif param == "animation_stop":
            self._client.stopAnimation()
            self.startAnimationBtn.setEnabled(True)
            self.stopAnimationBtn.setEnabled(False)
            self.controlTab.setEnabled(True)

        elif param == "settings_apply":
            self.udpIp = self.ipInput.text()
            self.udpPort = self.portInput.text()
            self.ledCount = self.ledsInput.value()
            self.ledBrightness = self.brightnessInput.value()

            print(self._client.is_socket_closed(), self.udpIp)
            self._client.setStrip(self.ledCount, self.ledBrightness, self.udpIp, self.udpPort)

        elif param == "settings_reset":
            self.udpIp = self._udpIp
            self.udpPort = self._udpPort
            self.ledCount = self._ledCount
            self.ledBrightness = self._ledBrightness

            self.ipInput.setText(self.udpIp)
            self.portInput.setText(self.udpPort)
            self.ledsInput.setValue(self.ledCount)
            self.brightnessInput.setValue(self.ledBrightness)
        
        else:
            pass

    # class AnimationWorker(QRunnable):

    #     def __init__(self, parent=None):
    #         super(AnimationWorker, self).__init__(parent)


class AudioSpectrum(pg.GraphicsLayoutWidget):

    def __init__(self, parent):
        super().__init__(parent)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
