Examples
********

**If you are on Windows, prefix all commands with** `py -m`

Encoding
========
All of these examples assume you have a file named test.jpg inside your current directory.

Basic: ``fvid -i ./test.jpg -e``

3 FPS: ``fvid -i ./test.jpg -e -f 3``

3 FPS + Password: ``fvid -i ./test.jpg -e -f 3 -p "testing testing 123"``

Advanced: ``fvid -i ./test.jpg -ez5 -f 3 -p "ez5 is short for encode, zfec, h265"``

Decoding
========
All of these examples assume you have an fvid-encoded video named file.mp4 inside your current directory.

Basic: ``fvid -i ./file.mp4 -d``

Encoded at 3 FPS: ``fvid -i ./file.mp4 -d -f 3``

Encoded at 3 FPS + Password: ``fvid -i ./file.mp4 -d -f 3`` (It'll prompt you to enter the password)

Advanced: ``fvid -i ./file.mp4 -dz5 -f 3``