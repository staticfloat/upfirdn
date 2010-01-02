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

import numpy as np
from Resampler import ResamplerRR, ResamplerRC, ResamplerCR, ResamplerCC

def enumdims(ary, dims=(0,), complement=False):
    """Enumerate over the given array dimensions
    yielding the index tuple and resulting array in sequence, 
    using ":" for each of the complementary dimensions.
    For example, if x is an array of shape (2,3,4),
       iterdims(x, [0]) yields 2 arrays of shape (3,4)
       iterdims(x, [1]) yields 3 arrays of shape (2,4)
       iterdims(x, [2]) yields 4 arrays of shape (2,3)
       iterdims(x, [0,1]) yields 6 arrays of shape (4)
       iterdims(x, [0,2]) yields 8 arrays of shape (3)
       iterdims(x, [1,2]) yields 12 arrays of shape (2)
       iterdims(x, [0,1,2]) yields 24 arrays of shape () (i.e., 0-D)
       iterdims(x, []) yields 1 array of shape (2,3,4)
       ...  
        
    """ 
    dimsNoNegative = []
    for d in dims: 
        if d < 0:
            dimsNoNegative.append(len(ary.shape)+d)
        else:
            dimsNoNegative.append(d)
    dims = tuple(dimsNoNegative)
    cdims = tuple([i for i in range(len(ary.shape)) if i not in dims])
    if complement:
        dims, cdims = cdims, dims
    x = ary.transpose(*(tuple(dims) + cdims))
    ndindexArgs = tuple([x.shape[i] for i in range(len(dims))])
    for idxTuple in np.ndindex(*ndindexArgs):
        yield idxTuple, x[idxTuple]

def iterdims(ary, dims=(0,), complement=False):
    """Like enumdims but yielding only the partial arrays, not
    the index tuple as well
 
    for xi in iterdims(x):  <-- equivalent to "for xi in x:"
    for xi in iterdims(x,[-1]):  <-- yields x[...,0], x[...,1], ... etc
    for xi in iterdims(x,[0,-1]):  <-- yields x[0,...,0], x[0,...,1], ... etc
    for xi in iterdims(x,[0,1]):  <-- yields x[0,0,...], x[0,1,...], ... etc
    """ 
    for idx, x in enumdims(ary, dims, complement):
        yield x

def full_index(x):
    """Return a list of arrays to index into array x."""
    idx = [np.arange(xs) for xs in x.shape]
    for i in range(len(idx)):
        idx[i].shape += (1,)*(len(x.shape)-i-1)
    return idx
    
def dim2back(x, xdim=-1):
    """
    Transpose ndarray so that a given dimension is moved to the back.
    
    Parameters
    ----------
    x : ndarray
        Input array.
    xdim : int, optional
        Dimension to put at back "x" input array. (default=-1)
        
    Returns
    -------
    y : ndarray 
        view of x transposed

    """
    num_dims_x = len(x.shape)
    if xdim < 0:
        xdim = num_dims_x + xdim
    return x.transpose(*(range(xdim) + range(xdim+1, num_dims_x) + [xdim]))

def back2dim(x, xdim=-1):
    """
    Transpose ndarray so that the back dimension is moved to a given position.
    
    Parameters
    ----------
    x : ndarray
        Input array.
    xdim : int, optional
        Dimension at which to put the back "x" input array dimension. 
        (default=-1)
        
    Returns
    -------
    y : ndarray 
        view of x transposed

    """
    num_dims_x = len(x.shape)
    if xdim < 0:
        xdim = num_dims_x + xdim
    return x.transpose(*(range(xdim) + [num_dims_x-1] + \
                         range(xdim, num_dims_x-1)))


# Index into Resampler object type switchyard is 
#  (signal type complex,  coefficient type complex) booleans
_SWITCH_YARD = {
    (False, False): ResamplerRR,
     (False, True): ResamplerRC,
     (True, False): ResamplerCR,
      (True, True): ResamplerCC
}

def klass_lookup(signal=1., coefficients=1.):
    """Return Resampler type based on input signal and coefficient objects.
    """
    klass = _SWITCH_YARD[(np.iscomplexobj(signal), \
                          np.iscomplexobj(coefficients))]
    return klass
    
