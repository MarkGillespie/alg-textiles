from math import sqrt, pi, sin, cos, atan2

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def norm(self):
        return sqrt(self.x**2 + self.y**2)

    def __add__(self, pt):
        return Point(self.x + pt.x, self.y + pt.y)

    def __sub__(self, pt):
        return Point(self.x - pt.x, self.y - pt.y)

    def __mul__(self, scalar):
        return Point(scalar * self.x, scalar * self.y)

    def __rmul__(self, scalar):
        return Point(scalar * self.x, scalar * self.y)

    def __truediv__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)

    def __eq__(self, pt):
        return (self.x == pt.x) and (self.y == pt.y)

    def rotate(self, theta):
        return Point(self.x * cos(theta) - self.y * sin(theta), self.x * sin(theta) + self.y * cos(theta))

    def length(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def __str__(self):
        return '{' + str(self.x) + ', ' + str(self.y) + '}'

    def __round__(self):
        return Point(round(self.x), round(self.y))

    def angle_to(self, pt):
        return atan2(pt.y - self.y, pt.x - self.x)
