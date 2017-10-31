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
        self.ser = None

    def run(self):
        """
        Starts the arduino communication thread.  The thread will be blocked
        until it gets the motor commands from the PID thread.
        :return:
        """
        start = time.time()
        self.done_signal.emit()
        self.exec_time = time.time() - start


    def stop_process(self):
        self.p.join()

    if __name__ == '__main__':
        ser = serial.Serial('com3', timeout=1)
        while True:
            val = 0
            dataPak = str(val)
            time.sleep(4)
            ser.write(b'0')
            val = 180
            dataPak = str(val)
            time.sleep(4)
            ser.write(b'180')
