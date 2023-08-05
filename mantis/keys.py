from mantis import utils


class MantisKeychain:
    def __init__(self, key: int, key_size: int, nbits: int, nblocks: int) -> None:
        if key_size % 2 != 0:
            raise ValueError('Key size cannot be odd.')

        half_key_size = (key_size // 2)

        k0 = key >> half_key_size
        k0p = utils.rotate_right(k0, 1, half_key_size) ^ (k0 >> 63)
        k1 = (key & (utils.get_mask(half_key_size)))

        self.k0 = utils.int2matrix(k0, nbits, half_key_size, nblocks)
        self.k1 = utils.int2matrix(k1, nbits, half_key_size, nblocks)
        self.k0p = utils.int2matrix(k0p, nbits, half_key_size, nblocks)
