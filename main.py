from mantis import utils
from mantis import constants
from mantis import cipher

def main():
    print('Run tests to make sure everything works!')
    debug = cipher.MantisDebug(4, 'matrix', True, 4)
    mantis = cipher.Mantis(4, 4, 4, debug)
    key, tweak, plaintext = '10010010111100001001100101010010110001100010010111100011111010011101011110100000011000001111011100010100110000000010100100101011',\
            '1011101010010001001011100110111100010000010101011111111011010010',\
            '0011000010001110100010100000011111110001011010001111010100010111',

    mantis.encrypt(plaintext, key, tweak)
    print(mantis._debug.get_state(-1, 'sbox'))
    print(utils.bitstring2matrix(plaintext, 4, 64, 4) ^ mantis._keys.k0)


if __name__ == '__main__':
    main()
