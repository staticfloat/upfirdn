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
*/

#include "Resampler.h"

/*
this is an example of how you would call upfirdn in cpp without using python
To run, 
  g++ example.cpp
  ./a.out
*/

using namespace std;

int main()
{ 
    // First example, using pointer/count for inputs
    float x[]={1., 2., 3.};
    float h[]={1., 1., 1.};
    for (int i=0; i<3; ++i) {
        cout << "x[" << i << "]=" << x[i] << endl;
    }
    vector<float> y;
    upfirdn(3, 1, x, 3, h, 3, y);
    for (int i=0; i<y.size(); ++i) {
        cout << "y[" << i << "]=" << y[i] << endl;
    }

    // Second example, using vectors for inputs
    float x1[]={1., 2., 3., 4., 5., 6., 7., 8., 9., 10.};
    float h1[]={.25, .5, .75, 1, .75, .5, .25};
    vector<float> x1v;
    vector<float> h1v;
    x1v.assign(x1, x1+10);
    h1v.assign(h1, h1+7);
    vector<float> y1;
    upfirdn(4, 3, x1v, h1v, y1);
    for (int i=0; i<y1.size(); ++i) {
        cout << "y1[" << i << "]=" << y1[i] << endl;
    }

}
