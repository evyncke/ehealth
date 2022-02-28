#!env python3.8

def hexDump(s, backgroundColor = None, offset = None, length = None):
    i = 0
    while i < len(s):
        j = 0
        while i + j < len(s) and j < 16:
            if backgroundColor and offset <= i+j and i+j < offset+length:
                print('<span style="background-color: {};">'.format(backgroundColor), end = '')
            if isinstance(s[i+j], str):
                print('{:02X} '.format(ord(s[i+j])), end = '')
            else:
                print('{:02X} '.format(s[i+j]), end = '')
            if backgroundColor and offset <= i+j and i+j < offset+length:
                print('</span>', end = '')
            j += 1
        while j < 16:
            print("   ", end = '')
            j += 1
        print("   ", end = '')
        j = 0
        while i < len(s) and j < 16:
            if isinstance(s[i], str):
                c = ord(s[i])
            else:
                c = s[i]
            if backgroundColor and offset <= i and i < offset+length:
                print('<span style="background-color: {};">'.format(backgroundColor), end = '')
            if (32 <= c and c <= 127):
                print(chr(c) + ' ', end='')
            else:
                print('. ', end = '')
            if backgroundColor and offset <= i and i < offset+length:
                print('</span>', end = '')
            i += 1
            j += 1
        print()

def hexDump1Line(s):
    i = 0
    result = "0x"
    while i < len(s):
        result += '{:02X}'.format(s[i])
        i += 1
    return result

def numericModeDecode(s):
    i = 0
    result = bytearray()
    while i+1 < len(s):
        c = int(s[i]) * 10 + int(s[i+1]) + ord('-')
        result.append(c)
        i += 2
    return result
