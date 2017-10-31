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
        self.arduinoComm = Arduino_Comm(100)
        self.pid = PID()

        self.detectBallThread.done_signal.connect(self.cv_done)
        self.pid.done_signal.connect(self.pid_done)
        self.arduinoComm.done_signal.connect(self.comm_done)

        self.h_min_slider, self.v_min_slider, self.s_min_slider = None, None, None
        self.h_max_slider, self.v_max_slider, self.s_max_slider = None, None, None
        self.save_cv_slider_values_btn, self.load_cv_slider_values_btn = None, None
        self.kp_slider, self.ki_slider, self.kd_slider = None, None, None
        self.setup_sliders()
        # self.servoSlider = QtGui.QSlider(QtGui.QMainWindow)
        # self.servoSlider.setMinimum(0)
        # self.servoSlider.setMaximum(180)
        # self.sl.setValue(0)

        self.resize(874,526)

    def run(self):
        self.detectBallThread.start()

    def cv_done(self, cx, cy):
        self.pid.cx = cx
        self.pid.cy = cy
        self.pid.run()

    def pid_done(self, motor_commands):
        self.arduinoComm.motor_commands = motor_commands
        self.arduinoComm.run()

    def comm_done(self):
        pass


    def exit_handler(self):
        self.detectBallThread.cap.release()
        self.detectBallThread.stop_process()
        self.detectBallThread.SHOULD_RUN = False

    def setup_sliders(self):
        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel("Image Processing Values"))
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

        self.save_cv_slider_values_btn = QtGui.QPushButton("Save CV Values")
        self.load_cv_slider_values_btn = QtGui.QPushButton("Load CV Values")
        self.ui_mainWindow.formLayout_2.addRow(self.save_cv_slider_values_btn, QtGui.QLabel(" "))
        self.ui_mainWindow.formLayout_2.addRow(self.load_cv_slider_values_btn, QtGui.QLabel(" "))
        self.save_cv_slider_values_btn.clicked.connect(self.save_values)
        self.load_cv_slider_values_btn.clicked.connect(self.load_values)

        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel(" "), QtGui.QLabel(" "))
        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel("PID Values"))

        self.kp_slider = SlideEdit(0, 10)
        kp_label = QtGui.QLabel('Kp', self)
        self.kp_slider.setCurrentValue(2)
        self.ui_mainWindow.formLayout_2.addRow(self.kp_slider, kp_label)

        self.ki_slider = SlideEdit(0, 10)
        ki_label = QtGui.QLabel('Ki', self)
        self.ki_slider.setCurrentValue(2)
        self.ui_mainWindow.formLayout_2.addRow(self.ki_slider, ki_label)

        self.kd_slider = SlideEdit(0, 10)
        kd_label = QtGui.QLabel('Kd', self)
        self.kd_slider.setCurrentValue(2)
        self.ui_mainWindow.formLayout_2.addRow(self.kd_slider, kd_label)

        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel(" "), QtGui.QLabel(" "))
        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel("Servo Values"))

        self.servo1_slider = SlideEdit(0, 180)
        servo1_label = QtGui.QLabel('Servo 1', self)
        self.servo1_slider.setCurrentValue(180)
        self.servo1_slider.valueChanged.connect(self.sliders_changed)
        self.ui_mainWindow.formLayout_2.addRow(self.servo1_slider, servo1_label)

        self.servo2_slider = SlideEdit(0, 180)
        servo2_label = QtGui.QLabel('Servo 2', self)
        self.servo2_slider.setCurrentValue(180)
        self.servo2_slider.releaseMouse()
        self.ui_mainWindow.formLayout_2.addRow(self.servo2_slider, servo2_label)

    def save_values(self, test):
        print (test)
        with open('slider_cv_values.p', 'wb') as fp:
            p.dump([self.detectBallThread.hsv_min, self.detectBallThread.hsv_max], fp, protocol=2)

    def load_values(self):
        with open('slider_cv_values.p', 'rb') as fp:
            data = p.load(fp)
            hsv_min = data[0]
            hsv_max = data[1]

        print (hsv_min, hsv_max)
        self.detectBallThread.hsv_min = hsv_min
        self.detectBallThread.hsv_max = hsv_max
        self.h_min_slider.setCurrentValue(hsv_min[0])
        self.s_min_slider.setCurrentValue(hsv_min[1])
        self.v_min_slider.setCurrentValue(hsv_min[2])
        self.h_max_slider.setCurrentValue(hsv_max[0])
        self.s_max_slider.setCurrentValue(hsv_max[1])
        self.v_max_slider.setCurrentValue(hsv_max[2])

        self.servo1_slider.setCurrentValue(Arduino_Comm.servo1)
        self.servo2_slider.setCurrentValue(Arduino_Comm.servo2)

    def sliders_changed(self):
        hsv_min = np.array((self.h_min_slider._currentValue, self.s_min_slider._currentValue, self.v_min_slider._currentValue))
        hsv_max = np.array((self.h_max_slider._currentValue, self.s_max_slider._currentValue, self.v_max_slider._currentValue))
        self.detectBallThread.hsv_min = hsv_min
        self.detectBallThread.hsv_max = hsv_max
        print(int(self.servo1_slider._currentValue))
        Arduino_Comm.send(self.arduinoComm, servo1=int(self.servo1_slider._currentValue),
                                servo2=int(self.servo2_slider._currentValue))
        # Arduino_Comm.servo2 = self.servo2_slider._currentValue