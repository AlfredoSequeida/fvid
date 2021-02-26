from bitstring import Bits, BitArray
from PIL import Image
import glob
from tqdm import tqdm
import binascii
import argparse
import sys
import os
import getpass
import io
import gzip
import json
import base64
import decimal
import random
import magic

from zfec import easyfec as ef

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from Crypto.Cipher import AES

try:
    from fvid_cython import cy_gbfi, cy_gbfi_h265

    use_cython = True
except (ImportError, ModuleNotFoundError):
    use_cython = False

FRAMES_DIR = "./fvid_frames/"
SALT = (
    "63929291bca3c602de64352a4d4bfe69".encode()
)  # It needs be the same in one instance of coding/decoding
DEFAULT_KEY = " " * 32
DEFAULT_KEY = DEFAULT_KEY.encode()
NOTDEBUG = True
TEMPVIDEO = "_temp.mp4"
FRAMERATE = "1"

# DO NOT CHANGE: (2, 3-8) works sometimes
# this is the most efficient by far though
KVAL = 4
MVAL = 5
# this can by ANY integer that is a multiple of (KVAL/MVAL)
# but it MUST stay the same between encoding/decoding
# reccomended 8-64
BLOCK = 16


class WrongPassword(Exception):
    pass


class MissingArgument(Exception):
    pass


def get_password(password_provided: str) -> bytes:
    """
    Prompt user for password and create a key for decrypting/encrypting

    password_provided: password provided by tge user with -p flag
    """

    if password_provided == "default":
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
            backend=default_backend(),
        )
        key = kdf.derive(password)
        return key

def encode_zfec(bit_array: BitArray) -> BitArray:
    global KVAL, MVAL, BLOCK
    """
    Apply Reed-Solomon error correction every byte to maximize retrieval
    possibility as opposed to applying it to the entire file

    bit_array -- BitArray containing raw file data
    ecc -- The error correction value to be used (default DEFAULT_ECC)
    """

    bits = bit_array.bin

    # split bits into blocks of bits
    byte_list = split_string_by_n(bits, BLOCK)

    ecc_bytes = ""


    print("Applying Zfec Error Correction...")

    encoder = ef.Encoder(KVAL, MVAL)
    for b in tqdm(byte_list):
        ecc_bytes += ''.join(map(bytes.decode, encoder.encode(b.encode('utf-8'))))

    return BitArray(bytes=ecc_bytes.encode('utf-8'))

def get_bits_from_file(
    filepath: str, key: bytes, zfec: bool
) -> BitArray:
    """
    Get/read bits fom file, encrypt data, and zip

    filepath -- the file to read
    key -- key used to encrypt file
    zfec -- if reed solomon should be used to encode bits
    """

    print("Reading file...")

    bitarray = BitArray(filename=filepath)

    if zfec:
        bitarray = encode_zfec(bitarray)

    # encrypt data
    cipher = AES.new(key, AES.MODE_EAX, nonce=SALT)
    ciphertext, tag = cipher.encrypt_and_digest(bitarray.tobytes())

    filename = os.path.basename(filepath)

    # because json can only serialize strings, the byte objects are encoded
    # using base64

    data_bytes = json.dumps(
        {
            "tag": base64.b64encode(tag).decode("utf-8"),
            "data": base64.b64encode(ciphertext).decode("utf-8"),
            "filename": filepath,
        }
    ).encode("utf-8")

    # print("Zipping...")

    # zip
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(data_bytes)
    zip = out.getvalue()
    # zip

    del bitarray

    bitarray = BitArray(zip)
    # bitarray = BitArray(data_bytes)

    return bitarray.bin


def get_bits_from_image(image: Image, use_h265: bool) -> str:
    """
    extract bits from image (frame) pixels

    image -- png image file used to extract bits from
    """

    # use two different functions so we can type pixel correctly
    if use_cython and not use_h265:
        return cy_gbfi(image)
    elif use_cython and use_h265:
        return cy_gbfi_h265(image)

    width, height = image.size

    px = image.load()
    bits = ""

    # use separate code path so we dont check inside every loop
    if not use_h265:
        for y in range(height):
            for x in range(width):
                pixel = px[x, y]
                pixel_bin_rep = "0"

                # if the white difference is smaller, that means the pixel is
                # closer to white, otherwise, the pixel must be black
                if (
                    abs(pixel[0] - 255) < abs(pixel[0] - 0)
                    and abs(pixel[1] - 255) < abs(pixel[1] - 0)
                    and abs(pixel[2] - 255) < abs(pixel[2] - 0)
                ):
                    pixel_bin_rep = "1"

                # adding bits
                bits += pixel_bin_rep
    else:
        for y in range(height):
            for x in range(width):
                pixel = px[x, y]
                pixel_bin_rep = "0"

                # pixel is either 0 or 255, black or white
                if pixel == 255:
                    pixel_bin_rep = "1"

                # adding bits
                bits += pixel_bin_rep

    return bits


