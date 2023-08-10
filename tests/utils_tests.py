import typing
import unittest

import numpy as np
from parameterized import parameterized

from mantis import utils


class UtilsTests(unittest.TestCase):
    @parameterized.expand([
        [0b001, 0b100, 1, 3],
        [0b100, 0b001, 2, 3],
        [0b001, 0b001, 3, 3],
    ])
    def test_rotate_left(self, expected: int, number: int, n: int, nbits: int):
        self.assertEqual(expected, utils.rotate_left(number, n, nbits))

    @parameterized.expand([
        [0b010, 0b100, 1, 3],
        [0b010, 0b001, 2, 3],
        [0b001, 0b001, 3, 3],
    ])
    def test_rotate_right(self, expected: int, number: int, n: int, nbits: int):
        self.assertEqual(expected, utils.rotate_right(number, n, nbits))

    @parameterized.expand([
        [0b1010, '1010'],
        [0b1010, ' \n1\t0  1 0   '],
        [0b1010, '  10 10\n\t\t'],
    ])
    def test_str2int(self, expected: int, string: str):
        self.assertEqual(expected, utils.str2int(string))

    @parameterized.expand([
       [np.array([1, 3, 2]), np.array([1, 2, 3]), np.array([0, 2, 1])]
    ])
    def test_permute(self, expected: np.ndarray, value: np.ndarray, permutation: np.ndarray):
        self.assertTrue(np.all(expected == utils.permute(value, permutation)))

    @parameterized.expand([
        [np.array([1, 3, 1]), np.array([0, 2, 1]), np.array([1, 1, 3])]
    ])
    def test_substitute(self, expected: np.ndarray, value: np.ndarray, lookup_table: np.ndarray):
        self.assertTrue(np.all(expected == utils.substitute(value, lookup_table)))

    @parameterized.expand([
        [0b1, 1],
        [0b11111, 5],
        [0b_1111_1111, 8],
        [0b_1001, 4, [0, 3]],
        [0b_1100_0010, 8, [1, 6, 7]]
    ])
    def test_get_mask(self, expected: int, mask_size: int, bit_indices: typing.Union[list[int], None] = None):
        self.assertEqual(expected, utils.get_mask(mask_size, bit_indices))

    @parameterized.expand([
        [np.array([1, 1, 0, 1]), 0b1101, 1, 4],
        [np.array([0b10, 0b11, 0b00, 0b01]), 0b10110001, 2, 8],
        [np.array([0b10110, 0b11001]), 0b1011011001, 5, 10],
        [np.array([0b000, 0b000, 0b000]), 0b000000000, 3, 9]
    ])
    def test_split_int(self, expected: np.ndarray, number: int, mask_size: int, number_length: int):
        self.assertTrue(np.all(expected == utils.split_int(number, mask_size, number_length)))

    @parameterized.expand([
        [np.array([1, 1, 0, 1]), '1101', 1, 4],
        [np.array([0b10, 0b11, 0b00, 0b01]), '10110001', 2, 8],
        [np.array([0b10110, 0b11001]), '1011011001', 5, 10],
        [np.array([0b000, 0b000, 0b000]), '000000000', 3, 9]
    ])
    def test_split_bitstring(self, expected: np.ndarray, bitstring: str, mask_size: int, number_length: int):
        self.assertTrue(np.all(expected == utils.split_bitstring(bitstring, mask_size, number_length)))

    @parameterized.expand([
        [np.array([[1, 1], [0, 1]]), '1101', 1, 4, 2],
        [np.array([[0b10, 0b11], [0b00, 0b01]]), '10110001', 2, 8, 2],
        [np.array([[0b000, 0b000], [0b000, 0b000]]), '000000000000', 3, 12, 2]
    ])
    def test_bitstring2matrix(self, expected: np.ndarray, bitstring: str, mask_size: int, number_length: int, side: int):
         self.assertTrue(np.all(expected == utils.bitstring2matrix(bitstring, mask_size, number_length, side)))


if __name__ == '__main__':
    unittest.main()
