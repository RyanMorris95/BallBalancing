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
        self.ser = serial.Serial('com3', timeout=1)
        self.servo1 = 180
        self.servo2 = 180

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


    def send(self, servo1=None, servo2=None):
        if servo1 is not None:
            servo1_val = "b'" + str(servo1)
            self.ser.write(servo1_val)
            self.servo1 = servo1
        # if servo2 is not None:
        #     servo2_val = 'b"' + str(servo2)
        #     self.ser.write(servo1_val)
        #     self.servo2 = servo2

    def stop_process(self):
        self.p.join()

    if __name__ == '__main__':
        print ('hi')
        # ser = serial.Serial('com3', timeout=1)
        # while True:
        #     servo1_val = 'b"' + self.servo1
        #     dataPak = str(val)
        #     time.sleep(4)
        #     ser.write(b'0')
        #     val = 180
        #     dataPak = str(val)
        #     time.sleep(4)
        #     ser.write(b'180')
