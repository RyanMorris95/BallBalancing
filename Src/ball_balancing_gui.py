import sys
import time

from PyQt4 import QtGui
from PyQt4 import QtCore
from Interface.ball_balancing_ui import Ui_MainWindow
from ComputerVision.detect_ball import DetectBall
from Interface.arduino_comm import Arduino_Comm
from Controls.PID import PID


class BallBalancingGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(BallBalancingGui, self).__init__(parent)

        self.ui_mainWindow = Ui_MainWindow()
        self.ui_mainWindow.setupUi(self)
        self.setWindowTitle('Ball Balancing')

        self.detectBallThread = DetectBall()
        self.arduinoCommThread = Arduino_Comm(100)
        self.pidThread = PID()

        self.detectBallThread.done_signal.connect(self.cv_done)
        self.pidThread.done_signal.connect(self.pid_done)

    def run(self):
        self.detectBallThread.start()
        self.arduinoCommThread.start()
        self.pidThread.start()

    def cv_done(self, x, y):
        self.pidThread.should_run = True
        self.pidThread.x = x
        self.pidThread.y = y

    def pid_done(self, motor_commands):
        self.arduinoCommThread.should_run = True
        self.arduinoCommThread.motor_commands = motor_commands

