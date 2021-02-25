Changelog
*********

Planned (1.1.0)
===============

- GUI
- Use json-encoded strings instead of pickle for storing stuff
- Add `-5` flag for H265 encoding/decoding, much smaller output file
- Add zfec error correction

1.0.0
=====

Additions:

- Added support for passwords, custom framerates, and Cython compilation
- file.mp4 compression with ``gzip``
- Pickled data to allow decompression with original file name

Bug Fixes:

- Fixed ``file.bin`` bug
- Removed ``magic``, ``mime``
- New ``make_image_sequence`` logic
- Framerate patch

Performance:

- Huge Cython/Python speedups

0.0.2
=====

- Bug fixes
- Minor speedups

0.0.1
=====

- Initial release
