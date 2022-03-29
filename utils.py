from multiprocessing.spawn import prepare
import numpy as np


class line(object):

    def __init__(self,d, p):
        self.d = d
        self.p = p
    
    def distance_to_point(self, p):
        perpd = np.array([-self.d[1], self.d[0]])
        return abs((p - self.p).dot(perpd))/np.linalg.norm(perpd)


class utils:

    def distance_between_points(p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def normalise(pos):
        return pos / np.linalg.norm(pos)

    def perpendicular(dir):
        perpdir = np.array([-dir[1], dir[0]])
        return perpdir / np.linalg.norm(perpdir)
