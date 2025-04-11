#include "lowpass_filter.h"
#include <math.h>  // For mathematical operations like pi
#include "config.h"

LowpassFilter::LowpassFilter(float T_s, float T_d) : first_pass(true) {
    float w_0 = 2 * M_PI / T_d;  // Angular frequency

    // Coefficients for the numerator and denominator
    num_coeffs[0] = w_0 * w_0 * T_s * T_s;
    num_coeffs[1] = 2 * w_0 * w_0 * T_s * T_s;
    num_coeffs[2] = w_0 * w_0 * T_s * T_s;

    den_coeffs[0] = w_0 * w_0 * T_s * T_s + 4 * w_0 * T_s + 4;
    den_coeffs[1] = 2 * w_0 * w_0 * T_s * T_s - 8;
    den_coeffs[2] = w_0 * w_0 * T_s * T_s - 4 * w_0 * T_s + 4;

    // Initialize the history values
    for (int i = 0; i < 3; i++) {
        num_values[i] = 1.0;
        if (i < 2) {
            den_values[i] = 1.0;
        }
    }
}

float LowpassFilter::apply(float in_val) {
    if (first_pass) {
        for (int i = 0; i < 3; i++) {
            num_values[i] *= in_val;
            if (i < 2) {
                den_values[i] *= in_val;
            }
        }
        first_pass = false;
    }

    // Shift values in the history arrays
    for (int i = 2; i > 0; i--) {
        num_values[i] = num_values[i - 1];
    }
    num_values[0] = in_val;

    // Calculate the filtered output value
    float out_val = (num_coeffs[0] * num_values[0] + num_coeffs[1] * num_values[1] + num_coeffs[2] * num_values[2] -
                     den_coeffs[1] * den_values[0] - den_coeffs[2] * den_values[1]) / den_coeffs[0];

    // Shift denominator values
    for (int i = 1; i > 0; i--) {
        den_values[i] = den_values[i - 1];
    }
    den_values[0] = out_val;

    return out_val;
}
