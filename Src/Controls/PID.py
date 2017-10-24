import time, sys
import cv2
import numpy as np

from PyQt4 import QtCore, QtGui


class PID(QtCore.QThread):
    done_signal = QtCore.pyqtSignal(int, name='pid_done')

    def __init__(self):
        super(PID, self).__init__()

        self.exec_time = None
        self.should_run = False
        self.x, self.y = None, None
        self.motor_commands = None

    def run(self):
        """
        Starts the PID thread.  It will be blocked by the computer vision
        thread.  Once it receives 2D coordinates of the ball then the PID
        thread will execute.
        :return:
        """
        while True:
            if self.should_run:
                start = time.time()
                self.motor_commands = 5
                self.done_signal.emit(self.motor_commands)
                self.should_run = False
                self.exec_time = time.time() - start
                #print ("Hi From PID")