def get_bits_from_video(video_filepath: str, use_h265: bool) -> str:
    """
    extract the bits from a video by frame (using a sequence of images)

    video_filepath -- The file path for the video to extract bits from
    """

    print("Reading video...")

    image_sequence = []
    if use_h265:
        os.system(
            "ffmpeg -i '"
            + video_filepath
            + "' -c:v libx265 -filter:v fps=fps="
            + FRAMERATE
            + " -x265-params lossless=1 -preset 6 -tune grain "
            + TEMPVIDEO
        )
    else:
        os.system(
            "ffmpeg -i '"
            + video_filepath
            + "' -c:v libx264rgb -filter:v fps=fps="
            + FRAMERATE
            + " "
            + TEMPVIDEO
        )
    os.system(
        "ffmpeg -i " + TEMPVIDEO + " ./fvid_frames/decoded_frames_%d.png"
    )
    os.remove(TEMPVIDEO)

    for filename in sorted(
        glob.glob(f"{FRAMES_DIR}decoded_frames*.png"), key=os.path.getmtime
    ):
        image_sequence.append(Image.open(filename))

    bits = ""
    sequence_length = len(image_sequence)
    print("Bits are in place")

    if use_cython:
        print("Using Cython...")

    for index in tqdm(range(sequence_length)):
        bits += get_bits_from_image(image_sequence[index], use_h265)

    return bits


