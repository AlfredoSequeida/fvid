How To
******

Basic Usage
===========

Assuming you have pip installed fvid, you can use encode videos as follows:

Linux/OSX:

``fvid -i [input file] -e``

``fvid -i [input file] --framerate 1 -e``

``fvid -i [input file] --password "wow fvid is cool" -e``

Windows:

``py -m fvid -i [input file] -e``

``py -m fvid -i [input file] --framerate 1 -e``

``py -m fvid -i [input file] --password "wow fvid is cool" -e``


Decoding is supported also:
 
Linux/OSX:

``fvid -i [input video] -d``

Windows:

``py -m fvid -i [input video] -d``


If the file was encoded with a non-default password, it'll prompt you to enter the password upon decoding.

Options
=======

* ``-i/--input`` After this, specify the path to the file you want to encode/decode
* ``-o/--output`` After this, specify the name of the new file you want to make. Defaults to ``file.mp4`` when encoding.
* ``-e/--encode`` This indicates you're encoding the input file
* ``-d/--decode`` This indicates you're decoding the input file
* ``-f/--framerate`` After this, specify the framerate that you want to have the file output at. A higher value means the frames go faster. Defaults to 1 fps.
* ``-p/--password`` After this, specify the password you want to encode with. You will need to remember this to decode the file. Defaults to 32 spaces.