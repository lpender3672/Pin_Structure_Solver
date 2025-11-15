
import pygame
import numpy as np

from member import member
from node import node
from utils import utils,line

def draw_line_dashed(surface, color, start_pos, end_pos, width = 1, dash_length = 10, exclude_corners = True):

    # convert tuples to numpy arrays
    start_pos = np.array(start_pos)
    end_pos   = np.array(end_pos)

    length = np.linalg.norm(end_pos - start_pos)
    length = max(length, 0.1)  # prevent division by zero
    length = min(length, 1000)  # prevent too many dashes

    dash_amount = int(length / dash_length)

    dash_knots = np.array([np.linspace(start_pos[i], end_pos[i], dash_amount) for i in range(2)]).transpose()

    return [pygame.draw.line(surface, color, tuple(dash_knots[n]), tuple(dash_knots[n+1]), width)
            for n in range(int(exclude_corners), dash_amount - int(exclude_corners), 2)]


class mouse(object):
    
    def __init__(self, disp, pos = None):

        self.disp = disp
        self.closest_node = None

        self.SNAP_DISTANCE_THRESHOLD = 10

        if pos == None:
            self.x, self.y = pygame.mouse.get_pos()
        else:
            self.x = pos[0]
            self.y = pos[1]

        self.cursor_updated = False
        self.snapped_to_node = False
    
    def to_node(self, node_id, mass = 0):
        return node(node_id, self.x, self.y, mass)

    def __list__(self):
        return [self.x, self.y]

    def pos(self):
        return np.array([self.x, self.y])
    
    def update(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.cursor_updated = True
    
    
    def snap_line(self, truss, draw_from_node = None):

        #closest_node = min(truss.nodes, key = lambda node : np.linalg.norm(node.pos - self.pos()))
        if draw_from_node is None:
            draw_from_node = truss.nodes[-1]

        n = draw_from_node.pos

        # lines at 30, 60, 90, 120, 150 degrees   
        lines = [
            line(np.array([1, 0]), n),
            line(np.array([0, 1]), n),
        ]
        
        lines_30 = [
            line(np.array([np.cos(np.pi/6), np.sin(np.pi/6)]), n),
            line(np.array([np.cos(np.pi/3), np.sin(np.pi/3)]), n),
            line(np.array([np.cos(np.pi/2), np.sin(np.pi/2)]), n),
            line(np.array([np.cos(2*np.pi/3), np.sin(2*np.pi/3)]), n),
            line(np.array([np.cos(5*np.pi/6), np.sin(5*np.pi/6)]), n)
        ]

        lines_45 = [
            line(np.array([np.cos(np.pi/4), np.sin(np.pi/4)]), n),
            line(np.array([np.cos(3*np.pi/4), np.sin(3*np.pi/4)]), n)
        ]
        #lines.extend(lines_30)
        #lines.extend(lines_45)

        members_connected = [m for m in truss.members if m.node1 == draw_from_node or m.node2 == draw_from_node]
        if len(members_connected) == 0:
            return
        for m in members_connected:
            lines.append(line(m.d, n)) # line along another connected member
            lines.append(line(utils.perpendicular(m.d), n)) # line perpendicular to a connected member
        
        members_not_connected = [m for m in truss.members if m.node1 != draw_from_node and m.node2 != draw_from_node]
        for m in members_not_connected[:-2]:
            lines.append(line(m.d, n)) # line parallel to not connected members

        dists = [l.distance_to_point(self.pos()) for l in lines]
        sorted_dists_idx = np.argsort(dists)

        # if two lines are very close set cursor to their intersection
        if (dists[sorted_dists_idx[0]] < 20) and (dists[sorted_dists_idx[1]] < 20):

            pos = utils.line_intersection(lines[sorted_dists_idx[0]], lines[sorted_dists_idx[1]])
            if pos is not None:
                self.x = pos[0]
                self.y = pos[1]
                self.cursor_updated = True
                return
        
        else:
            closest_line = lines[np.argmin(dists)]
            d = utils.normalise(closest_line.d)
            
            pos = n + d * (self.pos() - n).dot(d)
            self.x = pos[0]
            self.y = pos[1] 
            self.cursor_updated = True

        # perpendicular to existing beams

    def if_snap_point(self, nodes):
        if nodes is None or len(nodes) == 0:
            return False
        
        f = lambda node : np.linalg.norm(node.pos - self.pos())
        self.closest_node = min(nodes, key = f)
        return f(self.closest_node) < self.SNAP_DISTANCE_THRESHOLD
            

    def snap_point(self, truss, draw_from_node = None):    

        if len(truss.nodes) == 0:
            return
        
        if draw_from_node is None:
            draw_from_node = truss.nodes[-1]
        
        nodes_not_connected = [n for n in truss.nodes if n != draw_from_node]

        if self.if_snap_point(nodes_not_connected):
          # snapped to node
            self.x = self.closest_node.x
            self.y = self.closest_node.y
            self.cursor_updated = True
            self.snapped_to_node = True
            return

        lines = []

        lines.append(line(np.array([1, 0]), draw_from_node.pos))
        lines.append(line(np.array([0, 1]), draw_from_node.pos))

        drawn_line = line(utils.normalise(self.pos() - draw_from_node.pos), draw_from_node.pos)
        
        pnd_drawn = utils.perpendicular(drawn_line.d)
        drawn_dir_aligned = utils.is_axis_aligned(drawn_line.d, tol=1e-3)
        
        for n in nodes_not_connected:
            # snap point to be parallel and perpendicular with current drawn node
            if not drawn_dir_aligned:
                # parallel to drawn line is handled by drawn_line_to_node_dists
                #lines.append(line(drawn_line.d, n.pos))
                lines.append(line(pnd_drawn, n.pos))
            else:
                lines.append(line(np.array([1, 0]), n.pos))
                lines.append(line(np.array([0, 1]), n.pos))
            
            members_connected = [m for m in truss.members if m.node1 == n or m.node2 == n]
            for m in members_connected:
                # snap to member parallel and perpendicular lines
                lines.append(line(m.d, n.pos))
                pnd = utils.perpendicular(m.d)
                lines.append(line(pnd, n.pos))


            members_not_connected = [m for m in truss.members if m.node1 != n and m.node2 != n]
            for m in members_not_connected:
                if utils.is_axis_aligned(m.d, tol=1e-3):
                    lines.append(line(np.array([1, 0]), n.pos))
                    lines.append(line(np.array([0, 1]), n.pos))

        
        if len(lines) == 0:
            return
        
        for l in lines:
            pygame.draw.line(self.disp, (200, 200, 200), l.p, l.p + l.d * 50, 1)

        mouse_to_line_dists = [l.distance_to_point(self.pos()) for l in lines]
        sorted_ldists_idx = np.argsort(mouse_to_line_dists)
        drawn_line_to_node_dists = [drawn_line.distance_to_point(n.pos) for n in nodes_not_connected]
        sorted_ndists_idx = np.argsort(drawn_line_to_node_dists)

        #print(dists)

        # if two lines are very close set cursor to their intersection
        if ((mouse_to_line_dists[sorted_ldists_idx[0]] < 20) and 
            (mouse_to_line_dists[sorted_ldists_idx[1]] < 20)):

            pos = utils.line_intersection(lines[sorted_ldists_idx[0]], lines[sorted_ldists_idx[1]])
            if pos is not None:

                draw_line_dashed(self.disp, (0, 0, 0), lines[sorted_ldists_idx[0]].p, pos, width = 2, dash_length = 10)
                draw_line_dashed(self.disp, (0, 0, 0), lines[sorted_ldists_idx[1]].p, pos, width = 2, dash_length = 10)

                self.x = pos[0]
                self.y = pos[1]
                self.cursor_updated = True
                return
        
        if (len(nodes_not_connected) > 0 and 
            drawn_line_to_node_dists[sorted_ndists_idx[0]] < 20):

            n = nodes_not_connected[sorted_ndists_idx[0]]

            d = nodes_not_connected[sorted_ndists_idx[0]].pos - draw_from_node.pos
            dlen = np.linalg.norm(d)
            if np.isclose(dlen, 0):
                return
            
            pos = n.pos + d * (self.pos() - n.pos).dot(d) / dlen**2

            #draw_line_dashed(self.disp, (0, 0, 0), n.pos, pos, width = 2, dash_length = 10)

            self.x = pos[0]
            self.y = pos[1] 
            self.cursor_updated = True
            return
            
        if mouse_to_line_dists[sorted_ldists_idx[0]] < 20:

            d = utils.normalise(lines[sorted_ldists_idx[0]].d)
            n = lines[sorted_ldists_idx[0]].p
        
            pos = n + d * (self.pos() - n).dot(d)

            draw_line_dashed(self.disp, (0, 0, 0), n, pos, width = 2, dash_length = 10)

            self.x = pos[0]
            self.y = pos[1] 
            self.cursor_updated = True
        
    def get_hover_entities(self, truss): # iterator
        p = self.pos()

        for n in truss.nodes:
            if np.linalg.norm(n.pos - self.pos()) < self.SNAP_DISTANCE_THRESHOLD:
                yield n

            for f in n.forces:
                start = f.start_pos
                end = start + pygame.Vector2(f.vector.tolist())
                d = end - start
                seg_len2 = d.dot(d)
                if seg_len2 == 0:
                    continue
                
                t = np.dot(p - start, d) / seg_len2
                if 0 <= t <= 1:

                    proj = start + t * d
                    dist = np.linalg.norm(p - proj)
                    if dist < self.SNAP_DISTANCE_THRESHOLD:
                        yield f
        
            for c in n.constraints:
                if np.linalg.norm(c.ground_point - self.pos()) < self.SNAP_DISTANCE_THRESHOLD:
                    yield c
        
        for m in truss.members:
            p1 = m.node1.pos
            p2 = m.node2.pos
            d  = p2 - p1
            seg_len2 = np.dot(d, d)
            if seg_len2 == 0:
                continue
            
            t = np.dot(p - p1, d) / seg_len2
            if 0 <= t <= 1:

                proj = p1 + t * d
                dist = np.linalg.norm(p - proj)
                if dist < self.SNAP_DISTANCE_THRESHOLD:
                    yield m

    def get_nearest_node(self, truss):
        if len(truss.nodes) == 0:
            return None
        
        f = lambda node : np.linalg.norm(node.pos - self.pos())
        closest_node = min(truss.nodes, key = f)
        return closest_node
    