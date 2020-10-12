import os
import codecs
from distutils.core import Extension, setup
from Cython.Build import cythonize

ext = Extension(name="fvid_cython", sources=["fvid/fvid_cython.pyx"], include_dirs=["./fvid", "fvid/"])
setup(ext_modules=cythonize(ext, compiler_directives={'language_level': 3}))

try:
    from Cython.Build import cythonize
except ImportError:
    pass
else:
    cythonize(Extension("fvid_cython", ["fvid/fvid_cython.pyx"], include_dirs=["./fvid", "fvid/"]), compiler_directives={'language_level': "3", 'infer_types': True})

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
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 8",
        "Operating System :: Microsoft :: Windows :: Windows 8.1",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
    license="MIT",
    packages=["fvid"],
    install_requires=[
        "bitstring",
        "pillow",
        "tqdm",
        "cython >= 0.29.21",
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["fvid = fvid.fvid:main"]},
)
