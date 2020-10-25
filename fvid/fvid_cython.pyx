# distutils: language=c
# cython: boundscheck=False
# cython: cdivision=True
# cython: wraparound=False

cpdef cy_get_bits_from_image(image):
    cdef int width, height, x, y
    cdef str pixel_bin_rep
    cdef (int, int, int) pixel#, white_diff, black_diff

    width, height = image.size

    px = image.load()
    bits = ""
    
    for y in range(height):
        for x in range(width):
            pixel = px[x, y]

            pixel_bin_rep = <str>"0"

            # for exact matches, indexing each pixel individually is faster in cython for some reason
            if pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255:
                pixel_bin_rep = <str>"1"
            elif pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                pixel_bin_rep = <str>"0"
            else:
                # if the white difference is smaller (comparison part 1), that means the pixel is closer
                # to white, otherwise, the pixel must be black
                if abs(pixel[0] - 255) < abs(pixel[0] - 0) and abs(pixel[1] - 255) < abs(pixel[1] - 0) and abs(pixel[2] - 255) < abs(pixel[2] - 0):
                    pixel_bin_rep = <str>"1"
                else:
                    pixel_bin_rep = <str>"0"

            # adding bits
            bits += pixel_bin_rep

    return bits
