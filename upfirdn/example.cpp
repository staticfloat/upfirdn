/*
runUpfirdn function contributed by Lewis Anderson lkanders@ucsd.edu 
*/

float * runUpfirdn(float *input, int inLength, float *filter, int filterLength)
{
	// pad input by length of filter to flush all values out 
	float *inputPadded = new float[inLength + filterLength];
	for (int i = 0; i < inLength + filterLength; i++) {
		if (i < inLength)
			inputPadded[i] = input[i];
		else 
			inputPadded[i] = 0.0f;
	}
	
	// begin resampling/filtering
	Resampler<float, float, float> theResampler(1, 2, filter, filterLength);
	int resultsCount = theResampler.neededOutCount(inLength + filterLength);		// calc size of output
	
	float * results = new float[resultsCount]; // allocate results
        // run filtering
	int numSamplesComputed = theResampler.apply(inputPadded, inLength + filterLength, results, resultsCount); 
	delete[] inputPadded;
	
	return results;
}

