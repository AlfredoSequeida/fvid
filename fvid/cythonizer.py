#cython: language_level = 3
from distutils.core import Extension, setup
from Cython.Build import cythonize

ext = Extension(name="fvid_cython", sources=["fvid_cython.pyx"])
setup(ext_modules=cythonize(ext, compiler_directives={'language_level': 3, 'infer_types': True}))
