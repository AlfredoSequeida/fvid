# distutils: language=c++
# cython: boundscheck=False
# cython: cdivision=True
# cython: wraparound=False
# cython: c_string_type=unicode, c_string_encoding=ascii

from libcpp.string cimport string

cpdef str cy_gbfi(image):
    cdef int width, height, x, y
    cdef string bits = b''
    cdef (int, int, int) pixel

    width, height = image.size

    px = image.load()
    
    for y in range(height):
        for x in range(width):
            pixel = px[x, y]

            # if the white difference is smaller (comparison part 1), that means the pixel is closer
            # to white, otherwise, the pixel must be black
            bits.append(b'1' if abs(pixel[0] - 255) < abs(pixel[0] - 0) and abs(pixel[1] - 255) < abs(pixel[1] - 0) and abs(pixel[2] - 255) < abs(pixel[2] - 0) else b'0')

    return bits

cpdef str cy_gbfi_h265(image):
    cdef int width, height, x, y
    cdef string bits = b''

    width, height = image.size

    px = image.load()
    
    for y in range(height):
        for x in range(width):
            bits.append(b'1' if px[x, y] == 255 else b'0')

    return bits