class ResamplerBank(object):
    """
    A bank of Resampler objects.
    """
    def __init__(self, x, h, uprate=1, downrate=1, xdim=-1, hdim=-1):
        """
        Construct the ResamplerBank object.
        
        Parameters
        ----------
        x : array-like
            Input signal array.  May be multi-dimensional (ND).  The signals
            will be operated on along the "xdim" dimension of x.
            This is needed to determine how many Resamplers need to be created,
            since each one needs to retain state.
        h : array-like
            FIR (finite-impulse response) filter coefficients array.  May be ND.
            The filters are along the "hdim" dimension of h.
        uprate : int, optional
            Upsampling rate. (default=1)
        downrate : int, optional
            Downsampling rate. (default=1)
        xdim : int, optional
            Dimension for "x" input signal array. (default=-1)
        hdim : int, optional
            Dimension for "h" coefficient array. (default=-1)
    
        """
        x = np.atleast_1d(x)
        h = np.atleast_1d(h)
        klass = klass_lookup(x, h)
        
        x = dim2back(x, xdim)
        h = dim2back(h, hdim)
        
        xi = full_index(x)
        xi[-1] = xi[-1][0:1]
 
        # xx is ignored
        xx, hh = np.broadcast_arrays(x[xi], h)
        self.hh = hh
        bank = np.zeros(self.hh.shape[:-1], dtype=object)
        for idx, hi in enumdims(self.hh, (-1,), complement=True):
            bank[idx] = klass(uprate, downrate, hi)

        self.bank = bank
        self.r0 = self.bank.flat[0]
        self.coefs_per_phase = (h.shape[-1] + uprate - 1) // uprate
        self.xdim = xdim
        if np.iscomplexobj(x) or np.iscomplexobj(h):
            self.output_type = complex
        else:
            self.output_type = float
        
    def apply(self, x, all_samples=False):
        """
        Upsample, FIR filter, and downsample a signal or array of signals using
        the bank of Resampler objects.
        
        Parameters
        ----------
        x : array-like
            Input signal array.  May be multi-dimensional (ND).  The signals
            will be operated on along the "xdim" dimension of x.
        all_samples : bool, optional
            If True, feeds in zeros after the input signal to "drain" the 
            resampler and get all the non-zero samples.  (default=True)
            
        Returns
        -------
        y : float ndarray
    
        """
        x = np.atleast_1d(x)
        x = dim2back(x, self.xdim)
        # htemp is ignored
        xx, htemp = np.broadcast_arrays(x, self.hh[..., 0:1])
        in_count = xx.shape[-1]
        if all_samples:
            in_count += self.coefs_per_phase-1
            z = np.zeros((self.coefs_per_phase-1,))
        needed_out_count = self.r0.neededOutCount(in_count)
        y = np.zeros(xx.shape[:-1] + (needed_out_count,), \
                dtype=self.output_type)
        for idx, xi in enumdims(xx, (-1,), complement=True):
            out_count = self.bank[idx].apply(xi, y[idx])
            if all_samples:
                self.bank[idx].apply(z,  y[idx][out_count:])
        return back2dim(y, self.xdim)


def upfirdn(x, h, uprate=1, downrate=1, xdim=-1, hdim=-1, all_samples=True):
    """
    Upsample, FIR filter, and downsample a signal or array of signals.
    
    Parameters
    ----------
    x : array-like
        Input signal array.  May be multi-dimensional (ND).  The signals
        will be operated on along the "xdim" dimension of x.
    h : array-like
        FIR (finite-impulse response) filter coefficients array.  May be ND.
        The filters are along the "hdim" dimension of h.
    uprate : int, optional
        Upsampling rate. (default=1)
    downrate : int, optional
        Downsampling rate. (default=1)
    xdim : int, optional
        Dimension for "x" input signal array. (default=-1)
    hdim : int, optional
        Dimension for "h" coefficient array. (default=-1)
    all_samples : bool, optional
        If True, feeds in zeros after the input signal to "drain" the resampler
        and get all the non-zero samples.  (default=True)
        
    Returns
    -------
    y : float ndarray
        The output signal array.  The results of each upfirdn operation are
        along the "xdim" dimension; the array is discontinuous if xdim is not
        the last dimension.

    Notes
    -----
    The standard rules of broadcasting apply to the input ND arrays x and h,
    for those dimensions other than the "sample" dimension specified by
    xdim and hdim.  upfirdn operates along a single dimension, and
    supports multiple such operations for all the other dimensions using 
    broadcasting; this allows you to, for example, operate on multiple signal
    columns with a single filter, or apply multiple filters to a single signal.
    The uprate and downrate however are scalar and apply to ALL operations.
    
    In the case of ND, the most efficient choice of xdim is -1, that is, the
    last dimension (assuming C-style input x); otherwise each signal is copied
    prior to operating.
    
    Examples
    --------
    >>> upfirdn([1,1,1], [1,1,1])   # FIR filter
    array([ 1.,  2.,  3.,  2.,  1.])
    
    >>> upfirdn([1, 2, 3], [1], 3)  # upsampling with zeros insertion
    array([ 1.,  0.,  0.,  2.,  0.,  0.,  3.,  0.,  0.])
    
    >>> upfirdn([1,2,3], [1,1,1], 3)  # upsampling with sample-and-hold
    array([ 1.,  1.,  1.,  2.,  2.,  2.,  3.,  3.,  3.])
    
    >>> upfirdn([1,1,1], [.5,1,.5], 2)  # linear interpolation
    array([ 0.5,  1. ,  1. ,  1. ,  1. ,  1. ,  0.5,  0. ])
    
    >>> upfirdn(range(10), [1], 1, 3)  # decimation by 3
    array([ 0.,  3.,  6.,  9.])
    
    >>> upfirdn(range(10), [.5,1,.5], 2, 3)  # linear interpolation, rate 2/3
    array([ 0. ,  1. ,  2.5,  4. ,  5.5,  7. ,  8.5,  0. ])

    # Apply single filter to multiple signals
    >>> x = np.reshape(range(8), (4,2))
    array([[0, 1],
           [2, 3],
           [4, 5],
           [6, 7]])
    >>> h = [1, 1]
    >>> upfirdn(x, h, 2)   # apply along last dimension of x
    array([[ 0.,  0.,  1.,  1.],
           [ 2.,  2.,  3.,  3.],
           [ 4.,  4.,  5.,  5.],
           [ 6.,  6.,  7.,  7.]])
    >>> upfirdn(x, h, 2, xdim=0)  # apply along 0th dimension of x
    array([[ 0.,  1.],
           [ 0.,  1.],
           [ 2.,  3.],
           [ 2.,  3.],
           [ 4.,  5.],
           [ 4.,  5.],
           [ 6.,  7.],
           [ 6.,  7.]])

    """
    resampler_bank = ResamplerBank(x, h, uprate, downrate, xdim, hdim)
    return resampler_bank.apply(x, all_samples)


from numpy.testing import Tester
test = Tester().test
bench = Tester().bench
    

if __name__ == '__main__':
    h = np.ones((3,))
    x = np.random.randn(2,3,4)
    y = upfirdn(x, h, 3, 1, xdim=0)
    print y
    
