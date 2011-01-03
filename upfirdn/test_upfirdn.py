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
import upfirdn

from nose.tools import assert_raises
import sys
import time

random_state = np.random.RandomState(17)

def tic():
    global tictime
    tictime = time.time()

def toc():
    global tictime
    return time.time() - tictime
    
def resample(x, h, p, q):
    """This is the 'slow' version of upsampling, FIR filtering, and
    downsampling."""
    X = np.zeros((len(x), p), x.dtype)
    X[:, 0] = x
    X.shape = (-1,)
    Y = np.convolve(h, X)
    y = Y[::q]
    return y

class ResamplerCase(object):
    """Test C++ Resampler object
    
    Mainly tests that "apply" outputs correct values and that 
    state-retention is correct.
    
    """
    
    def __init__(self, p, q, coefs):
        """
        A random signal input type is chosen (real or complex).
        Inputs:
          p - a single integer upsampling factor
          q - a single integer downsampling factor
          coefs - real or complex coefficients array
        """
        self.p = p
        self.q = q
        self.coefs = coefs
        self.output_type = float
        if random_state.rand()>.5:
            self.signal_type = complex
            self.output_type = complex
        else:
            self.signal_type = float
        if np.iscomplexobj(coefs):
            self.coef_type = complex
            self.output_type = complex
        else:
            self.coef_type = float
        self.klass = upfirdn.klass_lookup(self.signal_type(), self.coefs)
        
    def __str__(self):
        return 'ResamplerCase(%d, %d, %d, %s, %s)'%(self.p, self.q, \
              len(self.coefs), self.signal_type.__name__, \
              self.coef_type.__name__)
            
    def __call__(self):
        print self
        self.scrub(np.ones(100), 'ones')
        if self.signal_type == float:
            x = random_state.randn(1000)
        else:
            x = random_state.randn(1000) + 1.j*random_state.randn(1000)
        self.scrub(x, 'randn')
        self.scrub(np.arange(10000), 'ramp')
        resampler = self.klass(self.p, self.q, self.coefs)
        assert_raises(ValueError, resampler.apply, \
            np.ones(200), np.ones(1, dtype=self.output_type))
        
    def scrub(self, x, name):
        tic()
        yr = resample(x, self.coefs, self.p, self.q)
        resample_time = toc()
        out_count = np.ceil(float(self.p) / self.q * len(x))
        yr = yr[:out_count]
        
        for test in ['oneshot', 'persample', 'randomsteps']:
            tic()
            y = self.__getattribute__(test)(x, out_count)
            test_time = toc()
            nmse = np.sum(abs(y - yr)**2) / np.sum(abs(yr)**2)
            print '%10s(%5d) %12s nmse = %10f    %10fx' % \
                (name, len(x), test, nmse, resample_time/test_time)
            assert nmse < 1e-10
            
        

    def oneshot(self, x, out_count):
        self.resampler = self.klass(self.p, self.q, self.coefs)
        y = np.zeros((out_count,), dtype=self.output_type)
        actual_out_count = self.resampler.apply(x, y)
        return y

    def persample(self, x, out_count):
        self.resampler = self.klass(self.p, self.q, self.coefs)
        y = np.zeros((out_count,), dtype=self.output_type)
        out_ptr = 0
        for xi in x:
            count = self.resampler.apply([xi], y[out_ptr:])
            out_ptr += count
        return y

    def randomsteps(self, x, out_count):
        self.resampler = self.klass(self.p, self.q, self.coefs)
        y = np.zeros((out_count,), dtype=self.output_type)
        base_step_size = len(x) / float(40)
        in_ptr = 0
        out_ptr = 0
        while in_ptr < len(x):
            step = int(base_step_size + random_state.randint(100) + 1)
            count = self.resampler.apply(x[in_ptr:in_ptr+step], y[out_ptr:])
            in_ptr += step
            out_ptr += count
        return y


def random_array(shape):
    a = random_state.randn(*shape)
    if random_state.rand() > .5:
        a = a + 1.j*random_state.randn(*shape)
    return a

class UpfirdnNdCase(object):
    """
    Test that broadcasting is working as expected for upfirdn function.
    """
    def __init__(self, p, q):
        self.p = p
        self.q = q
        
    def __str__(self):
        return 'UpfirdnNdCase (%d, %d)'%(self.p, self.q)

    def __call__(self):
        print self
        ndims = random_state.randint(1,5)
        shape = tuple([random_state.randint(2, 5) for i in range(ndims)])

        xdim = random_state.randint(ndims+1)
        hdim = random_state.randint(ndims+1)

        coefCount = random_state.randint(10, 20)
        inCount = random_state.randint(50, 100)

        h_singleton = [random_state.randint(2) for s in shape]
        hshape = tuple(np.where(h_singleton, 1, shape))

        x_singleton = [random_state.randint(2) for s in shape]
        # Avoid singleton dims in both arrays at the same place
        x_singleton = np.where(np.array(h_singleton) & x_singleton, 0, x_singleton)
        xshape = tuple(np.where(x_singleton, 1, shape))

        h = random_array(hshape[:hdim] + (coefCount,) + hshape[hdim:])
        x = random_array(xshape[:xdim] + (inCount,) + xshape[xdim:])

        print '  xshape =', xshape, '(%s)'%x.dtype
        print '  hshape =', hshape, '(%s)'%h.dtype

        y = upfirdn.upfirdn(x, h, self.p, self.q, xdim=xdim, hdim=hdim)
        
        for idx, yi in upfirdn.enumdims(y, (xdim,), complement=True):
            x_idx = tuple(np.where(x_singleton, 0, idx))
            x_idx = x_idx[:xdim] + (range(inCount),) + x_idx[xdim:]
            xi = x[x_idx]

            h_idx = tuple(np.where(h_singleton, 0, idx))
            h_idx = h_idx[:hdim] + (range(coefCount),) + h_idx[hdim:]
            hi = h[h_idx]

            y_expected = upfirdn.upfirdn(xi, hi, self.p, self.q)
            #print idx, np.mean(abs(yi - y_expected)**2)
            assert np.allclose(yi, y_expected, 1e-10)

def random_coefs(max_n):
    """Returns random length vector of normal random variables,
    with a 50/50 chance of complex."""
    n = random_state.randint(max_n) + 1
    coefs = random_state.randn(n)
    if random_state.rand() > .5:
        coefs = coefs + 1.j*random_state.randn(n)
    return coefs

def test():
    yield ResamplerCase(1, 1, [1.]),
    yield ResamplerCase(3, 2, [1.]),
    yield ResamplerCase(2, 3, [1.]),
    for i in range(10):
        p = random_state.randint(200)+1
        q = random_state.randint(200)+1
        coefs = random_coefs(200)
        yield ResamplerCase(p, q, coefs),

    for i in range(10):
        p = random_state.randint(10)+1
        q = random_state.randint(200)+1
        coefs = random_coefs(200)
        yield ResamplerCase(p, q, coefs),

    for i in range(10):
        p = random_state.randint(200)+1
        q = random_state.randint(10)+1
        coefs = random_coefs(200)
        yield ResamplerCase(p, q, coefs),

    for i in range(20):
        p = random_state.randint(10)+1
        q = random_state.randint(10)+1
        yield UpfirdnNdCase(p, q),


if __name__ == '__main__':
    # Execute the test suite
    for t in test():
        t[0]()
