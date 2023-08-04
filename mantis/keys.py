import numpy as np

from mantis import math


class MantisKeychain:
    def __init__(self, key: int, key_size: int, nbits: int) -> None:
        if key_size % 2 != 0:
            raise ValueError('Key size cannot be odd.')

        half_key_size = (key_size // 2)

        k0 = key >> half_key_size
        k0p = math.rotate_right(k0, 1, half_key_size) ^ (k0 >> 63)
        k1 = key & (math.get_mask(half_key_size) << (half_key_size - 1))

        self.k0 = math.split_int(k0, nbits)
        self.k1 = math.split_int(k1, nbits)
        self.k0p = math.split_int(k0p, nbits)


class MantisTweakChain:
    def __init__(self, tweak: np.ndarray) -> None:
        pass
