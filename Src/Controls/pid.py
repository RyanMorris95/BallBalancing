import numpy as np
import time

from collections import deque


class PID(object):
    """
    Takes in the location of the ball on the plate and outputs
    angles of the servos.
    """
    def __init__(self, tauP, tauI, tauD):
        """

        :param tau:
        """
        self.goal_pos = [0, 0]  # the point on the plate we want the ball to go to
        self.tauP, self.tauI, self.tauD = tauP, tauI, tauD
        self.input_queue = deque(maxlen=2)
        self.cte_queue = deque(maxlen=2)
        self.time_queue = deque(maxlen=2)

    def __call__(self, current_pos):
        """

        :param current_x:
        :param current_y:
        :return:
        """
        self.input_queue.append(current_pos)

        proportional = self._proportional(current_pos)
        integral = self._integral(current_pos)
        derivative = self._derivative(current_pos)

    def _proportional(self, current_pos):
        return current_pos * -self.tauP

    def _integral(self, current_pos):
        return None

    def _derivative(self, current_pos):
        return None