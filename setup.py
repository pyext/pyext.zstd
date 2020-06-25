#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from distutils.core import setup, Extension

pyext_zstd_module = Extension('pyext_zstd', sources=['pyext_zstd.cpp'])

setup(name='pyext_zstd',
      version='1.0',
      author='SSE4',
      author_email='tomskside@gmail.com',
      url='https://github.com/pyext/pyext_zstd',
      description='pyext_zstd is zstd compression/decompression binding',
      long_description='pyext_zstd is zstd compression/decompression binding',
      ext_modules=[pyext_zstd_module])
