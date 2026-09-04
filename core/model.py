import itertools

from core import geometry as geom

COINCIDENT_TOL = 1e-6


class force(object):

    def __init__(self, vector, label = None):
        self.vector = geom.vec(vector)
        self.label = label

    @classmethod
    def from_polar(cls, magnitude, angle_radians, label = None):
        return cls(magnitude * geom.unit(angle_radians), label)

    @property
    def magnitude(self):
        return geom.norm(self.vector)

    @property
    def angle(self):
        return geom.angle_of(self.vector)

    @property
    def text(self):
        return self.label if self.label is not None else str(round(self.magnitude, 2))


class constraint(object):

    # 'roller' resists along its normal only, 'pin' resists in both directions.
    # a built in support (3 reactions) needs moment equilibrium, which a pin
    # jointed solver does not have.
    REACTIONS = {'roller': 1, 'pin': 2}

    def __init__(self, normal, type = 'roller'):
        if type not in self.REACTIONS:
            raise ValueError(f"unknown constraint type {type!r}")

        self.normal = geom.normalise(normal)
        self.type = type

    @classmethod
    def from_angle(cls, angle_radians, type = 'roller'):
        return cls(geom.unit(angle_radians), type)

    @property
    def angle(self):
        return geom.angle_of(self.normal)

    @property
    def reaction_directions(self):
        if self.type == 'pin':
            return [self.normal, geom.perpendicular(self.normal)]
        return [self.normal]


class node(object):

    _ids = itertools.count()

    def __init__(self, x, y, mass = 0):

        self.id = next(self._ids)

        self.pos = geom.vec((x, y))
        self.mass = mass

        self.forces = []
        self.constraints = []

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    def move_to(self, p):
        self.pos = geom.vec(p)

    def is_at(self, p, tol = COINCIDENT_TOL):
        return geom.distance_between_points(self.pos, p) <= tol


class member(object):

    def __init__(self, node1, node2, mass_per_unit_length = 0):
        if node1 is node2:
            raise ValueError("a member cannot join a node to itself")
        if node1.is_at(node2.pos):
            raise ValueError("a member cannot have zero length")

        self.node1 = node1
        self.node2 = node2
        self.mass_per_unit_length = mass_per_unit_length

    # geometry is derived so it stays correct if a node is moved

    @property
    def vector(self):
        return self.node2.pos - self.node1.pos

    @property
    def length(self):
        return geom.norm(self.vector)

    @property
    def direction(self):
        return geom.normalise(self.vector)

    @property
    def angle(self):
        return geom.angle_of(self.vector)

    @property
    def midpoint(self):
        return 0.5 * (self.node1.pos + self.node2.pos)

    @property
    def mass(self):
        return self.length * self.mass_per_unit_length

    def joins(self, nd):
        return self.node1 is nd or self.node2 is nd


class truss(object): # made from nodes and members

    def __init__(self):
        self.nodes = []
        self.members = []
        self.revision = 0

    def touch(self):
        # bumped on every edit so cached solutions can be invalidated
        self.revision += 1

    def node_at(self, pos, tol = COINCIDENT_TOL):
        for n in self.nodes:
            if n.is_at(pos, tol):
                return n
        return None

    def add_node(self, nd, tol = COINCIDENT_TOL):
        if not isinstance(nd, node):
            return None

        existing = self.node_at(nd.pos, tol)
        if existing is not None:
            return existing

        self.nodes.append(nd)
        self.touch()
        return nd

    def add_member(self, mber):
        if not isinstance(mber, member):
            return None

        for m in self.members:
            if m.joins(mber.node1) and m.joins(mber.node2):
                return m

        for nd in (mber.node1, mber.node2):
            if nd not in self.nodes:
                self.nodes.append(nd)

        self.members.append(mber)
        self.touch()
        return mber

    def add_force(self, frce, nd):
        if not isinstance(frce, force):
            return None

        nd.forces.append(frce)
        self.touch()
        return frce

    def add_constraint(self, cstrnt, nd):
        if not isinstance(cstrnt, constraint):
            return None

        nd.constraints.append(cstrnt)
        self.touch()
        return cstrnt

    def members_at(self, nd):
        return [m for m in self.members if m.joins(nd)]

    def node_of(self, entity):
        for nd in self.nodes:
            if entity in nd.forces or entity in nd.constraints:
                return nd
        return None

    def delete_node(self, nd):
        if nd not in self.nodes:
            return

        for m in self.members_at(nd): # copy, delete_member mutates self.members
            self.delete_member(m)

        nd.forces = []
        nd.constraints = []

        self.nodes.remove(nd)
        self.touch()

    def delete_member(self, mber):
        if mber in self.members:
            self.members.remove(mber)
            self.touch()

    def delete_force(self, frce, nd = None):
        for n in ([nd] if nd is not None else self.nodes):
            if frce in n.forces:
                n.forces.remove(frce)
                self.touch()
                return

    def delete_constraint(self, cstrnt, nd = None):
        for n in ([nd] if nd is not None else self.nodes):
            if cstrnt in n.constraints:
                n.constraints.remove(cstrnt)
                self.touch()
                return

    def delete_entity(self, entity):
        if isinstance(entity, node):
            self.delete_node(entity)
        elif isinstance(entity, member):
            self.delete_member(entity)
        elif isinstance(entity, force):
            self.delete_force(entity)
        elif isinstance(entity, constraint):
            self.delete_constraint(entity)

    def get_all_entities(self):
        for n in self.nodes:
            yield n
        for m in self.members:
            yield m
        for nd in self.nodes:
            for f in nd.forces:
                yield f
            for c in nd.constraints:
                yield c

    def reaction_count(self):
        return sum(len(c.reaction_directions) for nd in self.nodes for c in nd.constraints)
