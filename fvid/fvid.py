from bitstring import Bits, BitArray
from magic import Magic
import mimetypes
from PIL import Image
import glob

from operator import sub
import numpy as np
from tqdm import tqdm
import ffmpeg

import binascii

import argparse

DELIMITER = bin(int.from_bytes("HELLO MY NAME IS ALFREDO".encode(), "big"))
FRAMES_DIR = "./fvid_frames/"


def get_bits_from_file(filepath):
    bitarray = BitArray(filename=filepath)

    # adding a delimiter to know when the file ends to avoid corrupted files
    # when retrieving
    bitarray.append(DELIMITER)

    return bitarray.bin

def less(val1, val2):
    return val1 < val2

def get_bits_from_image(image):
    width, height = image.size

    done = False

    px = image.load()
    bits = ""

    delimiter_str = DELIMITER.replace("0b", "")
    delimiter_length = len(delimiter_str)

    pbar = tqdm(range(height), desc="Getting bits from frame")

    white = (255, 255, 255)
    black = (0, 0, 0)
    
    for y in pbar:
        for x in range(width):

            # check if we have hit the delimiter
            if bits[-delimiter_length:] == delimiter_str:
                # remove delimiter from bit data to have an exact one to one
                # copy when decoding

                bits = bits[: len(bits) - delimiter_length]

                pbar.close()

                return (bits, True)

            pixel = px[x, y]

            pixel_bin_rep = "0"

            # for exact matches
            if pixel == white:
                pixel_bin_rep = "1"
            elif pixel == black:
                pixel_bin_rep = "0"
            else:
                white_diff = tuple(map(abs, map(sub, white, pixel)))
                # min_diff = white_diff
                black_diff = tuple(map(abs, map(sub, black, pixel)))


                # if the white difference is smaller, that means the pixel is closer
                # to white, otherwise, the pixel must be black
                if all(map(less, white_diff, black_diff)):
                    pixel_bin_rep = "1"
                else:
                    pixel_bin_rep = "0"

            # adding bits
            bits += pixel_bin_rep

    return (bits, done)


def get_bits_from_video(video_filepath):
    # get image sequence from video
    image_sequence = []

    ffmpeg.input(video_filepath).output(
        f"{FRAMES_DIR}decoded_frames%03d.png"
    ).run(quiet=True)

    for filename in glob.glob(f"{FRAMES_DIR}decoded_frames*.png"):
        image_sequence.append(Image.open(filename))

    bits = ""
    sequence_length = len(image_sequence)

    for index in range(sequence_length):
        b, done = get_bits_from_image(image_sequence[index])

        bits += b

        if done:
            break

    return bits


def save_bits_to_file(file_path, bits):
    # get file extension

    bitstring = Bits(bin=bits)

    mime = Magic(mime=True)
    mime_type = mime.from_buffer(bitstring.tobytes())

    # If filepath not passed in use defualt
    #    otherwise used passed in filepath
    if file_path == None:
        filepath = f"file{mimetypes.guess_extension(type=mime_type)}"
    else:
        filepath = file_path

    with open(
        filepath, "wb"
    ) as f:
        bitstring.tofile(f)


def make_image(bit_set, resolution=(1920, 1080)):

    width, height = resolution

    image = Image.new("1", (width, height))
    image.putdata(bit_set)

    return image


def split_list_by_n(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def make_image_sequence(bitstring, resolution=(1920, 1080)):
    width, height = resolution

    # split bits into sets of width*height to make (1) image
    set_size = width * height

    # bit_sequence = []
    bit_sequence = split_list_by_n(list(map(int, bitstring)), width * height)
    image_bits = []

    # using bit_sequence to make image sequence

    image_sequence = []

    for bit_set in bit_sequence:
        image_sequence.append(make_image(bit_set))

    return image_sequence


def make_video(output_filepath, image_sequence, framerate="1/5"):

    if output_filepath == None:
        outputfile = "file.mp4"
    else:
        outputfile = output_filepath


    frames = glob.glob(f"{FRAMES_DIR}encoded_frames*.png")

    # for one frame
    if len(frames) == 1:
        ffmpeg.input(frames[0], loop=1, t=1).output(
            outputfile, vcodec="libx264rgb"
        ).run(quiet=True)

    else:
        ffmpeg.input(
            f"{FRAMES_DIR}encoded_frames*.png",
            pattern_type="glob",
            framerate=framerate,
        ).output(outputfile, vcodec="libx264rgb").run(quiet=True)



def cleanup():
    # remove frames
    import shutil

    shutil.rmtree(FRAMES_DIR)


def setup():
    import os

    if not os.path.exists(FRAMES_DIR):
        os.makedirs(FRAMES_DIR)


def main():
    parser = argparse.ArgumentParser(description="save files as videos")
    parser.add_argument(
        "-e", "--encode", help="encode file as video", action="store_true"
    )
    parser.add_argument(
        "-d", "--decode", help="decode file from video", action="store_true"
    )

    parser.add_argument("-i", "--input", help="input file", required=True)
    parser.add_argument("-o", "--output", help="output path")
    parser.add_argument("-f", "--framerate", help="set framerate for encoding (as a fraction)", default="1/5", type=str)

    args = parser.parse_args()

    setup()

    if args.decode:
        bits = get_bits_from_video(args.input)

        file_path = None

        if args.output:
            file_path = args.output

        save_bits_to_file(file_path, bits)

    elif args.encode:
        # isdigit has the benefit of being True and raising an error if the user passes a negative string
        # all() lets us check if both the negative sign and forward slash are in the string, to prevent negative fractions
        if (not args.framerate.isdigit() and "/" not in args.framerate) or all(x in args.framerate for x in ("-", "/")):
            raise NotImplementedError("The framerate must be a positive fraction or an integer for now, like 3, '1/3', or '1/5'!")
        # get bits from file
        bits = get_bits_from_file(args.input)

        # create image sequence
        image_sequence = make_image_sequence(bits)

        # save images
        for index in range(len(image_sequence)):
            image_sequence[index].save(
                f"{FRAMES_DIR}encoded_frames_{index}.png"
            )

        video_file_path = None

        if args.output:
            video_file_path = args.output

        make_video(video_file_path, image_sequence, args.framerate)

    cleanup()
