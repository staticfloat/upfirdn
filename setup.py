#! /usr/bin/env python

# Copyright (c) 2009, Motorola, Inc
# 
# All Rights Reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright 
# notice, this list of conditions and the following disclaimer in the 
# documentation and/or other materials provided with the distribution.
# 
# * Neither the name of Motorola nor the names of its contributors may be 
# used to endorse or promote products derived from this software without 
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS 
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This module is used to build and install the upfirdn package.

This package consists of the "distribution root" directory (the one containing
setup.py, README.txt, etc.), and an enclosed "package directory" (upfirdn)
within the distribution root.

Usage:
  Commands are run from the distribution root directory.

  python setup.py build_ext 
    builds the _Resampler extension and places it in the package directory
    
  python setup.py install 
    builds the extension, installs the 'upfirdn' package in your python 
    site-packages area
    
"""
# System imports
import os, shutil
from distutils.core import *
from distutils.command.build_ext import build_ext, log

# we depend on numpy for everything
import numpy

majver, minver = [float(i) for i in numpy.__version__.split('.')[:2]]
assert (majver + minver/10. >= 1.2), "Requires Numpy 1.2.0 or above"
# needs function "broadcast_arrays", which appears in 1.2.0 of numpy

# Obtain the numpy include directory.
numpy_include = numpy.get_include()

# extension modules
_Resampler = Extension("upfirdn._Resampler",
                   ["upfirdn/Resampler_wrap.cpp",],
                   include_dirs=[numpy_include],
                   )

class custom_build_ext(build_ext):
    """Override the build_ext command class.

    Specialized behaviors:
     - inplace is disabled, so shared object file is always built in the build
       directory
     - build_extension method is overridden to copy the shared object file from
       the build directory to the package directory
    """
    def __init__(self, *args, **kwargs):
        build_ext.__init__(self, *args, **kwargs)
        self.inplace = False

    def build_extension(self, ext):
        build_ext.build_extension(self, ext)

        fullname = self.get_ext_fullname(ext.name)
        ext_filename = os.path.join(self.build_lib,
                                    self.get_ext_filename(fullname))

        modpath = fullname.split('.')
        package = '.'.join(modpath[:-1])
        base = modpath[-1]

        build_py = self.get_finalized_command('build_py')
        package_dir = build_py.get_package_dir(package)
        inplace_ext_filename = \
                       os.path.join(package_dir,
                                    self.get_ext_filename(base))

        log.info('upfirdn - CUSTOM BUILD EXT')
        log.info('  copying extension from build area to local package:')
        log.info('    from - %s'%ext_filename)
        log.info('      to - %s'%inplace_ext_filename)
        shutil.copy(ext_filename, inplace_ext_filename)
        
setup(name = "upfirdn",
      version = "0.2.1",
      description = "An efficient polyphase FIR resampler",
      author      = "Tom Krauss and Bryan Nollett",
      author_email = 'krauss@motorola.com',
      url = 'http://opensource.motorola.com/sf/projects/upfirdn',
      license = 'Motorola BSD 2.0 [see LICENSE.txt]',
      py_modules = ['upfirdn.Resampler'],
      ext_modules = [_Resampler],
      packages = ['upfirdn'],
      package_data={'upfirdn': ['Makefile', '*.i', '*.h']},
      cmdclass = {'build_ext': custom_build_ext}
      )

