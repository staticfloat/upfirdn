Copyright (c) 2009, Motorola, Inc

All Rights Reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in the 
documentation and/or other materials provided with the distribution.

* Neither the name of Motorola nor the names of its contributors may be 
used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS 
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,  
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR 
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

--------------------------------------------

OVERVIEW

This package provides a C++ object for efficient, polyphase FIR resampling
along with a python module with a functional and object interface.

See INSTALL.txt for notes about installation.

ALGORITHM DESCRIPTION
A "filter bank with resampling" is an operation on an input signal that 
generates an output signal, consisting of the following 3 steps:
   1) upsampling (that is, zero-insertion) of the input signal by an integer 
      factor (call it P).
   2) applying an FIR (finite-impulse response filter) to the result of 1).
   3) downsampling (that is, decimation) of the result of 2) by an integer 
      factor (call it Q).
 
For an input signal with sampling rate T, the generated output signal has 
sampling rate of P/Q*T.  The FIR filter is usually designed to prevent 
aliasing from corrupting the output signal.
 
An "efficiently implemented, polyphase filter bank with resampling" implements 
these three operations with a minimal amount of computation.
 
The algorithm is an implementation of the block diagram shown on page 129 of 
the Vaidyanathan text [1] (Figure 4.3-8d).

[1]  P. P. Vaidyanathan, Multirate Systems and Filter Banks, Prentice Hall, 
     1993.

PACKAGE OVERVIEW
PYTHON
The module "upfirdn" provides a functional and object interface.
  upfirdn -- function
  ResamplerBank -- object
These python wrappers support multi-dimensional arrays according to the 
usual numpy broadcasting rules.  See their doc-strings for usage notes.

SWIGGED C++
The Resampler object defined in Resampler.h is templatized on
input signal, output signal, and coefficient types.

The _Resampler module is a shared-object extension built from the C++ by SWIG
with typemaps and template instantiations as defined in Resampler.i.
It provides 4 template instantiations:
  ResamplerRR, ResamplerRC, ResamplerCR, ResamplerCC
where the "R/C" denotes real or complex, for the signal type, and the 
coefficient type.
 
