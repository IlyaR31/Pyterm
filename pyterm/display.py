from pyterm.image import Image
from pyterm.colors import COLORS
import threading
import sys
import os
import pyterm.events as events
import pyterm.keys as keys


class Display:
    def __init__(self, size, *args):
        self.__size: tuple[int, int] = (size[0], size[1])
        import blessed
        self.__terminal: blessed.Terminal = blessed.Terminal()
        self.__unpack_args(args)
        self.__ended: bool = False
        self.__screen: str = ""
        self.__pixels: dict[tuple[int, int], tuple[int, int, int]] = {}
        self.__stdout = sys.stdout
        # self.__stdout = os.fdopen(
        #     sys.stdout.fileno(),
        #     "w",
        #     -1  # 2 * self.__terminal.width * self.__terminal.height
        # )
        self.__stdout.write(self.__terminal.clear())
        self.__stdout.flush()
        self._fill = None
        self.__min_width, self.__min_height = self.__terminal.width, self.__terminal.height*2
        self.__setup()

    def __clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def __on_resize(self, sig, action):
        self.__min_width, self.__min_height = self.__terminal.width, self.__terminal.height*2
        self.__clear()

    def __setup(self):
        import signal
        signal.signal(signal.SIGWINCH, self.__on_resize)

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
        if c is None:
            self.__pixels = {}
            return
        for x in range(self.__size[0]+1):
            for y in range(self.__size[1]):
                self.__pixels[(x, y)] = (c[0], c[1], c[2])

    def blit(self, image: Image, dest: tuple[int, int] | list[int, int]):
        for pos, pix in image.pixels.items():
            if 0 <= pos[0] <= image.width and 0 <= pos[1] <= image.height and pix is not None:
                self.__pixels[(pos[0] + dest[0], pos[1] + dest[1])] = pix
        # for i in range(image.width):
        #     for j in range(image.height):
        #         pixel = image.get_pixel((i, j))
        #         if pixel is None:
        #             continue
        #         self.__pixels[(i+dest[0], j+dest[1])] = pixel

    def __unpack_args(self, args: list | tuple) -> None:
        if keys.FULLSCREEN in args:
            self.__size = (self.__terminal.width-1, self.__terminal.height*2-3)
        if keys.FULLWIDTH in args:
            self.__size = (self.__terminal.width-1, self.__size[1])
        if keys.FULLHEIGHT in args:
            self.__size = (self.__size[0], self.__terminal.height*2-3)

    def get_pixel(self, pos: tuple[int, int] | list[int, int]) -> tuple[int, int, int] | None:
        return self.__pixels.get(pos, None)

    def put_pixel(self, pos: tuple[int, int] | list[int, int],
                  color: tuple[int, int, int] | list[int, int, int] | str | None) -> None:
        c = color if not isinstance(color, str) else COLORS[color]
        if c is None and pos in self.__pixels:
            del self.__pixels[pos]
        elif c is not None:
            self.__pixels[pos] = (c[0], c[1], c[2])

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
        w, h = min(self.__size[0], self.__min_width), min(self.__size[1], self.__min_height)
        scr: list[list[tuple | None]] = [
            [
                None for _ in range(w+1)
            ] for __ in range(h+1)
        ]
        self.__screen = ""
        for pos, pix in self.__pixels.items():
            if 0 <= pos[0] <= w and 0 <= pos[1] <= h:
                scr[pos[1]][pos[0]] = pix

        self.__screen = "\n".join(
            [
                "".join(
                    [
                        self.join([j, scr[i+1][i2]]) for i2, j in enumerate(scr[i][:self.__min_width])
                    ]
                ) for i in range(0, min(len(scr)-1, self.__min_height-1), 2)
            ]
        )

        # for y in range(0, self.__size[1], 2):
        #     for x in range(0, self.__size[0]):
        #         if (x, y) in self.__pixels:
        #             r1, g1, b1 = self.__pixels[(x, y)] if self.__pixels[(x, y)] is not None else (None, None, None)
        #         else:
        #             r1, g1, b1 = None, None, None
        #         if (x, y+1) in self.__pixels:
        #             r2, g2, b2 = self.__pixels[(x, y+1)] if self.__pixels[(x, y+1)] is not None else (None, None, None)
        #         else:
        #             r2, g2, b2 = None, None, None
        #         if r1 is not None and r2 is not None:
        #             self.__screen += (self.__terminal.color_rgb(r1, g1, b1) +
        #                               self.__terminal.on_color_rgb(r2, g2, b2) + "▀")
        #         elif r1 is not None:
        #             self.__screen += self.__terminal.color_rgb(*self.__pixels[(x, y)]) + "▀"
        #         elif r2 is not None:
        #             self.__screen += self.__terminal.color_rgb(*self.__pixels[(x, y + 1)]) + "▄"
        #         else:
        #             self.__screen += " "
        #
        #         self.__screen += '\033[0m'
        #     self.__screen += "\n"
        # if self.__size[1] % 2 != 0:
        #     y = self.__size[1]
        #     for x in range(self.__size[0]):
        #         if (x, y) in self.__pixels:
        #             r1, g1, b1 = self.__pixels[(x, y)]
        #         else:
        #             r1, g1, b1 = None, None, None
        #         if r1 is not None:
        #             self.__screen += self.__terminal.color_rgb(*self.__pixels[(x, y)]) + "▀"
        #         else:
        #             self.__screen += " "
        #
        #         self.__screen += '\033[0m'
        #     self.__screen += "\n"
        # self.__screen += "\n" + str(self.events.get_events())

    def update(self) -> None:
        with self.__terminal.location(0, 0):
            self.__to_string()
            self.__stdout.write(self.__screen)
            self.__stdout.flush()

    @property
    def ended(self) -> bool:
        return self.__ended

    def exit(self) -> None:
        self.__stdout.write(self.__terminal.clear())
        self.__stdout.flush()
        self.__ended = True
        events.CLOSED = True
