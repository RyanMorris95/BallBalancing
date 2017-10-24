import time
import numpy as np
import serial

from PyQt4 import QtCore, QtGui


class Arduino_Comm(QtCore.QThread):
    done_signal = QtCore.pyqtSignal(name='comm_done')

    def __init__(self, comm_port):
        super(Arduino_Comm, self).__init__()

        self.comm_port = comm_port
        self.should_run = False
        self.motor_commands = None

    def run(self):
        """
        Starts the arduino communication thread.  The thread will be blocked
        until it gets the motor commands from the PID thread.
        :return:
        """
        while True:
            if self.should_run:
                start = time.time()
                #print ("Hi From Arduino")
                self.should_run = False
                self.done_signal.emit()
                self.exec_time = time.time() - start
