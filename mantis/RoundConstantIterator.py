import numpy as np


class RoundConstantIterator:
    __slots__ = ('_seed', '_generator', '_amount', '_size', '_counter', '_nbits')

    def __init__(self, seed: int, amount: int, size: int, nbits: int):
        self._nbits = nbits
        self._counter = 0
        self._seed = seed
        self._amount = amount
        self._size = size
        self._generator = np.random.default_rng(seed)

    def __iter__(self):
        return self

    def __next__(self):
        if self._counter == self._amount:
            raise StopIteration

        self._counter += 1
        return self._generator.integers(0, 2**self._nbits, (self._size, self._size), dtype=int)

    def restart(self):
        self._counter = 0
        self._generator = np.random.default_rng(self._seed)
