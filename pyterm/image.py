from typing import Self
from pyterm.colors import COLORS
from pyterm.rect import Rect
import os


class Image:
    def __init__(self, size: tuple[int, int] | list[int, int]):
        self.__size: tuple[int, int] = (size[0], size[1])
        self.__image: str = ""
        self.__pixels: dict[tuple[int, int], tuple[int, int, int]] = {}
        import blessed
        self.__terminal = blessed.Terminal()

    @property
    def pixels(self):
        return self.__pixels

    @property
    def width(self) -> int:
        return self.__size[0]

    @property
    def height(self) -> int:
        return self.__size[1]

    @property
    def size(self) -> tuple[int, int]:
        return self.__size

    def fill(self, color: tuple[int, int, int] | list[int, int, int] | str | None):
        c = color if not isinstance(color, str) else COLORS[color]
        for x in range(self.__size[0]):
            for y in range(self.__size[1]):
                if c is None and (x, y) in self.__pixels:
                    del self.__pixels[(x, y)]
                elif c is not None:
                    self.__pixels[(x, y)] = (color[0], color[1], color[2])

    def blit(self, image: Self, dest: tuple[int, int] | list[int, int]) -> None:
        for pos, pix in image.pixels.items():
            if 0 <= pos[0] <= image.width and 0 <= pos[1] <= image.height and pix is not None:
                self.__pixels[(pos[0] + dest[0], pos[1] + dest[1])] = pix
        # for i in range(image.width):
        #     for j in range(image.height):
        #         pixel = image.get_pixel((i, j))
        #         if pixel is None:
        #             continue
        #         self.__pixels[(i+dest[0], j+dest[1])] = pixel

    def put_pixel(self, pos: tuple[int, int] | list[int, int],
                  color: tuple[int, int, int] | list[int, int, int] | str | None) -> None:
        c = color if not isinstance(color, str) else COLORS[color]
        if c is None and pos in self.__pixels:
            del self.__pixels[pos]
        elif color is not None:
            self.__pixels[pos] = (c[0], c[1], c[2])

    def get_pixel(self, pos: tuple[int, int] | list[int, int]) -> tuple[int, int, int] | None:
        return self.__pixels.get(pos, None)

    def join(self, c):
        if c[0] is None and c[1] is None:
            return " "
        elif c[0] is None:
            return self.__terminal.color_rgb(*c[1]) + "▄" + '\033[0m'
        elif c[1] is None:
            return self.__terminal.color_rgb(*c[0]) + "▀" + '\033[0m'
        else:
            return self.__terminal.color_rgb(*c[0]) + self.__terminal.on_color_rgb(*c[1]) + "▀" + '\033[0m'

    def __to_string(self) -> None:
        scr: list[list[tuple | None]] = [
            [
                None for _ in range(self.__size[0] + 1)
            ].copy() for __ in range(self.__size[1] + 1)
        ]
        self.__image = ""
        for pos, pix in self.__pixels.items():
            if 0 <= pos[0] <= self.__size[0] and 0 <= pos[1] <= self.__size[1]:
                scr[pos[1]][pos[0]] = pix

        self.__image = "\n".join(
            [
                "".join(
                    [
                        self.join([j, scr[i + 1][i2]]) for i2, j in enumerate(scr[i])
                    ]
                ) for i in range(0, len(scr) - 1, 2)
            ]
        )
        # for y in range(self.__size[1], 2):
        #     for x in range(self.__size[0]):
        #         if (x, y) in self.__pixels:
        #             r1, g1, b1 = self.__pixels[(x, y)]
        #         else:
        #             r1, g1, b1 = None, None, None
        #         if (x, y + 1) in self.__pixels:
        #             r2, g2, b2 = self.__pixels[(x, y + 1)]
        #         else:
        #             r2, g2, b2 = None, None, None
        #         if r1 is not None and r2 is not None:
        #             self.__image += self.__terminal.color_rgb(r1, g1, b1) + self.__terminal.on_color_rgb(r2, g2, b2) + "▀"
        #         elif r1 is not None:
        #             self.__image += self.__terminal.color_rgb(*self.__pixels[(x, y)]) + "▀"
        #         elif r2 is not None:
        #             self.__image += self.__terminal.color_rgb(*self.__pixels[(x, y + 1)]) + "▄"
        #         else:
        #             self.__image += " "
        #
        #         self.__image += '\033[0m'
        #     self.__image += "\n"
        # if self.__size[1] % 2 != 0:
        #     y = self.__size[1]
        #     for x in range(self.__size[0]):
        #         if (x, y) in self.__pixels:
        #             r1, g1, b1 = self.__pixels[(x, y)]
        #         else:
        #             r1, g1, b1 = None, None, None
        #         if r1 is not None:
        #             self.__image += self.__terminal.color_rgb(*self.__pixels[(x, y)]) + "▀"
        #         else:
        #             self.__image += " "
        #
        #         self.__image += '\033[0m'
        #     self.__image += "\n"

    def cropped(self, rect: Rect) -> Self:
        image = Image((rect.width, rect.height))
        image.blit(self, (-rect.x, -rect.y))
        return image

    @staticmethod
    def open(filename: os.PathLike | str):
        from PIL import Image as PILImage
        image = PILImage.open(filename)
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        new_image = Image(image.size)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.getpixel((x, y))
                if pixel[3] > 0:
                    new_image.put_pixel((x, y), pixel[:-1])
        return new_image

    def to_rect(self, **keys):
        for key, value in keys.items():
            r = Rect(0, 0, self.width, self.height)
            match key:
                case "center":
                    r.center = value
                case "topleft":
                    r.topleft = value
                case "topright":
                    r.topright = value
                case "bottomleft":
                    r.bottomleft = value
                case "bottomright":
                    r.bottomright = value
                case "left":
                    r.x = value
                case "right":
                    r.x = value - r.width
                case "top":
                    r.y = value
                case "bottom":
                    r.y = value - r.height
                case _:
                    raise ValueError(f"Invalid key: {key}")
        return r
