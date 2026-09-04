import numpy as np

from core.model import node, member, force, constraint, truss

# tests are written in maths coordinates (y up) because that is how the hand
# calculations were done. the solver is frame agnostic, see test_frame_invariance.


def build(coords, pairs):
    t = truss()
    nodes = [t.add_node(node(x, y)) for x, y in coords]
    for i, j in pairs:
        t.add_member(member(nodes[i], nodes[j]))
    return t, nodes


def nodal_residual(t, sol, nd):
    total = np.zeros(2)

    for f in nd.forces:
        total = total + f.vector

    for m in t.members_at(nd):
        d = m.direction
        total = total + sol.tensions[m] * (d if m.node1 is nd else -d)

    return total + sol.reaction_at(nd)


def assert_in_equilibrium(t, sol, tol = 1e-8):
    for nd in t.nodes:
        assert np.allclose(nodal_residual(t, sol, nd), 0, atol = tol), \
            f"node {nd.id} out of equilibrium: {nodal_residual(t, sol, nd)}"


def bracket(load = 1000.0):
    """Two bar bracket off a wall.

        A (0,1) o---.
                |    \\  member AC
                |     \\
        B (0,0) o------o C (1,0)   <- load P downward
                 member BC

    both A and B are pinned to the wall. by hand:
      node C:  T_AC / sqrt2 = P        ->  T_AC = +P*sqrt2   (tension)
               T_BC = -T_AC / sqrt2    ->  T_BC = -P         (compression)
    """
    t, nodes = build([(0, 1), (0, 0), (1, 0)], [(0, 2), (1, 2)])
    A, B, C = nodes

    t.add_constraint(constraint((0, 1), 'pin'), A)
    t.add_constraint(constraint((0, 1), 'pin'), B)
    t.add_force(force((0, -load)), C)

    return t, nodes


def a_frame(load = 2000.0):
    """Symmetric triangle, pin at A, vertical roller at B, load at the apex.

              C (0,1)
              / \\
             /   \\
    A (-1,0) o---o B (1,0)

    by symmetry each support carries P/2 vertically. at the apex:
      T_AC = T_BC = -P / sqrt2   (compression)
    and at A:  T_AB = P/2        (tension)
    """
    t, nodes = build([(-1, 0), (1, 0), (0, 1)], [(0, 2), (1, 2), (0, 1)])
    A, B, C = nodes

    t.add_constraint(constraint((0, 1), 'pin'), A)
    t.add_constraint(constraint((0, 1), 'roller'), B)
    t.add_force(force((0, -load)), C)

    return t, nodes
