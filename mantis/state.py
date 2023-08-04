import numpy as np

from mantis import constants
from mantis.keys import MantisKeychain, MantisTweakChain


class MantisState:
    def __init__(self, initial_state: np.ndarray, key: np.ndarray, tweak: np.ndarray):
        self._state = initial_state
        self._keychain = MantisKeychain(key)
        self._tweak_chain = MantisTweakChain(tweak)

    def sub_cells(self):
        pass

    def permute_cells(self):
        pass

    def add_constant(self, index: int):
        pass

    def add_tweakey(self, tweak, key):
        pass

    def mix_columns(self):
        pass


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

class RoundConstantIteratorDefault:
    __slots__ = ('_round_constants', '_amount', '_counter')

    def __init__(self, amount: int) -> None:
        self._counter = 0
        self._amount = amount
        self._round_constants = [
            np.array([
                [0x1, 0x3, 0x1, 0x9],
                [0x8, 0xa, 0x2, 0xe],
                [0x0, 0x3, 0x7, 0x0],
                [0x7, 0x3, 0x4, 0x4]]),
            np.array([
                [0xa, 0x4, 0x0, 0x9],
                [0x3, 0x8, 0x2, 0x2],
                [0x2, 0x9, 0x9, 0xf],
                [0x3, 0x1, 0xd, 0x0]]),
            np.array([
                [0x0, 0x8, 0x2, 0xe],
                [0xf, 0xa, 0x9, 0x8],
                [0xe, 0xc, 0x4, 0xe],
                [0x6, 0xc, 0x8, 0x9]]),
            np.array([
                [0x4, 0x5, 0x2, 0x8],
                [0x2, 0x1, 0xe, 0x6],
                [0x3, 0x8, 0xd, 0x0],
                [0x1, 0x3, 0x7, 0x7]]),

            np.array([
                [0xb, 0xe, 0x5, 0x4],
                [0x6, 0x6, 0xc, 0xf],
                [0x3, 0x4, 0xe, 0x9],
                [0x0, 0xc, 0x6, 0xc]]),
            np.array([
                [0xc, 0x0, 0xa, 0xc],
                [0x2, 0x9, 0xb, 0x7],
                [0xc, 0x9, 0x7, 0xc],
                [0x5, 0x0, 0xd, 0xd]]),
            np.array([
                [0x3, 0xf, 0x8, 0x4],
                [0xd, 0x5, 0xb, 0x5],
                [0xb, 0x5, 0x4, 0x7],
                [0x0, 0x9, 0x1, 0x7]]),
            np.array([
                [0x9, 0x2, 0x1, 0x6],
                [0xd, 0x5, 0xd, 0x9],
                [0x8, 0x9, 0x7, 0x9],
                [0xf, 0xb, 0x1, 0xb]]),
        ]

        if self._amount > len(self._round_constants):
            raise ValueError(f'Amount cannot be greater than {len(self._round_constants)}.')

    def __iter__(self):
        return self

    def __next__(self):
        if self._counter == self._amount:
            raise StopIteration

        self._counter += 1
        return self._round_constants[self._counter - 1]
