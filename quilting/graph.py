from point import Point
from sys import stderr
from math import pi, atan2, sin, cos, ceil, sqrt
from random import choice

class Vertex:
    def __init__(self, pos, i):
        self.pos = pos
        self.neighbors = []
        self.doubled_neighbors = []
        self.index = i
        self.faces = []

    def angle_to(self, v):
        return self.pos.angle_to(v.pos)

class Face:
    def __init__(self, vertices, density):
        self.vertices = vertices
        for v in self.vertices:
            v.faces.append(self)
        self.filled = False
        self.density = density

class Graph:
    def __init__(self, obj):
        self.vertices = []
        self.faces = []
        density = -1
        for row in obj:
            symbols = row.split()
            if symbols[0] == 'v':
                pos = Point(float(symbols[1]), -float(symbols[3]))
                self.vertices.append(Vertex(pos, len(self.vertices)))
            elif symbols[0] == 'usemtl':
                density = int(symbols[1])
            elif symbols[0] == 'f':
                vertices = [int(s.split('//')[0]) - 1 for s in symbols[1:]]
                for i in range(1, len(vertices)):
                    for j in range(i):
                        self.add_edge(vertices[i], vertices[j])
                self.faces.append(Face([self.vertices[i] for i in vertices], density))
                if density > 0 and len(vertices) > 3:
                    raise Exception("tried to shade a non-triangular face")

    def add_edge(self, a, b):
        if self.vertices[b] not in self.vertices[a].neighbors:
            self.vertices[a].neighbors.append(self.vertices[b])
            self.vertices[b].neighbors.append(self.vertices[a])


    def create_doubled_edges(self):
        for v in self.vertices:
            v.doubled_neighbors = []

        for v in self.vertices:
            for w in v.neighbors:
                v.doubled_neighbors.append(w)
                v.doubled_neighbors.append(w)

    def remove_doubled_edge(self, a, b):
        a.doubled_neighbors.remove(b)
        b.doubled_neighbors.remove(a)

    def contains_edges(self, vertex_list, traversal):
        for i in range(len(vertex_list)):
            if vertex_list[i].doubled_neighbors:
                return (vertex_list[i], traversal.index(vertex_list[i].pos))
        return None, None

    def corner_vertex_index(self):
        distances_from_corners = [v.pos.norm() for v in self.vertices]
        return distances_from_corners.index(max(distances_from_corners))

    def fill(self, face, start_vertex):
        if len(face.vertices) != 3:
            print('Warning: ignoring command to fill non-triangular face', file=stderr)
            return

        face.filled = True


        start_index = face.vertices.index(start_vertex)
        vertex_a = face.vertices[start_index]
        vertex_b = face.vertices[(start_index + 1) % 3]
        vertex_c = face.vertices[(start_index + 2) % 3]

        self.remove_doubled_edge(vertex_a, vertex_b);
        self.remove_doubled_edge(vertex_b, vertex_c);
        self.remove_doubled_edge(vertex_c, vertex_a);

        a = vertex_a.pos
        b = vertex_b.pos
        c = vertex_c.pos

        len_a_side = (b-c).norm()
        len_b_side = (a-c).norm()
        len_c_side = (a-b).norm()
        s = (len_a_side + len_b_side + len_c_side)/2 #semiperimeter
        altitude = 2/len_a_side * sqrt(s * (s-len_a_side) * (s-len_b_side) * (s-len_c_side))

        n = ceil(face.density * altitude) // 2 * 2 + 1
        positions = []

        for i in range(1, n, 2):
            s = i/n
            pos_a_b = (1-s)*a + s*b
            pos_a_c = (1-s)*a + s*c
            positions += [pos_a_b, pos_a_c]

            s = (i+1)/n
            pos_a_b = (1-s)*a + s*b
            pos_a_c = (1-s)*a + s*c
            positions += [pos_a_c, pos_a_b]

        if n % 2 == 1:
            positions += [b, c]
            for i in range(n-1, 1, -2):
                s = i/n
                pos_a_b = (1-s)*a + s*b
                pos_a_c = (1-s)*a + s*c
                positions += [pos_a_c, pos_a_b]

                s = (i-1)/n
                pos_a_b = (1-s)*a + s*b
                pos_a_c = (1-s)*a + s*c
                positions += [pos_a_b, pos_a_c]

            positions.append(a)
        else:
            for i in range(n-1, 0, -2):
                s = i/n
                pos_a_b = (1-s)*a + s*b
                pos_a_c = (1-s)*a + s*c
                positions += [pos_a_b, pos_a_c]

                s = (i-1)/n
                pos_a_b = (1-s)*a + s*b
                pos_a_c = (1-s)*a + s*c
                positions += [pos_a_c, pos_a_b]

            positions.append(a)

        return ([vertex_a, vertex_b, vertex_c], positions)


    def doubled_traversal(self):
        self.create_doubled_edges()
        traversal = []
        visited_vertices = []
        start = self.vertices[self.corner_vertex_index()]
        not_done = True
        index = None

        while not_done:
            loop = []
            curr = start
            incoming_angle = None
            while curr is not None:
                loop.append(curr.pos)
                visited_vertices.append(curr)
                for f in curr.faces:
                    if f.density > 0 and not f.filled:
                        vertices, points = self.fill(f, curr)
                        visited_vertices += vertices
                        loop += points
                if curr.doubled_neighbors:
                    next_vertex = choice(curr.doubled_neighbors)
                    self.remove_doubled_edge(curr, next_vertex)
                    curr = next_vertex
                else:
                    curr = None

            if index is None:
                traversal = loop
            else:
                traversal = traversal[0:index] + loop + traversal[index+1:]

            start, index = self.contains_edges(visited_vertices, traversal)
            not_done = (start is not None)

        return traversal

    def traversal_point_list(self):
        positions = self.doubled_traversal()
        return normalize_points(positions)

def normalize_points(points):
    max_x = max([p.x for p in points])
    min_x = min([p.x for p in points])
    max_y = max([p.y for p in points])
    min_y = min([p.y for p in points])
    normalized_points = []
    scale = max(max_x-min_x, max_y-min_y)
    off_x = 0
    off_y = 0

    if (max_x-min_x > max_y-min_y):
        off_y = 0.5 * (max_x-min_x - (max_y-min_y))
    else:
        off_x = 0.5 * (max_y-min_y - (max_x-min_x))
    for p in points:
        normalized_x = (p.x - min_x + off_x) / scale
        normalized_y = (p.y - min_y + off_y) / scale
        normalized_points.append(Point(normalized_x, normalized_y))
    return normalized_points
