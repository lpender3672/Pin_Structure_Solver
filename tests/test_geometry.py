import numpy as np
import pytest

from core import geometry as geom


def test_normalise_raises_on_zero():
    with pytest.raises(ValueError):
        geom.normalise((0, 0))


def test_try_normalise_returns_none_on_zero():
    assert geom.try_normalise((0, 0)) is None
    assert np.allclose(geom.try_normalise((0, 3)), (0, 1))


def test_normalise_is_unit():
    assert geom.norm(geom.normalise((3, 4))) == pytest.approx(1.0)


def test_perpendicular_is_orthogonal_and_same_length():
    v = np.array([3.0, 4.0])
    p = geom.perpendicular(v)
    assert v.dot(p) == pytest.approx(0.0)
    assert geom.norm(p) == pytest.approx(geom.norm(v))


def test_angle_and_unit_round_trip():
    for a in (0.0, 0.7, np.pi / 2, -2.5):
        assert geom.angle_of(geom.unit(a)) == pytest.approx(a)


def test_is_axis_aligned():
    assert geom.is_axis_aligned((0, -2))
    assert geom.is_axis_aligned((5, 0))
    assert not geom.is_axis_aligned((1, 1))
    assert not geom.is_axis_aligned((0, 0))


def test_line_distance_to_point():
    l = geom.line((1, 0), (0, 0))
    assert l.distance_to_point((5, 3)) == pytest.approx(3.0)
    assert l.distance_to_point((5, 0)) == pytest.approx(0.0)


def test_line_distance_ignores_direction_magnitude():
    a = geom.line((1, 0), (0, 0))
    b = geom.line((7, 0), (0, 0))
    assert a.distance_to_point((2, 4)) == pytest.approx(b.distance_to_point((2, 4)))


def test_line_project():
    l = geom.line((0, 2), (1, 0))
    assert np.allclose(l.project((5, 7)), (1, 7))


def test_line_intersection():
    a = geom.line((1, 0), (0, 3))
    b = geom.line((0, 1), (4, 0))
    assert np.allclose(a.intersection(b), (4, 3))


def test_parallel_lines_do_not_intersect():
    a = geom.line((1, 1), (0, 0))
    b = geom.line((2, 2), (1, 0))
    assert a.intersection(b) is None


def test_vec_rejects_wrong_shape():
    with pytest.raises(ValueError):
        geom.vec((1, 2, 3))
