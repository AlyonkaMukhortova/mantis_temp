import numpy as np
import constants
import galois
from MantisKeychain import MantisKeychain


class Mantis:
    def __init__(self, nbits: int, nblocks: int, nrounds: int):
        self._gf = galois.GF(2 ** nbits)
        self._nblocks = nblocks
        self._nrounds = nrounds


    def encrypt(self, message:str, tweak, key):
        message = message.join(message.split())
        self._keychain = MantisKeychain(key)
        self._state = ''


    def _round(self, secret, round_constant):
        self._state = self._gf(self._substitute(self._state.ravel(), constants.S_BOX).reshape((4, 4)))
        self._state ^= round_constant
        self._state ^= secret
        self._state = self._gf(self._permute(self._state.ravel(), constants.P).reshape((4, 4)))
        self._state = constants.M.dot(self._state)


    def _round_inverse(self, secret, round_constant):
        self._state = constants.M.dot(self._state)
        self._state = self._gf(self._permute(self._state.ravel(), constants.P_INVERSE).reshape((4, 4)))
        self._state ^= secret
        self._state ^= round_constant
        self._state = self._gf(self._substitute(self._state.ravel(), constants.S_BOX).reshape((4, 4)))



    def _permute(matrix: np.ndarray, permutation: np.ndarray):
        result = np.empty_like(matrix)
        with np.nditer(permutation) as iterator:
            for a in iterator:
                result[iterator.iterindex] = matrix[a]
        return result


    def _substitute(matrix: np.ndarray, lookup_table: np.ndarray):
        result = np.empty_like(matrix)
        for i in range(lookup_table.size):
            result[i] = lookup_table[matrix[i]]
        return result
