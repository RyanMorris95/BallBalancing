import time, sys
import cv2
import numpy as np
import pyqtgraph as pg

from PyQt4 import QtCore, QtGui


class PID(QtCore.QObject):
    done_signal = QtCore.pyqtSignal(list, name='pid_done')

    def __init__(self, max_output, min_output):
        super(PID, self).__init__()

        self.exec_time = None
        self.should_run = False
        self.last_input, self.integral_sum = 0., 0.
        self.max_output, self.min_output = max_output, min_output
        self.end_time = None
        self.elapsed_time = None
        self.motor_command_1, self.motor_command_2 = None, None
        self.servo2_max, self.servo2_min = 70, 5  # tip +y, tip -y
        self.servo1_max, self.servo1_min = 120, 1  # top +x, tip -x
        self.servo1_flat, self.servo2_flat = 10, 35
        self.y_angle_conv = 0  # to convert y pixels to angle  # started: 20/220  best:
        self.x_angle_conv = 0  # to convert x pixels to angle
        self.kP_Y, self.kI_Y, self.kD_Y = self.y_angle_conv, 0.0, 0.0
        self.kP_X, self.kI_X, self.kD_X = self.x_angle_conv, 0.0, 0.0

    def _compute(self, error, x=True):
        if abs(error) > 10:
            if x:
                last_error = self.last_error[0]
                max = self.servo1_max
                min = self.servo1_min
                kP, kI, kD = self.kP_X, self.kI_X, self.kD_X
            else:
                last_error = self.last_error[1]
                max = self.servo2_max
                min = self.servo2_min
                kP, kI, kD = self.kP_Y, self.kI_Y, self.kD_Y

            p = kP * error
            i = self.integral_sum + kI * error * self.elapsed_time
            d = kD * (error - last_error) / self.elapsed_time

            self.integral_sum = i
            result = p + i + d

            if x:
                result = float(self.servo1_flat) - result
            else:
                result = float(self.servo2_flat) - result

            result = int(result)

            if result > max:
                result = max
            elif result < min:
                result = min

            return result
        return None

    def run(self, error):
        """
        Starts the PID thread.  It will be blocked by the computer vision
        thread.  Once it receives 2D coordinates of the ball then the PID
        thread will execute.
        :return:
        """
        if not self.end_time:  # wait one cycle
            self.last_error = error
        else:
            self.elapsed_time = time.time() - self.end_time
            self.motor_command_1 = self._compute(error[0], x=True)  # x pid
            if not self.motor_command_1:
                self.motor_command_1 = self.servo1_flat
            self.motor_command_2 = self._compute(error[1], x=False)
            if not self.motor_command_2:
                self.motor_command_2 = self.servo2_flat

        self.end_time = time.time()
        self.last_error = error
        self.done_signal.emit([self.motor_command_1, self.motor_command_2])
