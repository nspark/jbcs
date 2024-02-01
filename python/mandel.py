import argparse
import colorsys
import numpy as np

from enum import Enum
from math import log
from numba import jit, prange
from time import perf_counter


class Timer:
    def __init__(self, label=str):
        self.label = label

    def __enter__(self):
        self.elapsed = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.elapsed = perf_counter() - self.elapsed
        if self.label is not None:
            print(f"Elapsed: {self.elapsed:7.3f} seconds [{self.label}]")
        return self


class Mode(Enum):
    ALL = 0
    SERIAL = 1
    JIT = 2
    PARALLEL = 3


def mandel_serial(data, x0, x1, y0, y1):
    it = np.nditer(data, flags=["multi_index"])
    for _ in it:
        (y, x) = it.multi_index
        px = ((x1 - x0) / (width - 1)) * x + x0
        py = ((y1 - y0) / (height - 1)) * y + y0
        (x, y) = (0, 0)
        count = 0
        for i in range(max_iters):
            (x, y) = (x * x - y * y + px, 2 * x * y + py)
            count += 1
            if x * x + y * y >= 2 * 2:
                break
        data[it.multi_index] = log(count)


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(
        description="Generate an image of the Mandelbrot set"
    )
    parser.add_argument("OUTFILE", type=str, default="mandel.ppm")
    parser.add_argument("--resolution", "-r", type=int, default=250)
    parser.add_argument(
        "--box",
        "-b",
        nargs=4,
        metavar=("x0", "y0", "x1", "y1"),
        type=float,
        default=[-2.5, -1.5, 1.5, 1.5],
    )
    parser.add_argument("--max-iters", "-i", type=int, default=1000)
    parser.add_argument(
        "--mode", "-m", choices=Mode, type=lambda arg: Mode[arg], default=Mode.SERIAL
    )
    parser.add_argument("--verbose", "-v", action="store_true", default=False)
    args = parser.parse_args()

    # Parameters
    image_name = args.OUTFILE
    x0 = args.box[0]
    y0 = args.box[1]
    x1 = args.box[2]
    y1 = args.box[3]
    height = int((y1 - y0) * args.resolution)
    width = int((x1 - x0) * args.resolution)
    max_iters = args.max_iters

    # Allocate data
    data = np.zeros((height, width))

    # Invoke the JIT
    with Timer("JIT" if args.verbose else None) as _:
        pass

    # Generate Mandelbot image
    if args.mode is Mode.ALL:
        with Timer(Mode.SERIAL) as _:
            mandel_serial(data, x0, x1, y0, y1)
        with Timer(Mode.JIT) as _:
            pass
        with Timer(Mode.PARALLEL) as _:
            pass
    else:
        with Timer(str(args.mode)) as timer:
            if args.mode is Mode.SERIAL:
                mandel_serial(data, x0, x1, y0, y1)
            elif args.mode is Mode.JIT:
                pass
            elif args.mode is Mode.PARALLEL:
                pass

    # Output
    with Timer("I/O" if args.verbose else None) as _:
        with open(image_name, "wb") as f:
            f.write(bytes(f"P6\n{width} {height}\n255\n", encoding="utf-8"))
            for value in np.nditer(data):
                (r, g, b) = colorsys.hsv_to_rgb(value / log(max_iters + 1), 1.0, 1.0)
                r = int(r * 255)
                g = int(g * 255)
                b = int(b * 255)
                f.write(bytes((r, g, b)))
