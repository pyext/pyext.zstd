#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from distutils.core import setup, Extension
import os

zstd_module = Extension('pyext.zstd._zstd', sources=['pyext/zstd/_zstdmodule.cpp'])
cwd = os.path.abspath(os.path.dirname(__file__))

setup(name='pyext.zstd',
      version='1.0',
      author='SSE4',
      author_email='tomskside@gmail.com',
      url='https://github.com/pyext/pyext.zstd',
      description='pyext_zstd is zstd compression/decompression binding',
      keywords='compression, decompression, archive',
      long_description=open(os.path.join(cwd, "README.md"), 'rb').read().decode("utf-8"),
      long_description_content_type='text/markdown',
      classifiers=['Development Status :: 1 - Planning',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: C',
                   'Programming Language :: C++',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Topic :: System :: Archiving :: Compression',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: POSIX :: Linux'],
      license='MIT',
      packages=['pyext', 'pyext.zstd'],
      ext_modules=[zstd_module],
      include_package_data=True,
      package_data={"": ["README.md"]})
