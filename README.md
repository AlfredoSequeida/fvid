[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

[Demonstration/Explanation Video](https://youtu.be/yu_ZIr0q5rU)

fvid is a project that aims to encode any file as a video using 1-bit color images
to survive compression algorithms for data retrieval.

<p align="center">
    <img src="https://i.imgur.com/LVthky0.png" alt="fvid">
    </br>
</p>

---

# Installation

Requires installation of [FFmpeg](https://ffmpeg.org/download.html) and libmagic first, then install using pip3 

Linux/macOS

```
pip3 install fvid 
```

Windows 

```
py -m pip install fvid 
```

# Usage

Encoding files as videos
 
Linux/OSX

```
fvid -i [input file] -e
fvid -i [input file] --framerate 1 -e
fvid -i [input file] --password "wow fvid is cool" -e
```

Windows 

```
py -m fvid -i [input file] -e
py -m fvid -i [input file] --framerate 1 -e
py -m fvid -i [input file] --password "wow fvid is cool" -e
```

Retrieving data from videos
 
Linux/OSX

```
fvid -i [input video] -d
```

Windows 

```
py -m fvid -i [input video] -d
```

If the file was encoded with a non-default password, it'll prompt you to enter the password upon decoding.
 
 How to Contribute
-----------------

1.  Check for open issues or open a fresh issue to start a discussion
    around a feature idea or a bug [here](https://github.com/AlfredoSequeida/fvid/issues)
    tag for issues that should be ideal for people who are not very familiar with the codebase yet.
2.  Fork [the repository](https://github.com/alfredosequeida/fvid) on
    GitHub to start making your changes to the **master** branch (or branch off of it).
3.  Write a test which shows that the bug was fixed or that the feature
    works as expected.
4.  Send a pull request and bug the maintainer until it gets merged and
    published. :)
