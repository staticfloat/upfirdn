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

# System imports
from distutils.core import *

# we depend on numpy for everything
import numpy

majver, minver = [float(i) for i in numpy.__version__.split('.')[:2]]
assert (majver >= 1 and minver >= 2), "Requires Numpy 1.2.0 or above"
# needs function "broadcast_arrays", which appears in 1.2.0 of numpy

# Obtain the numpy include directory.
numpy_include = numpy.get_include()

# extension modules
_Resampler = Extension("_Resampler",
                   ["Resampler.i",],
                   include_dirs=[numpy_include],
                   swig_opts=['-c++']
                   )

setup(name = "upfirdn",
      version = "0.1.0",
      description = "An efficient polyphase FIR resampler",
      author      = "Tom Krauss and Bryan Nollett",
      author_email = 'krauss@motorola.com',
      url = 'http://opensource.motorola.com/sf/projects/upfirdn',
      license = 'Motorola BSD 2.0 [see LICENSE.txt]',
      py_modules = ['upfirdn', 'Resampler', 'test_upfirdn'],
      ext_modules = [_Resampler],
      )

