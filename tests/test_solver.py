import numpy as np
import pytest

from core.model import node, member, force, constraint, truss
from core.solver import solve_forces, status

from helpers import build, bracket, a_frame, assert_in_equilibrium

SQRT2 = np.sqrt(2)


def test_bracket_matches_hand_calculation():
    t, (A, B, C) = bracket(load = 1000.0)
    sol = solve_forces(t)

    assert sol.state == status.OK
    ac, bc = t.members
    assert sol.tensions[ac] == pytest.approx(1000 * SQRT2)   # tension
    assert sol.tensions[bc] == pytest.approx(-1000)          # compression


def test_bracket_reactions_match_hand_calculation():
    t, (A, B, C) = bracket(load = 1000.0)
    sol = solve_forces(t)

    assert np.allclose(sol.reaction_at(A), (-1000, 1000))
    assert np.allclose(sol.reaction_at(B), (1000, 0))


def test_bracket_is_in_equilibrium():
    t, _ = bracket()
    assert_in_equilibrium(t, solve_forces(t))


def test_a_frame_matches_hand_calculation():
    t, (A, B, C) = a_frame(load = 2000.0)
    sol = solve_forces(t)

    assert sol.state == status.OK
    ac, bc, ab = t.members
    assert sol.tensions[ac] == pytest.approx(-1000 * SQRT2)
    assert sol.tensions[bc] == pytest.approx(-1000 * SQRT2)
    assert sol.tensions[ab] == pytest.approx(1000)
    assert np.allclose(sol.reaction_at(A), (0, 1000))
    assert np.allclose(sol.reaction_at(B), (0, 1000))


def test_a_frame_is_in_equilibrium():
    t, _ = a_frame()
    assert_in_equilibrium(t, solve_forces(t))


def test_reactions_balance_the_applied_load():
    t, _ = a_frame(load = 2000.0)
    sol = solve_forces(t)

    applied = sum((f.vector for nd in t.nodes for f in nd.forces), np.zeros(2))
    reacted = sum((r.vector for r in sol.reactions), np.zeros(2))
    assert np.allclose(applied + reacted, 0)


def test_member_forces_scale_linearly_with_the_load():
    single = solve_forces(a_frame(load = 1000.0)[0])
    double_truss, _ = a_frame(load = 2000.0)
    double = solve_forces(double_truss)

    for a, b in zip(single.tensions.values(), double.tensions.values()):
        assert b == pytest.approx(2 * a)


def test_solution_is_frame_invariant():
    # the pygame front end works in screen coordinates (y down), the hand
    # calculations in maths coordinates (y up). tensions must not care.
    up, _ = a_frame(load = 2000.0)

    down, nodes = build([(-1, 0), (1, 0), (0, -1)], [(0, 2), (1, 2), (0, 1)])
    A, B, C = nodes
    down.add_constraint(constraint((0, -1), 'pin'), A)
    down.add_constraint(constraint((0, -1), 'roller'), B)
    down.add_force(force((0, 2000)), C)

    a = solve_forces(up)
    b = solve_forces(down)

    assert b.state == status.OK
    for ma, mb in zip(up.members, down.members):
        assert a.tensions[ma] == pytest.approx(b.tensions[mb])


def test_two_perpendicular_rollers_behave_like_a_pin():
    pinned, _ = a_frame(load = 2000.0)

    rolled, nodes = build([(-1, 0), (1, 0), (0, 1)], [(0, 2), (1, 2), (0, 1)])
    A, B, C = nodes
    rolled.add_constraint(constraint((0, 1), 'roller'), A)
    rolled.add_constraint(constraint((1, 0), 'roller'), A)
    rolled.add_constraint(constraint((0, 1), 'roller'), B)
    rolled.add_force(force((0, -2000)), C)

    a = solve_forces(pinned)
    b = solve_forces(rolled)

    assert b.state == status.OK
    for ma, mb in zip(pinned.members, rolled.members):
        assert a.tensions[ma] == pytest.approx(b.tensions[mb])


def test_single_bar_is_a_mechanism_and_cannot_carry_a_transverse_load():
    t, (A, B) = build([(0, 0), (1, 0)], [(0, 1)])
    t.add_constraint(constraint((0, 1), 'pin'), A)
    t.add_force(force((0, -1000)), B)

    sol = solve_forces(t)

    assert sol.state == status.MECHANISM
    assert sol.mechanisms == 1
    assert sol.redundancy == 0
    assert sol.residual > 1.0
    assert "cannot be carried" in sol.message


def test_mechanism_is_reported_even_when_the_load_happens_to_be_carriable():
    # an axial load on the same bar is in equilibrium, but the structure is
    # still unstable and the user needs to be told
    t, (A, B) = build([(0, 0), (1, 0)], [(0, 1)])
    t.add_constraint(constraint((0, 1), 'pin'), A)
    t.add_force(force((1000, 0)), B)

    sol = solve_forces(t)

    assert sol.state == status.MECHANISM
    assert sol.residual == pytest.approx(0.0)
    assert "cannot be carried" not in sol.message


def test_a_floating_node_is_a_mechanism():
    t, _ = a_frame()
    t.add_node(node(5, 5))

    sol = solve_forces(t)

    assert sol.state == status.MECHANISM
    assert sol.mechanisms == 2


def test_extra_member_makes_the_bracket_indeterminate():
    t, (A, B, C) = bracket()
    t.add_member(member(A, B))

    sol = solve_forces(t)

    assert sol.state == status.INDETERMINATE
    assert sol.redundancy == 1
    assert sol.mechanisms == 0
    assert "force method" in sol.message


def test_duplicate_constraints_are_indeterminate_not_a_mechanism():
    # two identical reaction unknowns used to collapse into one dictionary
    # key, leaving an empty column and a bogus mechanism report
    t, (A, B, C) = a_frame()
    t.add_constraint(constraint((0, 1), 'roller'), B)

    sol = solve_forces(t)

    assert sol.state == status.INDETERMINATE
    assert sol.redundancy == 1


def test_no_forces_are_reported_when_the_solve_failed():
    t, (A, B, C) = bracket()
    t.add_member(member(A, B))

    sol = solve_forces(t)

    assert not sol.ok
    assert sol.tensions == {}
    assert sol.reactions == []
    assert sol.tension(t.members[0]) is None


def test_unloaded_determinate_truss_has_zero_forces():
    t, (A, B, C) = a_frame(load = 0.0)
    sol = solve_forces(t)

    assert sol.state == status.OK
    assert all(v == pytest.approx(0.0) for v in sol.tensions.values())
    assert all(r.magnitude == pytest.approx(0.0) for r in sol.reactions)


def test_empty_truss_reports_empty():
    sol = solve_forces(truss())
    assert sol.state == status.EMPTY
    assert not sol.ok


def test_truss_with_no_members_or_constraints():
    t = truss()
    t.add_node(node(0, 0))

    sol = solve_forces(t)

    assert sol.state == status.MECHANISM
    assert sol.tensions == {}


def test_counts_are_reported_in_the_message():
    t, _ = a_frame()
    sol = solve_forces(t)
    assert "3 members + 3 reactions = 6 unknowns, 6 equations, rank 6" in sol.message


def test_solver_rejects_a_member_whose_nodes_are_not_in_the_truss():
    t, (A, B, C) = a_frame()
    t.members.append(member(node(9, 9), node(9, 8)))

    with pytest.raises(ValueError):
        solve_forces(t)
