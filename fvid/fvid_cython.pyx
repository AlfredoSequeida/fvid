# distutils: language=c++
from operator import sub
from tqdm import tqdm

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef cy_get_bits_from_image(image):
    cdef int width, height, x, y
    cdef str pixel_bin_rep
    cdef tuple white_diff, black_diff, pixel

    width, height = image.size

    px = image.load()
    bits = ""

    pbar = tqdm(range(height), desc="Getting bits from frame")
    
    for y in pbar:
        for x in range(width):
            pixel = px[x, y]

            pixel_bin_rep = "0"

            # for exact matches
            if pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255:
                pixel_bin_rep = "1"
            elif pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                pixel_bin_rep = "0"
            else:
                white_diff = (abs(pixel[0] - 255), abs(pixel[1] - 255), abs(pixel[2] - 255))
                # min_diff = white_diff
                black_diff = (abs(pixel[0] - 0), abs(pixel[1] - 0), abs(pixel[2] - 0))

                # if the white difference is smaller, that means the pixel is closer
                # to white, otherwise, the pixel must be black
                if all((white_diff[0] < black_diff[0], white_diff[1] < black_diff[1], white_diff[2] < black_diff[2])):
                    pixel_bin_rep = "1"
                else:
                    pixel_bin_rep = "0"

            # adding bits
            bits += pixel_bin_rep

    return bits
