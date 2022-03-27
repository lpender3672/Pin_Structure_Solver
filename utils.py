import numpy as np


class utils:

    def normalise(pos):
        return pos / np.linalg.norm(pos)

    def perpendicular(dir):
        perpdir = np.array([-dir[1], dir[0]])

        return perpdir / np.linalg.norm(perpdir)

    def line_to_point(d, p, point):
        return abs((point - p).dot(d))/np.linalg.norm(d)