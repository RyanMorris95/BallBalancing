import time, sys
import cv2
import numpy as np

from PyQt4 import QtCore, QtGui


class DetectBall(QtCore.QThread):
    done_signal = QtCore.pyqtSignal(int, int, name='cv_done')

    def __init__(self):
        super(DetectBall, self).__init__()

        self.cap = cv2.VideoCapture()
        self.frame = None  # will hold the current frame from webcam
        self.hsv_min = np.array((100,100,100))
        self.hsv_max = np.array((200,200,200))
        self.mask = None  # binary color mask
        self.exec_time = None

    def run(self):
        while True:
            start = time.time()
            # ret, self.frame = self.cap.read()
            # hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            #
            # self.mask = cv2.inRange(hsv, self.hsv_min, self.hsv_max)
            #
            # # Display the resulting frame
            # cv2.imshow('frame', self.frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            print ("Hi from CV")
            self.exec_time = time.time() - start
            self.done_signal.emit(10, 10)

if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    while (cap.isOpenend()):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()