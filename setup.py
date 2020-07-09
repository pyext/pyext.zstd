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
import platform
import subprocess
import sys


# FIXME : I want to be a python module!
def _get_python_path(name):
    import sysconfig
    return sysconfig.get_path(name)


def _get_python_sc_var(name):
    import sysconfig
    return sysconfig.get_config_var(name)


def _get_python_du_var(name):
    import distutils.sysconfig as du_sysconfig
    return du_sysconfig.get_config_var(name)


def _get_python_var(name):
    return _get_python_sc_var(name) or _get_python_du_var(name)


def _python_inc():
    import sysconfig
    return sysconfig.get_python_inc()


def _python_abiflags():
    import sys
    return getattr(sys, 'abiflags', '')


def _python_version():
    import sys
    return '%s.%s' % (sys.version_info[0], sys.version_info[1])


def _python_include():
    include = _get_python_path('include')
    plat_include = _get_python_path('platinclude')
    include_py = _get_python_var('INCLUDEPY')
    include_dir = _get_python_var('INCLUDEDIR')
    python_inc = _python_inc

    candidates = [include,
                  plat_include,
                  include_py,
                  include_dir,
                  python_inc]
    for candidate in candidates:
        if candidate:
            python_h = os.path.join(candidate, 'Python.h')
            print('checking %s' % python_h)
            if os.path.isfile(python_h):
                print('found Python.h: %s' % python_h, candidate)
                return candidate.replace('\\', '/')
    raise Exception("couldn't locate Python.h - make sure you have installed python development files")


def _python_libraries():
    stdlib = _get_python_var("stdlib")
    platstdlib = _get_python_var("platstdlib")
    library = _get_python_var("LIBRARY")
    ldlibrary = _get_python_var("LDLIBRARY")
    libdir = _get_python_var("LIBDIR")
    multiarch = _get_python_var("MULTIARCH")
    masd = _get_python_var("multiarchsubdir")
    with_dyld = _get_python_var("WITH_DYLD")
    if libdir and multiarch and masd:
        if masd.startswith(os.sep):
            masd = masd[len(os.sep):]
        libdir = os.path.join(libdir, masd)

    if not libdir:
        libdest = _get_python_var("LIBDEST")
        libdir = os.path.join(os.path.dirname(libdest), "libs")

    candidates = [stdlib, platstdlib, ldlibrary, library]
    library_prefixes = [""] if os.name == 'nt' else ["", "lib"]
    library_suffixes = [".lib"] if os.name == 'nt' else [".so", ".dll.a", ".a"]
    if with_dyld:
        library_suffixes.insert(0, ".dylib")

    python_version = _python_version()
    python_version_no_dot = python_version.replace(".", "")
    versions = ["", python_version, python_version_no_dot]
    abiflags = _python_abiflags()

    for prefix in library_prefixes:
        for suffix in library_suffixes:
            for version in versions:
                candidates.append("%spython%s%s%s" % (prefix, version, abiflags, suffix))

    for candidate in candidates:
        if candidate:
            python_lib = os.path.join(libdir, candidate)
            print('checking %s' % python_lib)
            if os.path.isfile(python_lib):
                print('found python library: %s' % python_lib)
                return python_lib.replace('\\', '/')
    raise Exception("couldn't locate python libraries - make sure you have installed python development files")


class CMakeConanBuild(build_ext):
    def run(self):
        for extension in self.extensions:
            self._build(extension)

    def _get_vs_version(self):
        import json

        program_files = os.environ.get("ProgramFiles(x86)", os.environ.get("ProgramFiles"))
        vswhere = os.path.join(program_files, "Microsoft Visual Studio", "Installer", "vswhere.exe")

        cmd = [vswhere, "-format", "json", "-all", "-prerelease", "-latest", "-legacy", "-version", "16"]
        out = subprocess.check_output(cmd).decode()
        data = json.loads(out)
        version = data[0]["installationVersion"]
        return version.split(".")[0]

    def _build(self, extension):
        build_type = "Debug" if self.debug else "Release"
        is64bit = sys.maxsize > 2**32
        sources = extension.sources
        for source in sources:
            if source.endswith("conanfile.txt") or source.endswith("conanfile.py"):
                conanfile_dir = os.path.abspath(os.path.dirname(source))
                the_os = {"Windows": "Windows",
                          "Darwin": "Macos",
                          "Linux": "Linux"}.get(platform.system())
                arch = "x86_64" if is64bit else "x86"
                settings = {"os": the_os,
                            "os_build": the_os,
                            "arch": arch,
                            "arch_build": arch,
                            "build_type": build_type}
                if the_os == "Windows":
                    runtime = "MDd" if self.debug else "MD"
                    settings["compiler"] = "Visual Studio"
                    settings["compiler.version"] = self._get_vs_version()
                    settings["compiler.runtime"] = runtime
                cmd = ["conan",
                       "install",
                       ".",
                       "--build",
                       "missing"]
                for name, value in settings.items():
                    cmd.extend(["-s", "%s=%s" % (name, value)])
                subprocess.check_call(cmd, cwd=conanfile_dir)
                break

        for source in sources:
            if source.endswith("CMakeLists.txt"):
                config = "Debug" if self.debug else "Release"
                cmake_dir = os.path.abspath(os.path.dirname(source))
                ext_dir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(extension.name)))
                ext_name = os.path.basename(self.get_ext_fullpath(extension.name))

                if not os.path.isdir(self.build_temp):
                    os.makedirs(self.build_temp)

                definitions = dict()
                definitions["CMAKE_BUILD_TYPE"] = build_type
                definitions["CMAKE_LIBRARY_OUTPUT_DIRECTORY_%s" % build_type.upper()] = ext_dir
                definitions["CMAKE_ARCHIVE_OUTPUT_DIRECTORY_%s" % build_type.upper()] = ext_dir
                definitions["CMAKE_RUNTIME_OUTPUT_DIRECTORY_%s" % build_type.upper()] = ext_dir
                definitions["OUTPUT_NAME"] = os.path.splitext(ext_name)[0]
                definitions["OUTPUT_SUFFIX"] = os.path.splitext(ext_name)[1]
                definitions["PYTHON_LIBRARY"] = _python_libraries()
                definitions["PYTHON_INCLUDE_DIR"] = _python_include()

                cmd = ["cmake", cmake_dir]
                if os.name == "nt":
                    version = self._get_vs_version()
                    year = {"9": "2008",
                            "10": "2010",
                            "11": "2012",
                            "12": "2013",
                            "14": "2015",
                            "15": "2017",
                            "16": "2019"}.get(version)
                    cmd.extend(["-G", "Visual Studio %s %s" % (version, year)])
                    if is64bit:
                        cmd.extend(["-A", "x64"])
                    else:
                        cmd.extend(["-A", "Win32"])
                for name, value in definitions.items():
                    cmd.append("-D%s=%s" % (name, value))
                subprocess.check_call(cmd, cwd=self.build_temp)

                cmd = ["cmake", "--build", ".", "--config", build_type]
                subprocess.check_call(cmd, cwd=self.build_temp)
                break


zstd_module = Extension('pyext.zstd._zstd', sources=['pyext/zstd/_zstdmodule.cpp',
                                                     'pyext/zstd/CMakeLists.txt',
                                                     'pyext/zstd/conanfile.txt'])
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
