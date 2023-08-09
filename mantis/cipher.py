import galois
from mantis import constants
from mantis import utils
from mantis.keys import MantisKeychain
import numpy as np


class MantisDebug:
    actions = ['sbox', '+const', '+tweakey', 'permute', 'matrix']
# self._state[row, col, state_index]
# self._state[:, :, i]

    def __init__(self, nrounds: int, action: str, save_all_flag: bool, nblocks: int) -> None:
        self._states = np.empty((nblocks, nblocks, 0), dtype=int)
        # self._final_action = self.actions.index(action)
        # self._final_round = nrounds
        self._save = save_all_flag

    def set_nrounds(self, nrounds: int) -> None:
        self._nrounds = nrounds

    def add_state(self, state: np.array) -> None:
        if not self._save and self._states.shape[2] == 1:
            self._states[:, :, 0] = state
            return
        self._states = np.dstack((self._states, state))

    def get_state(self, round: int, action: str):
        # round = nrounds + 2 + back_rounds
        if not self._save:
            return self._states[:, :, 0]
        if round > self._nrounds - 1:
            if round > self._nrounds + 1:
                if round >= 2 * self._nrounds + 2:
                    state_index = 2 + (round - 2) * 5 + 3 + (0 if action == '+tweakey' else 1)
                    print('last')
                else:
                    state_index = 2 + (round - 2) * 5 + self.actions.index(action) + 3
                    print("back rounds")
            else:
                print('mid rounds')
                state_index = 2 + (self._nrounds) * 5 + 2 * (round - self._nrounds) + (0 if action == 'sbox' else 1)
        elif round >= 0:
            state_index = 2 + round * 5 + self.actions.index(action)
        else:
            print('first')
            state_index = 1 if action == '+tweakey' else 0
        return self._states[:, :, state_index]
        # return state_index

class Mantis:
    def __init__(self, nbits: int, nblocks: int, nrounds: int, debug: MantisDebug=None) -> None:
        self._debug = debug
        if debug:
            self._debug.set_nrounds(nrounds)

        self._gf = galois.GF(2 ** nbits)
        self._nbits = nbits
        self._nblocks = nblocks
        self._nrounds = nrounds
        self._key_size = 2 * self._nbits * self._nblocks ** 2
        self._M = constants.get_m(nblocks)
        self._S = constants.get_s(nbits)
        self._P = constants.get_p(nblocks)
        self._P_INVERSE = constants.invert_permutation(self._P)
        self._H = constants.get_h(nblocks)
        self._H_INVERSE = constants.invert_permutation(self._H)
        

    def encrypt(self, message: str, key: str, tweak: str):
        self._prepare(message, key, tweak)

        self._encrypt()

        return self._state2bitstring()

    def decrypt(self, message: str, key: str, tweak: str):
        self._prepare(message, key, tweak)

        self._keys.k0, self._keys.k0p = self._keys.k0p, self._keys.k0
        self._keys.k1 ^= self._gf(constants.ALPHA)
        
        self._encrypt()

        return self._state2bitstring()

    def _encrypt(self):
        self._state ^= self._gf(self._keys.k0)
        self._add_state()
        self._state ^= self._gf(self._keys.k1)
        self._state ^= self._gf(self._tweak)
        self._add_state()

        for i in range(self._nrounds):
            self._tweak = utils.permute(self._tweak.ravel(), self._H).reshape((self._nblocks, self._nblocks))
            self._round(self._gf(self._keys.k1) ^ self._tweak, self._gf(constants.ROUND_CONSTANTS[i]))

        self._state = self._gf(utils.substitute(self._state.ravel(), self._gf(self._S)).reshape((self._nblocks, self._nblocks)))
        self._add_state()
        self._state = self._gf(self._M).dot(self._state)
        self._add_state()
        self._state = self._gf(utils.substitute(self._state.ravel(), self._gf(self._S)).reshape((self._nblocks, self._nblocks)))
        self._add_state()

        for i in range(self._nrounds):
            self._round_inverse(self._gf(self._keys.k1) ^ self._gf(constants.ALPHA) ^ self._tweak,
                                self._gf(constants.ROUND_CONSTANTS)[self._nrounds - i - 1])
            self._tweak = utils.permute(self._tweak.ravel(), self._H_INVERSE).reshape((self._nblocks, self._nblocks))

        self._state ^= self._gf(self._tweak)
        self._state ^= self._gf(self._keys.k1)
        self._state ^= self._gf(constants.ALPHA)
        self._add_state()
        self._state ^= self._gf(self._keys.k0p)
        self._add_state()

    def _round(self, tweakey, round_constant):
        self._state = self._gf(utils.substitute(self._state.ravel(), self._S).reshape((self._nblocks, self._nblocks)))
        self._add_state()
        self._state ^= round_constant
        self._add_state()
        self._state ^= tweakey
        self._add_state()
        self._state = self._gf(utils.permute(self._state.ravel(), self._P).reshape((self._nblocks, self._nblocks)))
        self._add_state()
        self._state = self._gf(self._M).dot(self._state)
        self._add_state()

    def _round_inverse(self, tweakey, round_constant):
        self._state = self._gf(self._M).dot(self._state)
        self._add_state()
        self._state = self._gf(utils.permute(self._state.ravel(), self._P_INVERSE).reshape((self._nblocks, self._nblocks)))
        self._add_state()
        self._state ^= tweakey
        self._add_state()
        self._state ^= round_constant
        self._add_state()
        self._state = self._gf(utils.substitute(self._state.ravel(), self._S).reshape((self._nblocks, self._nblocks)))
        self._add_state()

    def _prepare(self, plaintext: str, key: str, tweak: str):
        self._state = self._bitstring2matrix(plaintext)
        self._tweak = self._bitstring2matrix(tweak)
        self._keys = MantisKeychain(utils.str2int(key), self._key_size, self._nbits, self._nblocks)

    def _bitstring2matrix(self, bitstring: str):
        return self._gf(utils.bitstring2matrix(bitstring, self._nbits, self._nbits * self._nblocks ** 2, self._nblocks))

    def _state2bitstring(self):
        # to do: 0{nbits}b
        return ''.join([f'{i:04b}' for i in self._state.ravel()])
    
    def _add_state(self):
        if self._debug:
            self._debug.add_state(self._state)
