import numpy as np


def permute(matrix: np.ndarray, permutation: np.ndarray) -> np.ndarray:
    result = np.empty_like(matrix)
    with np.nditer(permutation) as iterator:
        for a in iterator:
            result[iterator.iterindex] = matrix[a]
    return result


def substitute(matrix: np.ndarray, lookup_table: np.ndarray) -> np.ndarray:
    result = np.empty_like(matrix)
    with np.nditer(matrix) as iterator:
        for a in iterator:
            result[iterator.iterindex] = lookup_table[a]
    return result


def rotate_left(number: int, n: int, nbits: int) -> int:
    def rotate_left_by_one(number: int, nbits: int) -> int:
        bit = number & (1 << (nbits - 1))
        number <<= 1
        if bit:
            number |= 1
        number &= (1 << nbits) - 1

        return number

    for _ in range(n):
        number = rotate_left_by_one(number, nbits)

    return number


def rotate_right(number: int, n: int, nbits: int) -> int:
    def rotate_right_by_one(number: int, nbits: int) -> int:
        bit = number & 1
        number >>= 1
        if bit:
            number |= 1 << (nbits - 1)

        return number

    for _ in range(n):
        number = rotate_right_by_one(number, nbits)

    return number


def str2int(binary_string: str) -> int:
    return int(''.join(binary_string.split()), 2)


def get_mask(mask_size: int) -> int:
    return (1 << mask_size) - 1


def split_int(number: int, mask_size: int) -> np.ndarray:
    if number.bit_length() % mask_size != 0:
        raise ValueError('Number length must be multiple of mask size.')

    nsplit = number.bit_length() // mask_size
    mask = get_mask(mask_size)
    return np.array([(number & (mask << (mask_size * i))) >> (i * mask_size) for i in range(nsplit)])[::-1]