def decode_zfec(data_bytes: bytes) -> bytes:
    global KVAL, MVAL, BLOCK

    byte_list = split_string_by_n(data_bytes, int(BLOCK*(MVAL/KVAL)))

    # appending to a single bytes object is very slow so we make 50-51 and combine at the end
    decoded_bytes = [bytes()] * (int(len(byte_list) / 50) + 1)

    print("Decoding Zfec Error Correction...")

    decoder = ef.Decoder(KVAL, MVAL)
    i = 0
    for b in tqdm(byte_list):
        base = split_string_by_n(b, len(b) // MVAL)
        decoded_str_1 = decoder.decode(base[:KVAL], list(range(KVAL)), 0)
        decoded_str_2 = decoder.decode(base[1:KVAL+1], list(range(KVAL+1))[1:], 0)
        if decoded_str_1 == decoded_str_2:
            decoded_bytes[i//50] += decoded_str_1
        else: # its corrupted here
            j = 10
            while j > 0 and decoded_str_1 != decoded_str_2:
                random.shuffle(base)
                decoded_str_1 = decoder.decode(base[:KVAL], list(range(KVAL)), 0)
                decoded_str_2 = decoder.decode(base[1:KVAL+1], list(range(KVAL+1))[1:], 0)
                j -= 1
            decoded_bytes[i//50] += decoded_str_1 # it should be correct by now
        i += 1

    decoded_bytestring = bytes()
    
    for bytestring in tqdm(decoded_bytes):
        decoded_bytestring += bytestring

    return decoded_bytestring


def save_bits_to_file(
    file_path: str, bits: str, key: bytes, zfec: bool
):
    """
    save/write bits to a file

    file_path -- the path to write to
    bits -- the bits to write
    key -- key userd for file decryption
    zfec -- needed if reed solomon was used to encode bits
    """

    bitstring = Bits(bin=bits)

    # zip
    print("Unziping...")
    in_ = io.BytesIO()
    in_.write(bitstring.bytes)
    in_.seek(0)
    # DOES NOT WORK IF WE DONT CHECK BUFFER, UNSURE WHY
    filetype = magic.from_buffer(in_.read())
    in_.seek(0)
    with gzip.GzipFile(fileobj=in_, mode="rb") as fo:
        bitstring = fo.read()
    # zip

    # loading data back from bytes to utf-8 string to deserialize
    data = json.loads(bitstring.decode("utf-8"))

    # decoding previously encoded base64 bytes data to get bytes back
    tag = base64.b64decode(data["tag"])
    ciphertext = base64.b64decode(data["data"])

    filename = data["filename"]

    # decrypting data
    cipher = AES.new(key, AES.MODE_EAX, nonce=SALT)
    data_bytes = cipher.decrypt(ciphertext)

    print("Checking integrity...")

    try:
        cipher.verify(tag)
    except ValueError:
        raise WrongPassword("Key incorrect or message corrupted")

    bitstring = Bits(data_bytes)

    if zfec:
        bitstring = Bits(
            "0b" + decode_zfec(data_bytes).decode("utf-8")
        )

    # If filepath not passed in use default otherwise used passed in filepath
    if file_path == None:
        filepath = filename
    else:
        filepath = file_path

    with open(filepath, "wb") as f:
        bitstring.tofile(f)


def split_string_by_n(bitstring: str, n: int) -> list:
    """
    Split a string every n number of characters
    (or less if the 'remaining characters' < n ) this way we can sperate the
    data for an etire video into a list based on the resolution of a frame.

    bitstring -- a string containing bits
    n -- split the string every n characters, for example to split a
    1920 x 1080 frame, this would be 1920*1080 = 2073600
    """

    bit_list = []

    for i in range(0, len(bitstring), n):
        bit_list.append(bitstring[i : i + n])

    return bit_list


def make_image_sequence(bitstring: BitArray, resolution: tuple = (1920, 1080)):
    """
    Create image sequence (frames) for a video

    bitstring -- BitArray of bits used to create pixels with bit data
    resolution -- the resoultion used for each frame (default 1920x1080)
    """

    width, height = resolution

    # split bits into sets of width*height to make (1) image
    set_size = width * height

    # bit_sequence = []
    print("Making image sequence")
    print("Cutting...")

    bitlist = split_string_by_n(bitstring, set_size)

    del bitstring

    bitlist[-1] = bitlist[-1] + "0" * (set_size - len(bitlist[-1]))

    index = 1
    bitlist = bitlist[::-1]

    print("Saving frames...")

    for _ in tqdm(range(len(bitlist))):
        bitl = bitlist.pop()
        image_bits = list(map(int, bitl))

        image = Image.new("1", (width, height))
        image.putdata(image_bits)
        image.save(f"{FRAMES_DIR}encoded_frames_{index}.png")
        index += 1


def make_video(output_filepath: str, framerate: int = FRAMERATE, use_h265: bool = False):
    """
    Create video using ffmpeg

    output_filepath -- the output file path where to store the video
    framerate -- the framerate for the vidoe (default 1)
    """

    if output_filepath == None:
        outputfile = "file.mp4"
    else:
        outputfile = output_filepath

    if use_h265:
        os.system(
            "ffmpeg -r "
            + framerate
            + " -i ./fvid_frames/encoded_frames_%d.png -c:v libx265 "
            + " -x265-params lossless=1 -preset 6 -tune grain "
            + outputfile
        )
    else:
        os.system(
            "ffmpeg -r "
            + framerate
            + " -i ./fvid_frames/encoded_frames_%d.png -c:v libx264rgb "
            + outputfile
        )

def cleanup():
    """
    Clean up the files (frames) creted by fvid during encoding/decoding
    """
    import shutil

    shutil.rmtree(FRAMES_DIR)


def setup():
    """
    setup fvid directory used to store frames for encoding/decoding
    """

    if not os.path.exists(FRAMES_DIR):
        os.makedirs(FRAMES_DIR)

def main():
    global FRAMERATE
    parser = argparse.ArgumentParser(description="save files as videos")
    parser.add_argument(
        "-e", "--encode", help="encode file as video", action="store_true"
    )
    parser.add_argument(
        "-d", "--decode", help="decode file from video", action="store_true"
    )

    parser.add_argument("-i", "--input", help="input file", required=True)
    parser.add_argument("-o", "--output", help="output path")
    parser.add_argument(
        "-f",
        "--framerate",
        help="set framerate for encoding (as a fraction)",
        default=FRAMERATE,
        type=str,
    )
    parser.add_argument(
        "-p",
        "--password",
        help="set password",
        nargs="?",
        type=str,
        default="default",
    )
    parser.add_argument(
        "-z",
        "--zfec",
        help=(
            "Apply Zfec error correcting. This is helpful if you're"
            " finding that your data is not being decoded correctly. It adds"
            " 2 extra bits per byte making it possible to recover all 8 bits"
            " in the case the data changes during the decoding process at"
            " the cost of making your video files larger. Note, if you use"
            " this option, you must also use the -r flag to decode a video"
            " back to a file, otherwise, your data will not be recovered"
            " correctly."
        ),
        action="store_true",
    )
    parser.add_argument(
        "-5",
        "--h265",
        help="Use H.265 codec for improved efficiency",
        action="store_true",
    )

    args = parser.parse_args()

    setup()

    if not NOTDEBUG:
        print("args", args)
        print(
            "PASSWORD",
            args.password,
            [
                len(args.password) if len(args.password) is not None else None
                for _ in range(0)
            ],
        )

    # using default framerate if none is provided by the user
    if args.framerate != FRAMERATE:
        FRAMERATE = args.framerate

    # check for arguments
    if not args.decode and not args.encode:
        raise MissingArgument("You should use either --encode or --decode!")

    key = get_password(args.password)

    if args.decode:
        bits = get_bits_from_video(args.input, args.h265)

        file_path = None

        if args.output:
            file_path = args.output

        save_bits_to_file(file_path, bits, key, args.zfec)

    elif args.encode:

        # isdigit has the benefit of being True and raising an error if the
        # user passes a negative string
        # all() lets us check if both the negative sign and forward slash are
        # in the string, to prevent negative fractions
        if (not args.framerate.isdigit() and "/" not in args.framerate) or all(
            x in args.framerate for x in ("-", "/")
        ):
            raise NotImplementedError(
                "The framerate must be a positive fraction or an integer for "
                "now, like 3, '1/3', or '1/5'!"
            )

        # get bits from file
        bits = get_bits_from_file(args.input, key, args.zfec)

        # create image sequence
        make_image_sequence(bits)

        video_file_path = None

        if args.output:
            video_file_path = args.output

        make_video(video_file_path, args.framerate, args.h265)

    cleanup()

if __name__ == '__main__':
    main()