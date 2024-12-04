from pyterm.image import Image
import math


def scale(surface, new_size: tuple[int, int]):
    new_surface = Image(new_size)
    scale_x = new_surface.width / surface.width
    scale_y = new_surface.height / surface.height

    for x in range(surface.width):
        for y in range(surface.height):
            new_x = int(x * scale_x)
            new_y = int(y * scale_y)
            new_surface.put_pixel((new_x, new_y), surface.get_pixel((x, y)))

    return new_surface


def scale2x(surface):
    return scale(surface, (surface.width * 2, surface.height * 2))


def scale_by(surface: Image, scale_factor):
    return scale(surface, (int(surface.width * scale_factor[0]), int(surface.height * scale_factor[1])))


def flip(surface: Image, flip_x, flip_y):
    new_surface = Image(surface.size)
    for x in range(surface.width):
        for y in range(surface.height):
            new_x = x if not flip_x else surface.width - 1 - x
            new_y = y if not flip_y else surface.height - 1 - y
            new_surface.put_pixel((new_x, new_y), surface.get_pixel((x, y)))

    return new_surface


def rotate(surface: Image, degree: int):
    # surface2 = scale_by(surface, (0.5, 0.5))
    radian = degree * (3.141592653589793 / 180)
    min_x, min_y = None, None
    max_x, max_y = 0, 0
    for x in range(surface.width):
        for y in range(surface.height):
            new_x = round(x * math.cos(radian) - y * math.sin(radian))
            new_y = round(x * math.sin(radian) + y * math.cos(radian))
            if new_x > max_x:
                max_x = new_x
            if new_y > max_y:
                max_y = new_y
            if min_x is None:
                min_x = new_x
            elif min_x > new_x:
                min_x = new_x

            if min_y is None:
                min_y = new_y
            elif min_y > new_y:
                min_y = new_y

    new_surface = Image((max_x + abs(min_x), max_y + abs(min_y)))

    for x in range(surface.width):
        for y in range(surface.height):
            for f1 in [int, round]:
                for f2 in [int, round]:
                    new_x = f1(x * math.cos(radian) - y * math.sin(radian)) + abs(min_x)
                    new_y = f2(x * math.sin(radian) + y * math.cos(radian)) + abs(min_y)
                    new_surface.put_pixel((new_x, new_y), surface.get_pixel((x, y)))
            # for nx in [0, 1]:
            #     for ny in [0, 1]:
            #         if new_surface.get_pixel((new_x+nx, new_y+ny)) is not None:
            #             continue
            #         new_surface.put_pixel((new_x+nx, new_y+ny), surface.get_pixel((x, y)))


    # new_surface = scale_by(new_surface, (2, 2))

    return new_surface
