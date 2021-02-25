# distutils: language=c
# cython: boundscheck=False
# cython: cdivision=True
# cython: wraparound=False

cpdef str cy_gbfi(image):
    cdef int width, height, x, y
    cdef str pixel_bin_rep, bits
    cdef (int, int, int) pixel

    width, height = image.size

    px = image.load()
    bits = ""
    
    for y in range(height):
        for x in range(width):
            pixel = px[x, y]

            pixel_bin_rep = <str>"0"

            # if the white difference is smaller (comparison part 1), that means the pixel is closer
            # to white, otherwise, the pixel must be black
            if abs(pixel[0] - 255) < abs(pixel[0] - 0) and abs(pixel[1] - 255) < abs(pixel[1] - 0) and abs(pixel[2] - 255) < abs(pixel[2] - 0):
                pixel_bin_rep = <str>"1"

            # adding bits
            bits += pixel_bin_rep

    return bits

cpdef str cy_gbfi_h265(image):
    cdef int width, height, x, y
    cdef str bits

    width, height = image.size

    px = image.load()
    bits = ""
    
    for y in range(height):
        for x in range(width):
            bits += "1" if px[x, y] == 255 else "0"

    return bits