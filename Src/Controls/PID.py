import time, sys
import cv2
import numpy as np
import pyqtgraph as pg

from PyQt4 import QtCore, QtGui


class PID(QtCore.QObject):
    done_signal = QtCore.pyqtSignal(int, name='pid_done')

    def __init__(self, max_output, min_output):
        super(PID, self).__init__()

        self.exec_time = None
        self.should_run = False
        self.motor_command = None
        self.kD, self.kP, self.kI = 1., 1., 1.
        self.last_input, self.integral_sum = 1., 1.
        self.max_output, self.min_output = max_output, min_output
        self.end_time = None
        self.elapsed_time = None

    def _compute(self, input):
        p = self.kP * input
        i = self.integral_sum + self.kI * input * self.elapsed_time
        d = self.kD * (input - self.last_input) / self.elapsed_time

        self.integral_sum = i
        self.last_input = input

        result = p + i + d
        self.motor_command = result;
        if result > self.max_output:
            self.motor_command = self.max_output
        elif result < self.min_output:
            self.motor_command = self.min_output

    def run(self, input):
        """
        Starts the PID thread.  It will be blocked by the computer vision
        thread.  Once it receives 2D coordinates of the ball then the PID
        thread will execute.
        :return:
        """
        if not self.end_time:  # wait one cycle
            self.last_input = input
        else:
            self.elapsed_time = time.time() - self.end_time
            self._compute(input)

        self.end_time = time.time()
        self.done_signal.emit(self.motor_command)
