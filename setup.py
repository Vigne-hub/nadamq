#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import versioneer

from path_helpers import path
from setuptools import setup, Extension, find_namespace_packages

# Check if Cython is available
try:
    from Cython.Build import cythonize

    CYTHON_BUILD = True
except ImportError:
    CYTHON_BUILD = False

base_path = path('.')#path(os.environ['SRC_DIR'])#path(__file__).parent
src_path = base_path.joinpath('nadamq', 'src')
include_dirs = [str(src_path)]
sources = [src_path / f for f in ['crc-16.cpp', 'crc_common.cpp', 'packet_actions.cpp']]
sources += [base_path.joinpath('nadamq', 'NadaMq.pyx') if CYTHON_BUILD
            else base_path.joinpath('nadamq', 'NadaMq.cpp')]
sources = [str(source) for source in sources]

# print(f"{'-' * 100}\n", include_dirs, f"{'-' * 100}\n")
# print(f"{'-' * 100}\n", sources, f"{'-' * 100}\n")

if CYTHON_BUILD:
    compiler_directives = {"language_level": 3, "embedsignature": True}
    # Cython build: Convert .pyx to .cpp and compile
    if os.name == 'nt':
        cy_config = dict(include_dirs=include_dirs, language='c++', compiler_directives=compiler_directives)
    else:
        cy_config = dict(include_dirs=include_dirs, language='c++', compiler_directives=compiler_directives)
    _extensions = [Extension('nadamq.NadaMq', sources, **cy_config)]
    extensions = cythonize(_extensions)
else:
    # Pre-generated .cpp sources build
    ext_config = dict(include_dirs=include_dirs)
    extensions = [Extension('nadamq.NadaMq', sources, **ext_config)]

setup(
    name='nadamq',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Embedded-friendly transport layer, inspired by ZeroMQ',
    keywords='cython embedded zeromq transport packet parse',
    author='Christian Fobel',
    author_email='christian@fobel.net',
    url='https://github.com/sci-bots/nadamq',
    license='GPL',
    # packages=['nadamq'],
    packages=find_namespace_packages(include=['nadamq*']),
    python_requires='>=3.6',
    include_package_data=True,
    ext_modules=extensions
)
