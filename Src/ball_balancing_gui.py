import sys
import time
import numpy as np
import pickle as p

from PyQt4 import QtGui
from PyQt4 import QtCore
from Interface.ball_balancing_ui import Ui_MainWindow
from ComputerVision.detect_ball import DetectBall
from Interface.arduino_comm import Arduino_Comm
from Controls.PID import PID
from Utils.slide_edit import SlideEdit


class BallBalancingGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(BallBalancingGui, self).__init__(parent)

        self.ui_mainWindow = Ui_MainWindow()
        self.ui_mainWindow.setupUi(self)
        self.setWindowTitle('Ball Balancing')

        self.detectBallThread = DetectBall(self.ui_mainWindow)
        self.arduinoCommThread = Arduino_Comm(100)
        self.pidThread = PID()

        self.detectBallThread.done_signal.connect(self.cv_done)
        self.pidThread.done_signal.connect(self.pid_done)
        self.arduinoCommThread.done_signal.connect(self.comm_done)

        self.h_min_slider, self.v_min_slider, self.s_min_slider = None, None, None
        self.h_max_slider, self.v_max_slider, self.s_max_slider = None, None, None
        self.save_slider_values_btn, self.load_slider_values_btn = None, None
        self.setup_sliders()

        self.resize(874,526)

    def run(self):
        self.detectBallThread.start()
        #self.arduinoCommThread.start()
        #self.pidThread.start()

    def cv_done(self):
        self.pidThread.should_run = True
        # self.pidThread.x = x
        # self.pidThread.y = y

    def pid_done(self, motor_commands):
        self.arduinoCommThread.should_run = True
        self.arduinoCommThread.motor_commands = motor_commands

    def comm_done(self):
        self.detectBallThread.should_run = True


    def exit_handler(self):
        self.detectBallThread.cap.release()
        self.detectBallThread.stop_process()
        self.detectBallThread.SHOULD_RUN = False

    def setup_sliders(self):
        self.h_min_slider = SlideEdit(0, 255)
        h_min_label = QtGui.QLabel('H Min', self)
        self.h_min_slider.valueChanged.connect(self.sliders_changed)
        self.h_min_slider.setCurrentValue(100)
        self.ui_mainWindow.formLayout_2.addRow(self.h_min_slider, h_min_label)

        self.s_min_slider = SlideEdit(0, 255)
        s_min_label = QtGui.QLabel('S Min', self)
        self.s_min_slider.valueChanged.connect(self.sliders_changed)
        self.s_min_slider.setCurrentValue(100)
        self.ui_mainWindow.formLayout_2.addRow(self.s_min_slider, s_min_label)

        self.v_min_slider = SlideEdit(0, 255)
        v_min_label = QtGui.QLabel('V Min', self)
        self.v_min_slider.valueChanged.connect(self.sliders_changed)
        self.v_min_slider.setCurrentValue(100)
        self.ui_mainWindow.formLayout_2.addRow(self.v_min_slider, v_min_label)

        self.h_max_slider = SlideEdit(0, 255)
        h_max_label = QtGui.QLabel('H Max', self)
        self.h_max_slider.valueChanged.connect(self.sliders_changed)
        self.h_max_slider.setCurrentValue(200)
        self.ui_mainWindow.formLayout_2.addRow(self.h_max_slider, h_max_label)

        self.s_max_slider = SlideEdit(0, 255)
        s_max_label = QtGui.QLabel('S Max', self)
        self.s_max_slider.valueChanged.connect(self.sliders_changed)
        self.s_max_slider.setCurrentValue(200)
        self.ui_mainWindow.formLayout_2.addRow(self.s_max_slider, s_max_label)

        self.v_max_slider = SlideEdit(0, 255)
        v_max_label = QtGui.QLabel('V Max', self)
        self.v_max_slider.valueChanged.connect(self.sliders_changed)
        self.v_max_slider.setCurrentValue(200)
        self.ui_mainWindow.formLayout_2.addRow(self.v_max_slider, v_max_label)

        self.save_slider_values_btn = QtGui.QPushButton("Save Values")
        self.load_slider_values_btn = QtGui.QPushButton("Load Values")
        self.ui_mainWindow.formLayout_2.addRow(self.save_slider_values_btn, QtGui.QLabel(" "))
        self.ui_mainWindow.formLayout_2.addRow(self.load_slider_values_btn, QtGui.QLabel(" "))
        self.save_slider_values_btn.clicked.connect(self.save_values)
        self.load_slider_values_btn.clicked.connect(self.load_values)

    def save_values(self):
        with open('slider_values.p', 'wb') as fp:
            p.dump([self.detectBallThread.hsv_min, self.detectBallThread.hsv_max], fp, protocol=2)

    def load_values(self):
        with open('slider_values.p', 'rb') as fp:
            data = p.load(fp)
            hsv_min = data[0]
            hsv_max = data[1]

        print (hsv_min, hsv_max)
        self.detectBallThread.hsv_min = hsv_min
        self.detectBallThread.hsv_max = hsv_max

    def sliders_changed(self):
        hsv_min = np.array((self.h_min_slider._currentValue, self.s_min_slider._currentValue, self.v_min_slider._currentValue))
        hsv_max = np.array((self.h_max_slider._currentValue, self.s_max_slider._currentValue, self.v_max_slider._currentValue))
        self.detectBallThread.hsv_min = hsv_min
        self.detectBallThread.hsv_max = hsv_max
