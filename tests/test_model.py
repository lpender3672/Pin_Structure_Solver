import numpy as np
import pytest

from core.model import node, member, force, constraint, truss


def test_member_length_is_the_real_length():
    m = member(node(0, 0), node(3, 4))
    assert m.length == pytest.approx(5.0)
    assert np.allclose(m.direction, (0.6, 0.8))


def test_member_mass_scales_with_length():
    m = member(node(0, 0), node(3, 4), mass_per_unit_length = 2)
    assert m.mass == pytest.approx(10.0)


def test_member_geometry_follows_its_nodes():
    a, b = node(0, 0), node(1, 0)
    m = member(a, b)
    b.move_to((0, 4))
    assert m.length == pytest.approx(4.0)
    assert np.allclose(m.direction, (0, 1))


def test_zero_length_member_rejected():
    with pytest.raises(ValueError):
        member(node(1, 1), node(1, 1))


def test_self_looping_member_rejected():
    a = node(1, 1)
    with pytest.raises(ValueError):
        member(a, a)


def test_node_ids_stay_unique_after_deletion():
    t = truss()
    a = t.add_node(node(0, 0))
    b = t.add_node(node(1, 0))
    t.delete_node(a)
    c = t.add_node(node(2, 0))
    assert len({a.id, b.id, c.id}) == 3


def test_nodes_are_hashable():
    a, b = node(0, 0), node(0, 0)
    assert len({a, b}) == 2


def test_add_node_reuses_a_coincident_node():
    t = truss()
    a = t.add_node(node(1, 2))
    b = t.add_node(node(1, 2))
    assert b is a
    assert len(t.nodes) == 1


def test_add_member_rejects_a_duplicate_either_way_round():
    t = truss()
    a = t.add_node(node(0, 0))
    b = t.add_node(node(1, 0))
    m = t.add_member(member(a, b))
    assert t.add_member(member(a, b)) is m
    assert t.add_member(member(b, a)) is m
    assert len(t.members) == 1


def test_deleting_a_node_deletes_everything_attached():
    t = truss()
    a = t.add_node(node(0, 0))
    b = t.add_node(node(1, 0))
    c = t.add_node(node(2, 0))
    t.add_member(member(a, b))
    t.add_member(member(b, c))
    t.add_force(force((0, -1)), b)
    t.add_force(force((1, 0)), b)
    t.add_constraint(constraint((0, 1)), b)

    t.delete_node(b)

    assert t.members == []
    assert list(t.get_all_entities()) == [a, c]


def test_deleting_forces_does_not_skip_any():
    # the old code removed from the list it was iterating, so every other
    # force survived a node deletion
    t = truss()
    a = t.add_node(node(0, 0))
    for i in range(5):
        t.add_force(force((i, 0)), a)

    for f in list(a.forces):
        t.delete_force(f)

    assert a.forces == []


def test_revision_bumps_on_every_edit():
    t = truss()
    seen = [t.revision]

    a = t.add_node(node(0, 0))
    seen.append(t.revision)
    b = t.add_node(node(1, 0))
    seen.append(t.revision)
    m = t.add_member(member(a, b))
    seen.append(t.revision)
    t.add_force(force((0, -1)), b)
    seen.append(t.revision)
    t.add_constraint(constraint((0, 1)), a)
    seen.append(t.revision)
    t.delete_member(m)
    seen.append(t.revision)

    assert seen == sorted(set(seen))


def test_force_polar_round_trip():
    f = force.from_polar(10, np.pi / 3)
    assert f.magnitude == pytest.approx(10.0)
    assert f.angle == pytest.approx(np.pi / 3)


def test_constraint_reaction_counts():
    assert len(constraint((0, 1), 'roller').reaction_directions) == 1
    assert len(constraint((0, 1), 'pin').reaction_directions) == 2


def test_pin_reactions_are_orthogonal():
    d1, d2 = constraint((1, 2), 'pin').reaction_directions
    assert d1.dot(d2) == pytest.approx(0.0)


def test_unknown_constraint_type_rejected():
    with pytest.raises(ValueError):
        constraint((0, 1), 'fixed')


def test_reaction_count_totals_the_truss():
    t = truss()
    a = t.add_node(node(0, 0))
    b = t.add_node(node(1, 0))
    t.add_constraint(constraint((0, 1), 'pin'), a)
    t.add_constraint(constraint((0, 1), 'roller'), b)
    assert t.reaction_count() == 3
