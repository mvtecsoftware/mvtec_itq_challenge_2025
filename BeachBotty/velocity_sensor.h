#ifndef SENSOR_H
#define SENSOR_H

#include <Arduino.h>
#include "KickSort.h" // Include KickSort library

#define WINDOW_SIZE 5 // Number of past velocity values to store for filtering
#define HAMPEL_K 3.0 // Threshold multiplier for standard deviation filtering

class VelocitySensor {
public:
    VelocitySensor(int sensorPin1, int sensorPin2);
    void initialize();
    void sensor_ISR();
    void updateVelocity();
    
    volatile float velocity;
    int sensorPin1;
    int sensorPin2;

private:
    volatile unsigned long lastTime;
    const float radius = 2.7e-2;
    const int teeth = 16;
    
    // Hampel filter variables
    float velocityBuffer[WINDOW_SIZE];  
    int bufferIndex;
    
    void applyHampelFilter(float& newVelocity);
    float calculateMedian(float arr[], int size);
    float calculateMAD(float arr[], int size, float median);
};

#endif
