import argparse

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from enum import Enum
from itertools import repeat
from numba import jit, prange
from os import cpu_count
from random import random
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
    THREADPOOL = 4
    PROCESSPOOL = 5
    THREADPOOLJIT = 6
    PROCESSPOOLJIT = 7


def pi_serial(N):
    hits = 0
    for _ in range(N):
        x = random()
        y = random()
        if x * x + y * y < 1.0:
            hits += 1
    return 4.0 * hits / N


@jit(nopython=True)
def pi_jit(N):
    hits = 0
    for _ in range(N):
        x = random()
        y = random()
        if x * x + y * y < 1.0:
            hits += 1
    return 4.0 * hits / N


@jit(nopython=True, parallel=True)
def pi_parallel(N):
    hits = 0
    for _ in prange(N):
        x = random()
        y = random()
        if x * x + y * y < 1.0:
            hits += 1
    return 4.0 * hits / N


def pi_pool_inner(args):
    (N, _) = args
    hits = 0
    for _ in range(N):
        x = random()
        y = random()
        if x * x + y * y < 1.0:
            hits += 1
    return hits


@jit(nopython=True)
def pi_pool_inner_jit(args):
    (N, _) = args
    hits = 0
    for _ in range(N):
        x = random()
        y = random()
        if x * x + y * y < 1.0:
            hits += 1
    return hits


def pi_pool_inner_tramp(args):
    return pi_pool_inner_jit(args)


def pi_pool(N, Executor, inner_fn):
    n_workers = cpu_count()
    with Executor(max_workers=n_workers) as pool:
        hits = sum(
            pool.map(
                inner_fn,
                zip(repeat((N + n_workers - 1) // n_workers), range(n_workers)),
            )
        )
    return 4.0 * hits / N


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Estimate pi")
    parser.add_argument("--niters", "-n", type=int, default=int(1e8))
    parser.add_argument(
        "--mode", "-m", choices=Mode, type=lambda arg: Mode[arg], default=Mode.SERIAL
    )
    parser.add_argument("--verbose", "-v", action="store_true", default=False)
    args = parser.parse_args()

    if args.mode in [Mode.ALL, Mode.JIT]:
        with Timer("JIT: pi_jit" if args.verbose else None) as _:
            pi_jit(10)

    if args.mode in [Mode.ALL, Mode.PARALLEL]:
        with Timer("JIT: pi_parallel" if args.verbose else None) as _:
            pi_parallel(10)

    if args.mode in [Mode.ALL, Mode.THREADPOOLJIT, Mode.PROCESSPOOLJIT]:
        with Timer("JIT: pi pool inner jit" if args.verbose else None) as _:
            pi_pool_inner_jit((10, 0))

    if args.mode is Mode.ALL:
        with Timer(Mode.SERIAL) as _:
            pi = pi_serial(args.niters)
            print(f"pi ≈ {pi:.9f}")
        with Timer(Mode.JIT) as _:
            pi = pi_jit(args.niters)
            print(f"pi ≈ {pi:.9f}")
        with Timer(Mode.PARALLEL) as _:
            pi = pi_parallel(args.niters)
            print(f"pi ≈ {pi:.9f}")
        with Timer(Mode.THREADPOOL) as _:
            pi = pi_pool(args.niters, ThreadPoolExecutor, pi_pool_inner)
            print(f"pi ≈ {pi:.9f}")
        with Timer(Mode.PROCESSPOOL) as _:
            pi = pi_pool(args.niters, ProcessPoolExecutor, pi_pool_inner)
            print(f"pi ≈ {pi:.9f}")
        with Timer(Mode.THREADPOOLJIT) as _:
            pi = pi_pool(args.niters, ThreadPoolExecutor, pi_pool_inner_jit)
            print(f"pi ≈ {pi:.9f}")
        with Timer(Mode.PROCESSPOOLJIT) as _:
            pi = pi_pool(args.niters, ProcessPoolExecutor, pi_pool_inner_tramp)
            print(f"pi ≈ {pi:.9f}")
    else:
        with Timer(str(args.mode)) as timer:
            if args.mode is Mode.SERIAL:
                pi = pi_serial(args.niters)
            elif args.mode is Mode.JIT:
                pi = pi_jit(args.niters)
            elif args.mode is Mode.PARALLEL:
                pi = pi_parallel(args.niters)
            elif args.mode is Mode.THREADPOOL:
                pi = pi_pool(args.niters, ThreadPoolExecutor, pi_pool_inner)
            elif args.mode is Mode.PROCESSPOOL:
                pi = pi_pool(args.niters, ProcessPoolExecutor, pi_pool_inner)
            elif args.mode is Mode.THREADPOOLJIT:
                pi = pi_pool(args.niters, ThreadPoolExecutor, pi_pool_inner_jit)
            elif args.mode is Mode.PROCESSPOOLJIT:
                pi = pi_pool(args.niters, ProcessPoolExecutor, pi_pool_inner_tramp)
            print(f"pi ≈ {pi}")
