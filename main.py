import mantis
from bitarray import bitarray

def main():
    key = bitarray('11111111 11111111 11111111 11111111 \
                   11111111 11111111 11111111 11111111 \
                   11111111 11111111 11111111 11111111 \
                   11111111 11111111 11111111 11111111 ')
    
    m = bitarray('11110111 11111111 11111111 11111111 \
                   11111111 11111111 11111111 11111111')
    
    tweak = bitarray('11100010 11100010 11100010 11100010 \
                     11100010 11100010 11100010 11100010 ')
    

    m = bitarray('00000000 00000000 00000000 00000000 \
                 00000000 00000000 00000000 00000000 ')
    
    tweak = bitarray('00100000 00000000 00000000 00000000 \
                 00000000 00100000 00000000 00000000 ')
    
    key = m + m
    print(key)
    cipher = mantis.MantisState(key, m, tweak)

    c = cipher.encrypt(4, 4, m)


    m_1 = cipher.decrypt(4, 4, c)

    # print(m)
    print(c)
    print(m_1)
    # print(m == m_1)

main()