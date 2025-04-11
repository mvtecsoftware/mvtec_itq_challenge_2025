#ifndef LOWPASSFILTER_H
#define LOWPASSFILTER_H

#include "config.h"

class LowpassFilter {
public:
    LowpassFilter(float T_s = 1.0, float T_d = 20.0);  // Constructor with default values
    float apply(float in_val);  // Method to apply the filter on a new input value

private:
    float num_coeffs[3];  // Numerator coefficients
    float den_coeffs[3];  // Denominator coefficients
    float num_values[3];  // Values for the numerator calculation
    float den_values[2];  // Values for the denominator calculation
    bool first_pass;      // Flag for the first pass to initialize values
};

#endif
