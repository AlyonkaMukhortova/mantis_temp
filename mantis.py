import numpy as np
from bitarray import bitarray, util
import galois
from scipy.linalg import circulant

class MantisState:


    def __init__(self, key: bitarray, message: bitarray, tweak: bitarray):
        self._nblocks: int = 4
        self._nbits: int = 4
        self._GF = galois.GF(2 ** self._nbits)
        self._M = self._GF(np.array(circulant([0] + [1] * (self._nblocks - 1))))
        keysize = len(key)
        self._k0 = key[:keysize//2]
        self._k1 = self._arr_to_matrix(key[keysize//2:])
        self._k0p = self._arr_to_matrix(self._rotate_right(self._k0, 1) ^ (self._k0 >> 63))
        self._k0 = self._arr_to_matrix(self._k0)
        self._sbox: list = [0xc, 0xa, 0xd, 0x3, 
                      0xe, 0xb, 0xf, 0x7, 
                      0x8, 0x9, 0x1, 0x5, 
                      0x0, 0x2, 0x4, 0x6]
        self._permutation: list = [ 0, 11,  6, 13, 
                                    10,  1, 12,  7, 
                                     5, 14,  3,  8, 
                                    15,  4,  9,  2]
        self._inv_permutation = [self._permutation.index(i) for i in range (self._nblocks ** 2)]
        self._is = self._GF(np.array([util.ba2int(message[self._nbits * i : self._nbits * i + self._nbits], signed=False) 
                                      for i in range(len(message)//self._nbits)]).reshape((self._nblocks, self._nblocks)))
        self._tweak = self._arr_to_matrix(tweak)
        self._tweak_permutation = [6, 5, 14, 15, 0, 1, 2, 3, 7, 12, 13, 4, 8, 9, 10, 11]
        self._inv_tweak_permutation = [self._tweak_permutation.index(i) for i in range (self._nblocks ** 2)]
        self._round_constants = [self._GF(np.array([[0x1, 0x3, 0x1, 0x9],
                                                    [0x8, 0xa, 0x2, 0xe],
                                                    [0x0, 0x3, 0x7, 0x0],
                                                    [0x7, 0x3, 0x4, 0x4]])),

                                self._GF(np.array( [[0xa, 0x4, 0x0, 0x9],
                                                    [0x3, 0x8, 0x2, 0x2],
                                                    [0x2, 0x9, 0x9, 0xf],
                                                    [0x3, 0x1, 0xd, 0x0]])),

                                self._GF(np.array([[0x0, 0x8, 0x2, 0xe],
                                                    [0xf, 0xa, 0x9, 0x8],
                                                    [0xe, 0xc, 0x4, 0xe],
                                                    [0x6, 0xc, 0x8, 0x9]])),

                                self._GF(np.array([[0x4, 0x5, 0x2, 0x8],
                                                    [0x2, 0x1, 0xe, 0x6],
                                                    [0x3, 0x8, 0xd, 0x0],
                                                    [0x1, 0x3, 0x7, 0x7]])),

                                self._GF(np.array([[0xb, 0xe, 0x5, 0x4],
                                                    [0x6, 0x6, 0xc, 0xf],
                                                    [0x3, 0x4, 0xe, 0x9],
                                                    [0x0, 0xc, 0x6, 0xc]])),

                                self._GF(np.array([[0xc, 0x0, 0xa, 0xc],
                                                    [0x2, 0x9, 0xb, 0x7],
                                                    [0xc, 0x9, 0x7, 0xc],
                                                    [0x5, 0x0, 0xd, 0xd]])),

                                self._GF(np.array([[0x3, 0xf, 0x8, 0x4],
                                                    [0xd, 0x5, 0xb, 0x5],
                                                    [0xb, 0x5, 0x4, 0x7],
                                                    [0x0, 0x9, 0x1, 0x7]])),

                                self._GF(np.array([[0x9, 0x2, 0x1, 0x6],
                                                    [0xd, 0x5, 0xd, 0x9],
                                                    [0x8, 0x9, 0x7, 0x9],
                                                    [0xf, 0xb, 0x1, 0xb]]))]

        self._alfa = self._GF(np.array([[0x2, 0x4, 0x3, 0xf],
                                        [0x6, 0xa, 0x8, 0x8],
                                        [0x8, 0x5, 0xa, 0x3],
                                        [0x0, 0x8, 0xd, 0x3]]))

    def _set_key(self, key):
        pass


    def encrypt(self, num_r, num_inv_r, input_state):
        temp_tweak = self._tweak.copy()
        if type(input_state) is bitarray:
            input_state = self._arr_to_matrix(input_state)
        input_state = self._add_whitening_key_first(input_state)
        input_state = self._add_tweakey(input_state)

        for i in range(num_r):
            input_state = self.r_i(input_state, i)
            print(input_state)
        
        input_state = self.mid_rounds(input_state)
        
        for i in range(num_inv_r):
            input_state = self.r_i_inv(input_state, num_inv_r - i - 1)
            print(i + num_r)
        
        input_state = self._add_tweakey(input_state, inverse=True)
        input_state = self._add_alpha(input_state)

        self._tweak = temp_tweak
        return self._add_whitening_key_last(input_state)
    
    def decrypt(self, num_r, num_inv_r, input_state):
        self._k0, self._k0p = self._k0p, self._k0
        self._k1 ^= self._alfa

        input_state = self.encrypt(num_inv_r, num_r, input_state)

        self._k0, self._k0p = self._k0p, self._k0
        self._k1 ^= self._alfa

        return input_state


    def r_i(self, input_state, i):
        return self._mix_columns(self._permute_cells(self._add_tweakey(self._add_constant(
            self._sub_cells(input_state), i)), self._permutation))
    

    def r_i_inv(self, input_state, i):
        return self._sub_cells(self._add_constant(self._add_alpha(self._add_tweakey(self._permute_cells(
            self._mix_columns(input_state), self._inv_permutation), inverse=True)), i))
    
    
    def mid_rounds(self, input_state):
        return self._sub_cells(self._mix_columns(self._sub_cells(input_state)))
    

    def _arr_to_matrix(self, message : bitarray):
        return self._GF(np.array([util.ba2int(message[self._nbits * i : self._nbits * i + self._nbits], signed=False)\
                                   for i in range(len(message)//self._nbits)]).reshape((self._nblocks, self._nblocks)))
    

    def _mix_columns(self, state):
        return self._GF(self._M.dot(state))


    def _permute_cells(self, state, permutation):
        return self._GF(np.array([state[permutation[i] // self._nbits][permutation[i] % self._nbits] 
                                  for i in range(self._nblocks ** 2)])).reshape(self._nblocks, self._nblocks)


    def _add_whitening_key_first(self, state):
        return state ^ self._k0
    
    
    def _add_whitening_key_last(self, state):
        return state ^ self._k0p


    def _add_tweakey(self, state, inverse=False):
        state = state ^ self._k1 ^ self._tweak
        self._tweak = self._permute_cells(self._tweak, self._tweak_permutation if not inverse else self._inv_tweak_permutation)
        return state


    def _add_alpha(self, state):
        return state ^ self._alfa


    def _add_constant(self, state, i): 
        return state ^ self._round_constants[i]


    def _sub_cells(self, state):
        return self._GF(np.array([int(self._sbox[x]) for x in np.nditer(state)])).reshape(self._nblocks, self._nblocks)


    def _rotate_left(self, x, n):
        return (x << n)[:-n] + x[:n]


    def _rotate_right(self, x, n):
        return x[-n:] + (x >> n)[n:]