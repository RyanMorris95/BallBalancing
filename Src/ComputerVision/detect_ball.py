import time, sys
import cv2
import numpy as np

from multiprocessing import Queue, Process, Pipe
from PyQt4 import QtCore, QtGui

SHOULD_RUN = True
close_signal = QtCore.pyqtSignal(name='close')


def image_processing(input_queue, output_queue, hsv_min, hsv_max, cap):
    count = 0
    while SHOULD_RUN:
        data_in = input_queue.get()
        hsv_min = data_in[0]
        hsv_max = data_in[1]
        ret, frame = cap.read()
        if ret:
            try:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mask = cv2.inRange(hsv, hsv_min, hsv_max)
                frame = cv2.bitwise_and(frame, frame, mask=mask)
                output_queue.put([frame, mask])
                count += 1
            except:
                print ("HSV values not correct.")


class DetectBall(QtCore.QThread):
    done_signal = QtCore.pyqtSignal(name='cv_done')

    def __init__(self, ui_mainWindow):
        super(DetectBall, self).__init__()

        self.frame = None  # will hold the current frame from webcam
        self.hsv_min = np.array((100,100,100))
        self.hsv_max = np.array((200,200,200))
        self.mask = None  # binary color mask
        self.exec_time = None
        self.should_run = True
        self.ui_mainWindow = ui_mainWindow
        self.cap = cv2.VideoCapture(1)
        self.p, self.queue = None, None

    def run(self):
        self.input_queue, self.output_queue = Queue(maxsize=1), Queue(maxsize=1)
        self.p = Process(target=image_processing, args=(self.input_queue, self.output_queue, self.hsv_min, self.hsv_max, self.cap))
        self.p.start()
        while True:
            self.input_queue.put([self.hsv_min, self.hsv_max])
            out = self.output_queue.get()
            self.frame = out[0]
            self.mask = out[1]
            self.done_signal.emit()

            height, width, channel = self.frame.shape
            bpl = 3 * width
            qImg = QtGui.QImage(self.frame.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(qImg)

            self.ui_mainWindow.image_holder.setPixmap(pix)
            self.ui_mainWindow.image_holder.show()

    def stop_process(self):
        self.p.join()


if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        print (ret)
        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()