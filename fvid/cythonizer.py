#cython: language_level=3
# distutils: include_dirs = /root/fvid, /rood/fvid/tests
from distutils.core import Extension, setup
from Cython.Build import cythonize

ext = Extension(name="fvid_cython", sources=["fvid_cython.pyx"], include_dirs=['/root/fvid', '/root/fvid/tests'])
setup(ext_modules=cythonize(ext, annotate=True, compiler_directives={'language_level': 3, 'infer_types': True}))
