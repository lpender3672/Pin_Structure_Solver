import numpy as np

from core import geometry as geom
from core.model import member


class status:
    OK = 'ok'
    EMPTY = 'empty'
    INDETERMINATE = 'indeterminate'
    MECHANISM = 'mechanism'
    NUMERICAL = 'numerical'


class reaction(object):

    def __init__(self, nd, cstrnt, direction, magnitude):
        self.node = nd
        self.constraint = cstrnt
        self.direction = geom.vec(direction)
        self.magnitude = magnitude

    @property
    def vector(self):
        return self.magnitude * self.direction


class solution(object):

    def __init__(self, state, message, tensions = None, reactions = None,
                 redundancy = 0, mechanisms = 0, residual = 0.0):

        self.state = state
        self.message = message
        self.tensions = tensions if tensions is not None else {}
        self.reactions = reactions if reactions is not None else []
        self.redundancy = redundancy   # unknowns - rank, degree of indeterminacy
        self.mechanisms = mechanisms   # equations - rank, degrees of freedom
        self.residual = residual

    @property
    def ok(self):
        return self.state == status.OK

    def tension(self, mber):
        return self.tensions.get(mber)

    def reaction_at(self, nd):
        total = np.zeros(2)
        for r in self.reactions:
            if r.node is nd:
                total = total + r.vector
        return total


def assemble(trss):
    # one horizontal and one vertical equilibrium equation per node.
    # unknowns are member tensions followed by constraint reactions.
    rows = {nd: 2 * i for i, nd in enumerate(trss.nodes)}

    unknowns = list(trss.members)
    for nd in trss.nodes:
        for c in nd.constraints:
            for d in c.reaction_directions:
                unknowns.append((nd, c, d))

    A = np.zeros((2 * len(trss.nodes), len(unknowns)))
    b = np.zeros(2 * len(trss.nodes))

    for col, u in enumerate(unknowns):
        if isinstance(u, member):
            if u.node1 not in rows or u.node2 not in rows:
                raise ValueError("member references a node that is not in the truss")

            # positive tension pulls each end toward the other
            d = u.direction
            A[rows[u.node1]:rows[u.node1] + 2, col] += d
            A[rows[u.node2]:rows[u.node2] + 2, col] -= d
        else:
            nd, _, d = u
            A[rows[nd]:rows[nd] + 2, col] += d

    for nd in trss.nodes:
        for f in nd.forces:
            b[rows[nd]:rows[nd] + 2] -= f.vector

    return A, b, unknowns


def solve_forces(trss, tol = 1e-9):

    if len(trss.nodes) == 0:
        return solution(status.EMPTY, "Nothing to solve: draw some nodes and members first.")

    A, b, unknowns = assemble(trss)
    num_equations, num_unknowns = A.shape

    if num_unknowns == 0:
        return solution(status.MECHANISM,
                        "No members or constraints: nothing can carry a load.",
                        mechanisms = num_equations,
                        residual = geom.norm(b) if b.any() else 0.0)

    rank = int(np.linalg.matrix_rank(A))
    redundancy = num_unknowns - rank   # self stress states
    mechanisms = num_equations - rank  # inextensional mechanisms

    x, _, _, _ = np.linalg.lstsq(A, b, rcond = None)

    # lstsq only returns residuals when the system is overdetermined and full
    # rank, so compute it here instead and scale it against the applied load
    residual = float(np.linalg.norm(A @ x - b))
    scale = float(np.linalg.norm(b))
    relative = residual / scale if scale > tol else residual

    counts = (f"{len(trss.members)} members + {trss.reaction_count()} reactions "
              f"= {num_unknowns} unknowns, {num_equations} equations, rank {rank}")

    if redundancy > 0:
        message = (f"Statically indeterminate to degree {redundancy} ({counts}). "
                   "Needs the force method or FEM.")
        if mechanisms > 0:
            message += f" It is also a mechanism with {mechanisms} degree(s) of freedom."
        return solution(status.INDETERMINATE, message,
                        redundancy = redundancy, mechanisms = mechanisms, residual = residual)

    if mechanisms > 0:
        message = f"Mechanism with {mechanisms} degree(s) of freedom ({counts})."
        if relative > tol:
            message += " The applied load cannot be carried."
        return solution(status.MECHANISM, message,
                        redundancy = redundancy, mechanisms = mechanisms, residual = residual)

    if relative > tol:
        return solution(status.NUMERICAL,
                        f"Determinate but equilibrium is not satisfied, residual {residual:.3e}.",
                        redundancy = redundancy, mechanisms = mechanisms, residual = residual)

    tensions = {}
    reactions = []
    for col, u in enumerate(unknowns):
        if isinstance(u, member):
            tensions[u] = float(x[col])
        else:
            nd, c, d = u
            reactions.append(reaction(nd, c, d, float(x[col])))

    return solution(status.OK, f"Statically determinate and stable ({counts}).",
                    tensions = tensions, reactions = reactions,
                    redundancy = redundancy, mechanisms = mechanisms, residual = residual)


def solve_displacements(trss):
    pass

    # be nice if we could draw displaced shape too
