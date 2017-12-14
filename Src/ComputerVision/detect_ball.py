import time, sys
import cv2
import numpy as np

from multiprocessing import Queue, Process, Pipe
from PyQt4 import QtCore, QtGui
from pympler.tracker import SummaryTracker
from mem_top import mem_top

SHOULD_RUN = True
close_signal = QtCore.pyqtSignal(name='close')
image_shape = [480, 640]
center = [240, 320]
print (mem_top())


def timer_done():
    global ready
    ready = True
    print ("Timer Done!")


def image_processing(input_queue, output_queue, proc_params, cap):
    font = cv2.FONT_HERSHEY_COMPLEX
    detection = True
    tracking = False
    First = True
    x, y = 0, 0
    cx, cy = 0, 0
    r = 0
    roi, hsv_roi, mask, term_crit, track_window = None, None, None, None, None

    while SHOULD_RUN:

        start_time = time.time()
        proc_params = input_queue.get()
        ret, frame = cap.read()
        cv2.circle(frame, (center[1], center[0]), 60, (0, 255, 255), 3)
        img_proc_params = [int(i) for i in proc_params[0][0:6]]
        ready = proc_params[0][6]


        if ret:
            if detection and ready:
                # Hough Circles
                grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, dp=img_proc_params[0], minDist=img_proc_params[1],
                                           param1=img_proc_params[2], param2=img_proc_params[3],
                                           minRadius=img_proc_params[4],
                                           maxRadius=img_proc_params[5])
                if not circles is None:
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)

                        cx = i[0]
                        cy = i[1]
                        r = i[2]

                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), 3)

                    # in reference to center
                    x = cx - center[1]
                    y = center[0] - cy
                    cv2.putText(frame, str(x) + ', ' + str(y), (cx, cy - 10), font, 1, (255, 255, 0), 2,
                                cv2.LINE_AA)

            elif tracking and ready:
                if First:
                    roi = frame[cy - 2:cy + 2, cx - 2:cx + 2]
                    track_window = (cx, cy, r * 2, r * 2)
                    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                    min_arr = np.array([np.min(hsv_roi[:, :, 0]), np.min(hsv_roi[:, :, 1]), np.min(hsv_roi[:, :, 2])])
                    max_arr = np.array([np.max(hsv_roi[:, :, 0]), np.max(hsv_roi[:, :, 1]), np.max(hsv_roi[:, :, 2])])

                    mask = cv2.inRange(hsv_roi, min_arr, max_arr)
                    roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
                    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
                    First = False
                    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
                else:
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
                    ret, track_window = cv2.meanShift(dst, track_window, term_crit)

                    x, y, w, h = track_window
                    cx = x + (w / 2)
                    cy = y + (h / 2)
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), 255, 2)
                    cv2.circle(frame, (cx, cy), r, (0, 255, 0), 2)
                    cv2.putText(frame, str(cx) + ', ' + str(cy), (cx, cy - 10), font, 0.75, (255, 255, 0), 2,
                                cv2.LINE_AA)

                    # in reference to the center
                    x = cx - center[1]
                    y = center[0] - cy

            fps = (1.0 / (time.time() - start_time))
            cv2.putText(frame, str(round(fps, 1)) + ' ' + 'FPS', (10, 30), font, 0.75, (0, 255, 0), 2,
                        cv2.LINE_AA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output_queue.put([frame, [x, y]])


class DetectBall(QtCore.QThread):
    done_signal = QtCore.pyqtSignal(int, int, name='cv_done')

    def __init__(self, ui_mainWindow):
        super(DetectBall, self).__init__()

        self.frame = None  # will hold the current frame from webcam
        self.proc_params = []
        self.mask = None  # binary color mask
        self.exec_time = None
        self.should_run = True
        self.ui_mainWindow = ui_mainWindow
        self.cap = cv2.VideoCapture(1)
        self.p, self.queue = None, None
        self.cx, cy = 0, 0
        self.reset = False
        self.ready = False
        self.tracking = False
        self.input_queue, self.output_queue = Queue(maxsize=1), Queue(maxsize=1)

    def run(self):
        self.p = Process(target=image_processing,
                         args=(self.input_queue, self.output_queue, self.proc_params, self.cap))
        self.p.start()
        while True:
            self.proc_params.append(self.ready)
            self.proc_params.append(self.reset)
            self.proc_params.append(self.tracking)
            self.input_queue.put([self.proc_params])
            out = self.output_queue.get()
            self.frame = out[0]
            self.cx, self.cy = out[1]
            self.done_signal.emit(self.cx, self.cy)

            height, width, channel = self.frame.shape
            bpl = 3 * width
            qImg = QtGui.QImage(self.frame.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(qImg)

            self.ui_mainWindow.image_holder.setPixmap(pix)
            self.ui_mainWindow.image_holder.show()
            self.proc_params = self.proc_params[0:6]

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
