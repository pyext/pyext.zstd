#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

try:
    from setuptools.command.build_ext import build_ext
    from setuptools import setup, Extension
except ImportError:
    from distutils.command.build_ext import build_ext
    from distutils.core import setup
    from distutils.extension import Extension

import os
import sys


class CMakeConanBuild(build_ext):
    def run(self):
        for extension in self.extensions:
            self._build(extension)

    def _build(self, extension):
        import subprocess

        sources = extension.sources
        for source in sources:
            if source.endswith("CMakeLists.txt"):
                config = "Debug" if self.debug else "Release"
                cmake_dir = os.path.abspath(os.path.dirname(source))
                ext_dir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(extension.name)))
                ext_name = os.path.basename(self.get_ext_fullpath(extension.name))

                if not os.path.isdir(self.build_temp):
                    os.makedirs(self.build_temp)

                definitions = dict()
                definitions["CMAKE_BUILD_TYPE"] = config
                definitions["CMAKE_LIBRARY_OUTPUT_DIRECTORY_%s" % config.upper()] = ext_dir
                definitions["CMAKE_ARCHIVE_OUTPUT_DIRECTORY_%s" % config.upper()] = ext_dir
                definitions["CMAKE_RUNTIME_OUTPUT_DIRECTORY_%s" % config.upper()] = ext_dir
                definitions["OUTPUT_NAME"] = os.path.splitext(ext_name)[0]
                definitions["OUTPUT_SUFFIX"] = os.path.splitext(ext_name)[1]

                cmd = ["cmake", cmake_dir]
                if os.name == "nt":
                    if sys.maxsize > 2**32:
                        cmd.extend(["-A", "x64"])
                    else:
                        cmd.extend(["-A", "Win32"])
                for name, value in definitions.items():
                    cmd.append("-D%s=%s" % (name, value))
                subprocess.check_call(cmd, cwd=self.build_temp)

                cmd = ["cmake", "--build", ".", "--config", config]
                subprocess.check_call(cmd, cwd=self.build_temp)
                break


zstd_module = Extension('pyext.zstd._zstd', sources=['pyext/zstd/_zstdmodule.cpp',
                                                     'pyext/zstd/CMakeLists.txt'])
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
      package_data={"": ["README.md"]},
      cmdclass={"build_ext": CMakeConanBuild})
