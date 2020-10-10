# distutils: language=c++
from tqdm import tqdm

cdef bint less(int val1, int val2):
    return val1 < val2

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef str cy_get_bits_from_image(image, str DELIMITER):
    cdef int width, height, delimiter_length, x, y
    cdef bint done
    cdef str bits, delimiter_str, pixel_bin_rep
    #cdef tuple pixel
    cdef tuple white_diff, black_diff, pixel

    width, height = image.size

    done = False

    px = image.load()
    bits = ""

    delimiter_str = DELIMITER[2:]
    delimiter_length = len(delimiter_str)

    pbar = tqdm(range(height), desc="Getting bits from frame")
    
    for y in pbar:
        for x in range(width):

            # check if we have hit the delimiter
            if bits[-delimiter_length:] == delimiter_str:
                # remove delimiter from bit data to have an exact one to one
                # copy when decoding

                bits = bits[: len(bits) - delimiter_length]

                pbar.close()

                return bits

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
                if all((less(white_diff[0], black_diff[0]), less(white_diff[1], black_diff[1]), less(white_diff[2], black_diff[2]))):
                    pixel_bin_rep = "1"
                else:
                    pixel_bin_rep = "0"

            # adding bits
            bits += pixel_bin_rep

    return bits
