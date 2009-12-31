/*
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
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR 
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
// -*- c++ -*-

%module Resampler

%{
#define SWIG_FILE_WITH_INIT
#include "Resampler.h"
%}

// Get the NumPy typemaps
%include "numpy.i"
%numpy_typemaps(complex<double>, NPY_CDOUBLE, int)

%init %{
  import_array();
%}

// Get the STL typemaps
%include "stl.i"

// Handle standard exceptions
%include "exception.i"
%exception
{
  try
  {
    $action
  }
  catch (const std::invalid_argument& e)
  {
    SWIG_exception(SWIG_ValueError, e.what());
  }
}

%feature("autodoc");

%apply (double* IN_ARRAY1, int DIM1) {(double* coefs, int coefCount)};
%apply (complex<double>* IN_ARRAY1, int DIM1) {(complex<double>* coefs, int coefCount)};

%apply (double* IN_ARRAY1, int DIM1) {(double* in, int inCount)};
%apply (complex<double>* IN_ARRAY1, int DIM1) {(complex<double>* in, int inCount)};

%apply (double* INPLACE_ARRAY1, int DIM1) {(double* out, int outCount)};
%apply (complex<double>* INPLACE_ARRAY1, int DIM1) {(complex<double>* out, int outCount)};

%include "Resampler.h"

%template(ResamplerRR) Resampler<double, double, double>;
%template(ResamplerRC) Resampler<double, complex<double>, complex<double> >;
%template(ResamplerCR) Resampler<complex<double>, complex<double>, double >;
%template(ResamplerCC) Resampler<complex<double>, complex<double>, complex<double> >;
