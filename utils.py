from multiprocessing.spawn import prepare
import numpy as np


class line(object):

    def __init__(self,d, p):
        self.d = d
        self.p = p
    
    def distance_to_point(self, p):
        perpd = np.array([-self.d[1], self.d[0]])
        return abs((p - self.p).dot(perpd))/np.linalg.norm(perpd)
    
    def length(self):
        return np.linalg.norm(self.d)


class utils:

    def distance_between_points(p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def normalise(pos):
        return pos / np.linalg.norm(pos)

    def perpendicular(dir):
        return np.array([-dir[1], dir[0]])
    
    def is_axis_aligned(v, tol=1e-6):
        v = np.asarray(v, dtype=float)
        norm = np.linalg.norm(v)
        if norm < tol:
            return False
        
        axes = np.eye(len(v))
        dots = np.abs(axes @ v)
        return np.any(np.abs(dots - norm) < tol)
    
    def line_intersection(line1, line2):
        d1 = line1.d
        p1 = line1.p
        d2 = line2.d
        p2 = line2.p

        denom = d1[0] * d2[1] - d1[1] * d2[0]
        if denom == 0:
            return None  # Lines are parallel

        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / denom

        intersection_point = p1 + t * d1
        return intersection_point
