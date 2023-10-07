import random


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def random_in_range(cls, point_start, point_end):
        return cls(random.randint(point_start[0], point_end[0]), random.randint(point_start[1], point_end[1]))

    def offset(self, offsets):
        return Point(self.x + offsets.x, self.y + offsets.y)
