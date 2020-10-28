import os
import codecs
from setuptools import setup
from setuptools import Extension
from setuptools.command.build_ext import build_ext

try:
    from Cython.Build import cythonize
except ImportError:
    use_cython = False
    ext = 'c'
else:
    use_cython = True
    ext = 'pyx'

try:
    if not use_cython:
        extensions = [Extension("fvid.fvid_cython", ["fvid/fvid_cython.c"], include_dirs=["./fvid", "fvid/"])]
    else:
        extensions = [Extension("fvid.fvid_cython", ["fvid/fvid_cython.pyx"], include_dirs=["./fvid", "fvid/"])]
        extensions = cythonize(extensions, compiler_directives={'language_level': "3", 'infer_types': True})
except: # blanket exception until the exact exception name is found
    extensions = []

with open("README.md", "r") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


dynamic_version = get_version("fvid/__init__.py")

try:
    setup(
        name="fvid",
        version=dynamic_version,
        author="Alfredo Sequeida",
        description="fvid is a project that aims to encode any file as a video using 1-bit color images to survive compression algorithms for data retrieval.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/AlfredoSequeida/fvid",
        download_url="https://github.com/AlfredoSequeida/fvid/archive/"
        + dynamic_version
        + ".tar.gz",
        keywords="fvid youtube videos files bitdum hexdump ffmpeg video file",
        platforms="any",
        classifiers=[
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Operating System :: Microsoft :: Windows :: Windows 10",
            "Operating System :: Microsoft :: Windows :: Windows 8",
            "Operating System :: Microsoft :: Windows :: Windows 8.1",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
        ],
        license="MIT",
        packages=["fvid"],
        install_requires=[
            "bitstring >= 3.1.6",
            "pillow >= 7.2.0",
            "tqdm >= 4.49.0",
            "cryptography >= 3.1.1",
            "pycryptodome >= 3.9.8"
        ],
        python_requires=">=3.6",
        entry_points={"console_scripts": ["fvid = fvid.fvid:main"]},
        cmdclass={'build_ext': build_ext},
        ext_modules=extensions,
        include_package_data=True,
        zip_safe=False,
        )
except:
    setup(
        name="fvid",
        version=dynamic_version,
        author="Alfredo Sequeida",
        description="fvid is a project that aims to encode any file as a video using 1-bit color images to survive compression algorithms for data retrieval.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/AlfredoSequeida/fvid",
        download_url="https://github.com/AlfredoSequeida/fvid/archive/"
        + dynamic_version
        + ".tar.gz",
        keywords="fvid youtube videos files bitdum hexdump ffmpeg video file",
        platforms="any",
        classifiers=[
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Operating System :: Microsoft :: Windows :: Windows 10",
            "Operating System :: Microsoft :: Windows :: Windows 8",
            "Operating System :: Microsoft :: Windows :: Windows 8.1",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
        ],
        license="MIT",
        packages=["fvid"],
        install_requires=[
            "bitstring >= 3.1.6",
            "pillow >= 7.2.0",
            "tqdm >= 4.49.0",
            "cryptography >= 3.1.1",
            "pycryptodome >= 3.9.8"
        ],
        python_requires=">=3.6",
        entry_points={"console_scripts": ["fvid = fvid.fvid:main"]},
        include_package_data=True,
        )
