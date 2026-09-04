import numpy as np

EPS = 1e-12


class line(object):

    def __init__(self, d, p):
        self.d = vec(d)
        self.p = vec(p)

    def distance_to_point(self, q):
        perpd = perpendicular(self.d)
        n = np.linalg.norm(perpd)
        if n <= EPS:
            return distance_between_points(self.p, q)
        return float(abs((vec(q) - self.p).dot(perpd)) / n)

    def project(self, q):
        d = normalise(self.d)
        return self.p + d * (vec(q) - self.p).dot(d)

    def intersection(self, other):
        d1, p1 = self.d, self.p
        d2, p2 = other.d, other.p

        denom = d1[0] * d2[1] - d1[1] * d2[0]
        if denom == 0:
            return None  # parallel

        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / denom
        return p1 + t * d1


def vec(p):
    a = np.asarray(p, dtype=float)
    if a.shape != (2,):
        raise ValueError(f"expected a 2d point, got shape {a.shape}")
    return a


def norm(v):
    return float(np.linalg.norm(vec(v)))


def normalise(v, tol = EPS):
    v = vec(v)
    n = np.linalg.norm(v)
    if n <= tol:
        raise ValueError("cannot normalise a zero length vector")
    return v / n


def try_normalise(v, tol = EPS):
    # for callers where a degenerate vector is expected rather than a bug
    try:
        return normalise(v, tol)
    except ValueError:
        return None


def perpendicular(v):
    v = vec(v)
    return np.array([-v[1], v[0]])


def angle_of(v):
    v = vec(v)
    return float(np.arctan2(v[1], v[0]))


def unit(angle):
    return np.array([np.cos(angle), np.sin(angle)])


def distance_between_points(p1, p2):
    return norm(vec(p2) - vec(p1))


def is_axis_aligned(v, tol = 1e-6):
    v = vec(v)
    n = np.linalg.norm(v)
    if n < tol:
        return False
    return bool(np.any(np.abs(np.abs(v) - n) < tol))


def line_intersection(line1, line2):
    return line1.intersection(line2)
