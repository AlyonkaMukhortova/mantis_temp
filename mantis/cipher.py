import galois

from mantis import constants
from mantis import utils
from mantis.keys import MantisKeychain


class Mantis:
    def __init__(self, nbits: int, nblocks: int, nrounds: int) -> None:
        self._gf = galois.GF(2 ** nbits)
        self._nbits = nbits
        self._nblocks = nblocks
        self._nrounds = nrounds
        self._key_size = 2 * self._nbits * self._nblocks ** 2

    def encrypt(self, message: str, key: str, tweak: str):
        self._state = self._gf(utils.bitstring2matrix(message, self._nbits, self._nbits * self._nblocks ** 2, self._nblocks))
        self._tweak = self._gf(utils.bitstring2matrix(tweak, self._nbits, self._nbits * self._nblocks ** 2, self._nblocks))
        self._keys = MantisKeychain(utils.str2int(key), self._key_size, self._nbits, self._nblocks)
        
        self._encrypt()

        return ''.join([f'{i:04b}' for i in self._state.ravel()])

    def decrypt(self, message: str, key: str, tweak: str):
        self._state = self._gf(utils.bitstring2matrix(message, self._nbits, self._nbits * self._nblocks ** 2, self._nblocks))
        self._tweak = self._gf(utils.bitstring2matrix(tweak, self._nbits, self._nbits * self._nblocks ** 2, self._nblocks))
        self._keys = MantisKeychain(utils.str2int(key), self._key_size, self._nbits, self._nblocks)

        self._keys.k0, self._keys.k0p = self._keys.k0p, self._keys.k0
        self._keys.k1 ^= self._gf(constants.ALPHA)
        
        self._encrypt()

        return ''.join([f'{i:04b}' for i in self._state.ravel()])

    def _encrypt(self):
        self._state ^= self._gf(self._keys.k0)
        self._state ^= self._gf(self._keys.k1)
        self._state ^= self._gf(self._tweak)

        for i in range(self._nrounds):
            self._tweak = utils.permute(self._tweak.ravel(), constants.H).reshape(4, 4)
            self._round(self._gf(self._keys.k1) ^ self._tweak, self._gf(constants.ROUND_CONSTANTS[i]))
            

        self._state = self._gf(utils.substitute(self._state.ravel(), self._gf(constants.S_BOX)).reshape((4, 4)))
        self._state = self._gf(constants.M).dot(self._state)
        self._state = self._gf(utils.substitute(self._state.ravel(), self._gf(constants.S_BOX)).reshape((4, 4)))

        for i in range(self._nrounds):
            self._round_inverse(self._gf(self._keys.k1) ^ self._gf(constants.ALPHA) ^ self._tweak,
                                self._gf(constants.ROUND_CONSTANTS)[self._nrounds - i - 1])
            self._tweak = utils.permute(self._tweak.ravel(), constants.H_INVERSE).reshape(4, 4)

        self._state ^= self._gf(self._tweak)
        self._state ^= self._gf(self._keys.k1)
        self._state ^= self._gf(constants.ALPHA)
        self._state ^= self._gf(self._keys.k0p)

    def _round(self, tweakey, round_constant):
        self._state = self._gf(utils.substitute(self._gf(self._state.ravel()), constants.S_BOX).reshape((4, 4)))
        self._state ^= round_constant
        self._state ^= tweakey
        self._state = self._gf(utils.permute(self._state.ravel(), constants.P).reshape((4, 4)))
        self._state = self._gf(constants.M).dot(self._state)

    def _round_inverse(self, tweakey, round_constant):
        self._state = self._gf(constants.M).dot(self._state)
        self._state = self._gf(utils.permute(self._state.ravel(), constants.P_INVERSE).reshape((4, 4)))
        self._state ^= tweakey
        self._state ^= round_constant
        self._state = self._gf(utils.substitute(self._state.ravel(), constants.S_BOX).reshape((4, 4)))
