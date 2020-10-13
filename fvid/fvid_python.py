from bitstring import Bits, BitArray
from PIL import Image
import glob

from operator import sub
import numpy as np
from tqdm import tqdm

import binascii

import argparse
import sys
import os

import getpass 

import io
import gzip
import pickle

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from Crypto.Cipher import AES

try:
    from fvid_cython import cy_get_bits_from_image as cy_gbfi
except (ImportError, ModuleNotFoundError):
    use_cython = False
else:
    use_cython = True

FRAMES_DIR = "./fvid_frames/"
SALT = '63929291bca3c602de64352a4d4bfe69'.encode()  # It need be the same in one instance of coding/decoding
DEFAULT_KEY = ' '*32
DEFAULT_KEY = DEFAULT_KEY.encode()
NOTDEBUG = True

class WrongPassword(Exception):
    pass

class MissingArgument(Exception):
    pass

def get_password(password_provided):
    if password_provided=='default':
        return DEFAULT_KEY
    else:
        if password_provided == None:
            password_provided = getpass.getpass("Enter password:")

        password = str(password_provided).encode()  
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=SALT,
            iterations=100000,
            backend=default_backend()
            )
        key = kdf.derive(password)
        return key



def get_bits_from_file(filepath, key):
    print('Reading file...')
    bitarray = BitArray(filename=filepath)
    # adding a delimiter to know when the file ends to avoid corrupted files
    # when retrieving

    cipher = AES.new(key, AES.MODE_EAX, nonce=SALT)
    ciphertext, tag = cipher.encrypt_and_digest(bitarray.tobytes())
    
    filename = os.path.basename(filepath)
    pickled = pickle.dumps({'tag':tag,
                            'data':ciphertext,
                            'filename':filepath})
    print('Ziping...')
    #zip
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode='w') as fo:
        fo.write(pickled)
    zip = out.getvalue()
    #zip
    
    del bitarray
    del pickled

    bitarray = BitArray(zip)
    return bitarray.bin

def less(val1, val2):
    return val1 < val2

def get_bits_from_image(image):
    if use_cython:
        bits = cy_gbfi(image)
        return bits, False
    width, height = image.size

    done = False

    px = image.load()
    bits = ""

    pbar = range(height)
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    for y in pbar:
        for x in range(width):

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
    print('Reading video...')
    image_sequence = []

    os.system('ffmpeg -i ' + video_filepath + ' ./fvid_frames/decoded_frames_%d.png');

    # for filename in glob.glob(f"{FRAMES_DIR}decoded_frames*.png"):
    for filename in sorted(glob.glob(f"{FRAMES_DIR}decoded_frames*.png"), key=os.path.getmtime) :
        image_sequence.append(Image.open(filename))

    bits = ""
    sequence_length = len(image_sequence)
    print('Bits are in place')
    for index in tqdm(range(sequence_length)):
        b, done = get_bits_from_image(image_sequence[index])

        bits += b

        if done:
            break

    return bits


def save_bits_to_file(file_path, bits, key):
    # get file extension

    bitstring = Bits(bin=bits)

    #zip
    print('Unziping...')
    in_ = io.BytesIO()
    in_.write(bitstring.bytes)
    in_.seek(0)
    with gzip.GzipFile(fileobj=in_, mode='rb') as fo:
        bitstring = fo.read()
    #zip


    unpickled = pickle.loads(bitstring)
    tag = unpickled['tag']
    ciphertext = unpickled['data']
    filename = unpickled['filename']
    
    cipher = AES.new(key, AES.MODE_EAX, nonce=SALT)
    bitstring = cipher.decrypt(ciphertext)
    print('Checking integrity...')
    try:
     cipher.verify(tag)
    except ValueError:
     raise WrongPassword("Key incorrect or message corrupted")

    bitstring = BitArray(bitstring)


    # If filepath not passed in use defualt
    #    otherwise used passed in filepath
    if file_path == None:
        filepath = filename
    else:
        filepath = file_path # No need for mime Magic

    with open(
        filepath, "wb"
    ) as f:
        bitstring.tofile(f)



def split_list_by_n(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def make_image_sequence(bitstring, resolution=(1920, 1080)):
    width, height = resolution

    # split bits into sets of width*height to make (1) image
    set_size = width * height

    # bit_sequence = []
    print('Making image sequence')
    print('Cutting...')
    #bitlist = list(tqdm(split_list_by_n(bitstring, set_size)))
    bitlist = list(split_list_by_n(bitstring, set_size))
    
    del bitstring
    
    bitlist[-1] = bitlist[-1] + '0'*(set_size - len(bitlist[-1]))

    index = 1
    bitlist = bitlist[::-1]
    print('Saving frames...')
    for _ in tqdm(range(len(bitlist))):
        bitl = bitlist.pop()
    # for bitl in tqdm(bitlist):
        # image_bits = list(map(int, tqdm(bitl)))
        image_bits = list(map(int, bitl))
        # print(image_bits)

        image = Image.new("1", (width, height))
        image.putdata(image_bits)
        image.save(
            f"{FRAMES_DIR}encoded_frames_{index}.png"
        )
        index += 1


def make_video(output_filepath, framerate="1/5"):

    if output_filepath == None:
        outputfile = "file.mp4"
    else:
        outputfile = output_filepath

    os.system('ffmpeg -r ' + framerate + ' -i ./fvid_frames/encoded_frames_%d.png -c:v libx264rgb ' + outputfile)



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
    parser.add_argument("-p", "--password", help="set password", nargs="?", type=str, default='default')

    args = parser.parse_args()

    setup()
    if not NOTDEBUG:
        print('args', args)
        print('PASSWORD', args.password, [len(args.password) if len(args.password) is not None else None for _ in range(0)])
    
    if not args.decode and not args.encode:
        raise   MissingArgument('You should use either --encode or --decode!') #check for arguments
    
    key = get_password(args.password)
    
    if args.decode:
        bits = get_bits_from_video(args.input)

        file_path = None

        if args.output:
            file_path = args.output

        save_bits_to_file(file_path, bits, key)

    elif args.encode:
        # isdigit has the benefit of being True and raising an error if the user passes a negative string
        # all() lets us check if both the negative sign and forward slash are in the string, to prevent negative fractions
        if (not args.framerate.isdigit() and "/" not in args.framerate) or all(x in args.framerate for x in ("-", "/")):
            raise NotImplementedError("The framerate must be a positive fraction or an integer for now, like 3, '1/3', or '1/5'!")
        # get bits from file
        bits = get_bits_from_file(args.input, key)

        # create image sequence
        make_image_sequence(bits)


        video_file_path = None

        if args.output:
            video_file_path = args.output

        make_video(video_file_path, args.framerate)
    
    cleanup()
