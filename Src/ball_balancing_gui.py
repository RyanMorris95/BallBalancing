import sys
import time
import numpy as np
import pickle as p
import pyqtgraph as pg
import ComputerVision.detect_ball as detect_ball

from collections import deque
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
        time.sleep(1)
        self.pid = PID(max_output=100, min_output=-100)
        self.x_commands, self.y_commands = deque(maxlen=500), deque(maxlen=500)
        self.x_times, self.y_times = deque(maxlen=500), deque(maxlen=500)

        self.detectBallThread.done_signal.connect(self.cv_done)
        self.pid.done_signal.connect(self.pid_done)

        self.dp_edit, self.minDist_edit, self.param1_edit = None, None, None
        self.param2_edit, self.minRadius_edit, self.maxRadius_edit = None, None, None
        self.save_cv_edit_values_btn, self.load_cv_edit_values_btn = None, None
        self.reset_cv_btn, self.start_cv_btn, self.tracking_cv_btn = None, None, None
        self.kpX_edit, self.kiX_edit, self.kdX_edit = None, None, None
        self.kpY_edit, self.kiY_edit, self.kdY_edit = None, None, None
        self.setup_sliders()
        # self.servoSlider = QtGui.QSlider(QtGui.QMainWindow)
        # self.servoSlider.setMinimum(0)
        # self.servoSlider.setMaximum(180)
        # self.sl.setValue(0)
        # self.arduinoComm.send(servo1=35, servo2=15)
        # self.pidX_plot_widget = pg.plot(self.x_times, self.x_commands, title="PID X")
        # self.pidX_plot_widget.addItem(pg.PlotCurveItem())
        # self.pidY_plot_widget = pg.plot(self.y_times, self.y_commands, title="PID Y")
        # self.pidY_plot_widget.addItem(pg.PlotCurveItem())
        # self.ui_mainWindow.taskGraphLayout.addWidget(self.pidX_plot_widget)
        # self.ui_mainWindow.taskGraphLayout.addWidget(self.pidY_plot_widget)


        self.start_time = time.time()

        self.resize(885, 800)

    def run(self):
        self.detectBallThread.start()

    def cv_done(self, cx, cy):
        if self.detectBallThread.ready:
            self.pid.run([cx, cy])

    def pid_done(self, motor_commands):
        if motor_commands:
            # self.x_commands.append(motor_commands)
            # self.x_times.append(time.time()-self.start_time)
            # self.pidX_plot_widget.plotItem.setData(np.array(self.x_commands))
            self.arduinoComm.send(servo1=motor_commands[0], servo2=motor_commands[1])

    def comm_done(self):
        pass

    def exit_handler(self):
        self.detectBallThread.cap.release()
        self.detectBallThread.stop_process()
        self.detectBallThread.SHOULD_RUN = False

    def setup_sliders(self):
        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel("Image Processing Values"))
        self.dp_edit = QtGui.QLineEdit()
        self.dp_edit.returnPressed.connect(self.edits_changed)
        h_min_label = QtGui.QLabel('dp', self)
        self.ui_mainWindow.formLayout_2.addRow(self.dp_edit, h_min_label)

        self.minDist_edit = QtGui.QLineEdit()
        self.minDist_edit.returnPressed.connect(self.edits_changed)
        s_min_label = QtGui.QLabel('minDist', self)
        self.ui_mainWindow.formLayout_2.addRow(self.minDist_edit, s_min_label)

        self.param1_edit = QtGui.QLineEdit()
        self.param1_edit.returnPressed.connect(self.edits_changed)
        v_min_label = QtGui.QLabel('param1', self)
        self.ui_mainWindow.formLayout_2.addRow(self.param1_edit, v_min_label)

        self.param2_edit = QtGui.QLineEdit()
        self.param2_edit.returnPressed.connect(self.edits_changed)
        h_max_label = QtGui.QLabel('param2', self)
        self.ui_mainWindow.formLayout_2.addRow(self.param2_edit, h_max_label)

        self.minRadius_edit = QtGui.QLineEdit()
        self.minRadius_edit.returnPressed.connect(self.edits_changed)
        s_max_label = QtGui.QLabel('minRadius', self)
        self.ui_mainWindow.formLayout_2.addRow(self.minRadius_edit, s_max_label)

        self.maxRadius_edit = QtGui.QLineEdit()
        self.maxRadius_edit.returnPressed.connect(self.edits_changed)
        v_max_label = QtGui.QLabel('maxRadius', self)
        self.ui_mainWindow.formLayout_2.addRow(self.maxRadius_edit, v_max_label)

        self.reset_cv_btn = QtGui.QPushButton("Reset CV")
        self.start_cv_btn = QtGui.QPushButton("Start")
        self.tracking_cv_btn = QtGui.QPushButton("Track")
        self.ui_mainWindow.formLayout_2.addRow(self.reset_cv_btn, self.start_cv_btn)
        self.ui_mainWindow.formLayout_2.addRow(self.tracking_cv_btn, QtGui.QLabel(" "))
        self.tracking_cv_btn.clicked.connect(self.track_cv)
        self.reset_cv_btn.clicked.connect(self.reset_cv)
        self.start_cv_btn.clicked.connect(self.start_cv)

        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel(" "), QtGui.QLabel(" "))
        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel("PID X Values"))

        self.kpX_edit = QtGui.QLineEdit()
        kp_label = QtGui.QLabel('Kp', self)
        self.kpX_edit.returnPressed.connect(self.edits_changed)
        self.ui_mainWindow.formLayout_2.addRow(self.kpX_edit, kp_label)

        self.kiX_edit = QtGui.QLineEdit()
        ki_label = QtGui.QLabel('Ki', self)
        self.kiX_edit.returnPressed.connect(self.edits_changed)
        self.ui_mainWindow.formLayout_2.addRow(self.kiX_edit, ki_label)

        self.kdX_edit = QtGui.QLineEdit()
        kd_label = QtGui.QLabel('Kd', self)
        self.kdX_edit.returnPressed.connect(self.edits_changed)
        self.ui_mainWindow.formLayout_2.addRow(self.kdX_edit, kd_label)

        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel(" "), QtGui.QLabel(" "))
        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel("PID Y Values"))

        self.kpY_edit = QtGui.QLineEdit()
        kp_label = QtGui.QLabel('Kp', self)
        self.kpY_edit.returnPressed.connect(self.edits_changed)
        self.ui_mainWindow.formLayout_2.addRow(self.kpY_edit, kp_label)

        self.kiY_edit = QtGui.QLineEdit()
        ki_label = QtGui.QLabel('Ki', self)
        self.kiY_edit.returnPressed.connect(self.edits_changed)
        self.ui_mainWindow.formLayout_2.addRow(self.kiY_edit, ki_label)

        self.kdY_edit = QtGui.QLineEdit()
        kd_label = QtGui.QLabel('Kd', self)
        self.kdY_edit.returnPressed.connect(self.edits_changed)
        self.ui_mainWindow.formLayout_2.addRow(self.kdY_edit, kd_label)

        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel(" "), QtGui.QLabel(" "))
        self.ui_mainWindow.formLayout_2.addRow(QtGui.QLabel("Servo Values"))

        self.servo1_edit = QtGui.QLineEdit()
        servo1_label = QtGui.QLabel('Servo 1', self)
        self.servo1_edit.setText("10")
        self.servo1_edit.returnPressed.connect(self.edits_changed)
        self.ui_mainWindow.formLayout_2.addRow(self.servo1_edit, servo1_label)

        self.servo2_edit = QtGui.QLineEdit()
        servo2_label = QtGui.QLabel('Servo 2', self)
        self.servo2_edit.setText("35")
        self.servo2_edit.returnPressed.connect(self.edits_changed)
        self.servo2_edit.releaseMouse()
        self.ui_mainWindow.formLayout_2.addRow(self.servo2_edit, servo2_label)

        self.save_cv_edit_values_btn = QtGui.QPushButton("Save Values")
        self.load_cv_edit_values_btn = QtGui.QPushButton("Load Values")
        self.ui_mainWindow.formLayout_2.addRow(self.save_cv_edit_values_btn, QtGui.QLabel(" "))
        self.ui_mainWindow.formLayout_2.addRow(self.load_cv_edit_values_btn, QtGui.QLabel(" "))
        self.save_cv_edit_values_btn.clicked.connect(self.save_values)
        self.load_cv_edit_values_btn.clicked.connect(self.load_values)

        self.load_values()

    def track_cv(self):
        self.detectBallThread.tracking = True

    def reset_cv(self):
        self.detectBallThread.reset = True

    def start_cv(self):
        self.detectBallThread.ready = True

    def save_values(self, test):
        dump_list = [self.dp_edit.text(), self.minDist_edit.text(), self.param1_edit.text(),
                     self.param2_edit.text(), self.minRadius_edit.text(), self.maxRadius_edit.text(),
                     self.kpX_edit.text(), self.kiX_edit.text(), self.kdX_edit.text(), self.kpY_edit.text(),
                     self.kiX_edit.text(), self.kdY_edit.text()]

        print (dump_list)

        with open('slider_cv_values.p', 'wb') as fp:
            p.dump(dump_list, fp, protocol=2)

    def load_values(self):
        with open('slider_cv_values.p', 'rb') as fp:
            data = p.load(fp)

        self.detectBallThread.proc_params = data[0:6]
        self.dp_edit.setText(data[0])
        self.minDist_edit.setText(data[1])
        self.param1_edit.setText(data[2])
        self.param2_edit.setText(data[3])
        self.minRadius_edit.setText(data[4])
        self.maxRadius_edit.setText(data[5])
        self.kpX_edit.setText(data[6])
        self.kiX_edit.setText(data[7])
        self.kdX_edit.setText(data[8])
        self.kpY_edit.setText(data[9])
        self.kiY_edit.setText(data[10])
        self.kdY_edit.setText(data[11])

        # self.servo1_slider.setCurrentValue(Arduino_Comm.servo1)
        # self.servo2_slider.setCurrentValue(Arduino_Comm.servo2)

    def edits_changed(self):
        self.detectBallThread.proc_params = [int(self.dp_edit.text()), int(self.minDist_edit.text()),
                                             int(self.param1_edit.text()), int(self.param2_edit.text()),
                                             int(self.minRadius_edit.text()), int(self.maxRadius_edit.text())]
        self.reset_cv()

        self.pid.kP_X = float(self.kpX_edit.text())
        self.pid.ki_X = float(self.kiX_edit.text())
        self.pid.kD_X = float(self.kdX_edit.text())
        self.pid.kP_Y = float(self.kpY_edit.text())
        self.pid.ki_Y = float(self.kiY_edit.text())
        self.pid.kD_Y = float(self.kdY_edit.text())

        # Arduino_Comm.send(self.arduinoComm, servo1=int(self.servo1_edit.text()),
        # servo2=int(self.servo2_edit.text()))
        self.arduinoComm.send(servo1=int(self.servo1_edit.text()),
                              servo2=int(self.servo2_edit.text()))
        Arduino_Comm.servo2 = self.servo2_edit.text
