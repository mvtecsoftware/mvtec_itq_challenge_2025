#include "velocity_sensor.h"
#include "config.h"

VelocitySensor::VelocitySensor(int sensorPin1, int sensorPin2) 
    : sensorPin1(sensorPin1), sensorPin2(sensorPin2), velocity(0.0), lastTime(0), bufferIndex(0) {
    // Initialize velocity buffer with zeros
    for (int i = 0; i < WINDOW_SIZE; i++) {
        velocityBuffer[i] = 0.0;
    }
}

void VelocitySensor::initialize() {
    pinMode(sensorPin1, INPUT);
    pinMode(sensorPin2, INPUT);
}

void VelocitySensor::sensor_ISR() {
    unsigned long currentTime = micros();
    unsigned long deltaTime = currentTime - lastTime;
    lastTime = currentTime;

    if (deltaTime > 0) {
        float newVelocity = 2 * M_PI * radius / (deltaTime * teeth) * 1e6; // Factor 1e6 because deltaTime is in microseconds

        if (digitalRead(sensorPin2) == HIGH) {
            newVelocity = -newVelocity;  // Forward
        }

        //Clip to -V_MAX...V_MAX
        newVelocity = (newVelocity > V_MAX) ? V_MAX : newVelocity;
        newVelocity = (newVelocity < -V_MAX) ? -V_MAX : newVelocity;

        // Optionally apply Hampel filter
        //applyHampelFilter(newVelocity);
        velocity = newVelocity;
    }
}

void VelocitySensor::updateVelocity() {
    velocity *= 0.98; // Gradually reduce velocity
}

// ---- Hampel Filter Implementation ----

// Helper function to compute median using KickSort (must be installed via Arduino IDE)
float VelocitySensor::calculateMedian(float arr[], int size) {
    float sorted[size];
    memcpy(sorted, arr, size * sizeof(float));

    // Use KickSort for sorting
    KickSort<float>::quickSort(sorted, size);

    return (size % 2 == 0) ? (sorted[size / 2 - 1] + sorted[size / 2]) / 2.0 : sorted[size / 2];
}

// Helper function to compute Median Absolute Deviation (MAD)
float VelocitySensor::calculateMAD(float arr[], int size, float median) {
    float deviations[size];
    for (int i = 0; i < size; i++) {
        deviations[i] = fabs(arr[i] - median);
    }

    // Use KickSort for sorting
    KickSort<float>::quickSort(deviations, size);

    return calculateMedian(deviations, size);
}

// Hampel filter for glitch detection
void VelocitySensor::applyHampelFilter(float& newVelocity) {
    // Store new value in buffer
    velocityBuffer[bufferIndex] = newVelocity;
    bufferIndex = (bufferIndex + 1) % WINDOW_SIZE;

    // Calculate median and MAD of buffer
    float median = calculateMedian(velocityBuffer, WINDOW_SIZE);
    float mad = calculateMAD(velocityBuffer, WINDOW_SIZE, median);
    float threshold = HAMPEL_K * mad;

    // If the new value is an outlier, replace it with the median
    if (fabs(newVelocity - median) > threshold) {
        newVelocity = median;
    }
}
