This package provides a C++ object for efficient, polyphase FIR resampling along with a python module with a functional and object interface.

# ALGORITHM DESCRIPTION #

A "filter bank with resampling" is an operation on an input signal that generates an output signal, consisting of the following 3 steps:

  1. upsampling (that is, zero-insertion) of the input signal by an integer factor (call it P).
  1. applying an FIR (finite-impulse response filter) to the result of 1.
  1. downsampling (that is, decimation) of the result of 2. by an integer factor (call it Q).

For an input signal with sampling rate T, the generated output signal has sampling rate of P/Q\*T.  The FIR filter is usually designed to prevent aliasing from corrupting the output signal.

An "efficiently implemented, polyphase filter bank with resampling" implements these three operations with a minimal amount of computation.

The algorithm is an implementation of the block diagram shown on page 129 of the Vaidyanathan text `[1]` (Figure 4.3-8d).

`[1]`  P. P. Vaidyanathan, Multirate Systems and Filter Banks, Prentice Hall, 1993.

# PACKAGE OVERVIEW #

## PYTHON ##

The module "upfirdn" provides a functional and object interface.

  * upfirdn - functional interface

  * ResamplerBank - object interface

These python wrappers support multi-dimensional arrays according to the usual numpy broadcasting rules.  See their doc-strings for usage notes.

## SWIGGED C++ ##

The Resampler object defined in Resampler.h is templatized on input signal, output signal, and coefficient types.

The `_`Resampler module is a shared-object extension built from the C++ by SWIG with typemaps and template instantiations as defined in Resampler.i.  It provides 4 template instantiations:
> ResamplerRR, ResamplerRC, ResamplerCR, ResamplerCC
where the "R/C" denotes real or complex, for the signal type, and the coefficient type.

# See Also #
This google code site provides the most recent updates (as of February 2014) and a browsable hg repository.   The project's previous main web site is at https://sourceforge.net/motorola/upfirdn (as of June 2011), which provides archives of individual releases up to a point.