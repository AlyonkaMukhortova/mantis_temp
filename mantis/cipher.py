import numpy as np
import galois

from mantis import constants
from mantis import math
from mantis.keys import MantisKeychain


class Mantis:
    def __init__(self, nbits: int, nblocks: int, nrounds: int) -> None:
        self._gf = galois.GF(2 ** nbits)
        self._nbits = nbits
        self._nblocks = nblocks
        self._nrounds = nrounds
        self._key_size = 2 * self._nbits * self._nblocks ** 2

    def encrypt(self, message: str, key: str, tweak: str):
        self._state = self._gf(
            math.split_int(math.str2int(message), self._nbits)
                .reshape(self._nblocks, self._nblocks))

        self._keys = MantisKeychain(math.str2int(key), self._key_size, self._nbits)

    def _round(self, secret: galois.typing.Array, round_constant: galois.typing.Array):
        self._state = self._gf(math.substitute(self._state.ravel(), constants.S_BOX).reshape((4, 4)))
        self._state ^= round_constant
        self._state ^= secret
        self._state = self._gf(math.permute(self._state.ravel(), constants.P).reshape((4, 4)))
        self._state = constants.M.dot(self._state)

    def _round_inverse(self, secret, round_constant):
        self._state = constants.M.dot(self._state)
        self._state = self._gf(math.permute(self._state.ravel(), constants.P_INVERSE).reshape((4, 4)))
        self._state ^= secret
        self._state ^= round_constant
        self._state = self._gf(math.substitute(self._state.ravel(), constants.S_BOX).reshape((4, 4)))
