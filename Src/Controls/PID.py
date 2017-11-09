import time, sys
import cv2
import numpy as np
import pyqtgraph as pg

from PyQt4 import QtCore, QtGui


class PID(QtCore.QObject):
    done_signal = QtCore.pyqtSignal(int, name='pid_done')

    def __init__(self):
        super(PID, self).__init__()

        self.exec_time = None
        self.should_run = False
        self.cx, self.cy = None, None
        self.motor_commands = None

    def run(self):
        """
        Starts the PID thread.  It will be blocked by the computer vision
        thread.  Once it receives 2D coordinates of the ball then the PID
        thread will execute.
        :return:
        """
        start = time.time()
        self.motor_commands = 5
        self.done_signal.emit(self.motor_commands)
        self.exec_time = time.time() - start
