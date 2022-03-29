from multiprocessing.spawn import prepare
import numpy as np


class utils:

    def distance_between_points(p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def normalise(pos):
        return pos / np.linalg.norm(pos)

    def perpendicular(dir):
        perpdir = np.array([-dir[1], dir[0]])
        return perpdir / np.linalg.norm(perpdir)

    def line_to_point(d, p, point):
        normal = utils.perpendicular(d)
        return abs((point - p).dot(normal))/np.linalg.norm(normal)