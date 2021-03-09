import pytest
import unittest
import os
import sys
import subprocess
import fvid
import ffpb
import tqdm
import platform

from helper import SkippableTest
from shlex import split
from collections import namedtuple
from functools import reduce

proc_output = namedtuple('proc_output', 'stdout stderr')

def pipeline(starter_command, *commands):
    if not commands:
        try:
            starter_command, *commands = starter_command.split('|')
        except AttributeError:
            pass
    starter_command = _parse(starter_command)
    starter = subprocess.Popen(starter_command, stdout=subprocess.PIPE)
    last_proc = reduce(_create_pipe, map(_parse, commands), starter)
    return proc_output(*last_proc.communicate())

def _create_pipe(previous, command):
    proc = subprocess.Popen(command, stdin=previous.stdout, stdout=subprocess.PIPE)
    previous.stdout.close()
    return proc

def _parse(cmd):
    try:
        ok = list(map(str, split(cmd)))
        print(ok)
        return ok
    except Exception:
        return cmd

class FvidTestCase(unittest.TestCase):
    def test_decode_from_yt(self):
        logging_info = ""
        encoded_yt_videos = [i for i in sorted(os.listdir('../tests/encoded/'), reverse=True) if i.lower().startswith('yt')]
        for video_name in encoded_yt_videos:
            cmd = "python3 -m" + video_name[2:-4] + " -i '../tests/encoded/" + video_name + "'"
            if platform.system().lower() in ("linux", "darwin"):
                cmd += ' -o /dev/null'
            elif platform.system().lower() in ("windows",):
                cmd += ' -o nul'
            resp = pipeline(cmd)[0].decode('utf-8')
            print(resp)
            logging_info += resp
        assert 'error' not in logging_info.lower()

    def test_encode_and_decode_files(self):
        logging_info = ""
        files = [i for i in sorted(os.listdir('../tests/decoded/'), reverse=True) if not i == 'README.txt']
        possible_encodings = ['-ey5', '-ey5 -f 3', '-eyz5', '-eyz']
        for file_name in files:
            for encoding in possible_encodings:
                cmd = "python3 -m fvid " + encoding + " -i ../tests/decoded/" + file_name + " -o '../tests/temp/yt_fvid_" + encoding + ".mp4'"
                resp = pipeline(cmd)[0].decode('utf-8')
                print(resp)
                logging_info += resp
                break # only doing one for now so we can test decoding
            break
        videos = [i for i in sorted(os.listdir('./temp/'), reverse=True)]
        possible_decodings = ['-dy5', '-dy5 -f 3', '-dyz5', '-dyz']
        for video_name in videos:
            for decoding in possible_decodings:
                cmd = "python3 -m" + video_name[2:-4].replace('_', ' ') + " -i ../tests/temp/" + video_name
                if platform.system().lower() in ("linux", "darwin"):
                    cmd += ' -o /dev/null'
                elif platform.system().lower() in ("windows",):
                    cmd += ' -o nul'
                resp = pipeline(cmd)[0].decode('utf-8')
                print(resp)
                logging_info += resp
                break
            break       
        print(logging_info.lower())
        assert 'error' not in logging_info.lower()


if __name__ == '__main__':
#    try:
#        print(FvidTestCase().test_decode_from_yt())
#        print(FvidTestCase().test_encode_and_decode_files())
#    except KeyboardInterrupt:
#        pass
    pytest.main([__file__])