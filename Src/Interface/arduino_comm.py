import time
import numpy as np
import serial

from PyQt4 import QtCore, QtGui


class Arduino_Comm(QtCore.QObject):
    done_signal = QtCore.pyqtSignal(name='comm_done')

    def __init__(self, comm_port):
        super(Arduino_Comm, self).__init__()

        self.comm_port = comm_port
        self.should_run = False
        self.motor_commands = None
        self.ser = serial.Serial('/dev/ttyACM0', baudrate=2000000, timeout=1)
        self.servo1 = 35
        self.servo2 = 10
        self.first = True

    def run(self):
        """
        Starts the arduino communication thread.  The thread will be blocked
        until it gets the motor commands from the PID thread.
        :return:
        """
        start = time.time()
        self.done_signal.emit()
        self.exec_time = time.time() - start
        self.send(self.servo1, self.servo2)

    def _diff(self, curr, prev, thresh=5):
        return abs(curr - prev) >= thresh

    def send(self, servo1=None, servo2=None):
        if self.servo1 != servo1 or self.servo2 != servo2 or self.first:
            if servo1 and servo2:
                servo1_val = servo1 + 400
                ser_command = str(servo1_val) + ',' + '%03d' % servo2
                self.ser.write(str(ser_command))  # max angle of 315, min = 200 -- flat = 235
                self.servo1 = servo1
                self.servo2 = servo2
            self.first = False
        self.done_signal.emit()
