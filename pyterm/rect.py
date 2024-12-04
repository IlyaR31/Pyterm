from typing import Self


class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def to_tuple(self):
        return self.x, self.y, self.width, self.height

    @property
    def topleft(self):
        return self.x, self.y

    @topleft.setter
    def topleft(self, value):
        self.x, self.y = value

    @property
    def topright(self):
        return self.x + self.width, self.y

    @topright.setter
    def topright(self, value):
        self.x, self.y = value[0] - self.width, value[1]

    @property
    def bottomleft(self):
        return self.x, self.y + self.height

    @bottomleft.setter
    def bottomleft(self, value):
        self.x, self.y = value[0] - self.height, value[1]

    @property
    def bottomright(self):
        return self.x + self.width, self.y + self.height

    @bottomright.setter
    def bottomright(self, value):
        self.x, self.y = value[0] - self.width, value[1] - self.height

    @property
    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2

    @center.setter
    def center(self, value):
        self.x, self.y = value[0] - self.width // 2, value[1] - self.height // 2

    def colliderect(self, rect: Self):
        return (
            self.x < rect.x + rect.width and
            self.x + self.width > rect.x and
            self.y < rect.y + rect.height and
            self.y + self.height > rect.y
        )

    def collidepoint(self, point: tuple[int, int]):
        return (
            self.x <= point[0] < self.x + self.width and
            self.y <= point[1] < self.y + self.height
        )

    def collidepoints(self, points):
        return any(self.collidepoint(point) for point in points)

    def copy(self):
        return Rect(self.x, self.y, self.width, self.height)
