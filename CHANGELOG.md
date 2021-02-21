__Planned (1.1.0)__
- GUI
- Use json-encoded strings instead of pickle for storing stuff

__1.0.0__

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

__0.0.2__
- Bug fixes
- Minor speedups

__0.0.1__
- Initial release
