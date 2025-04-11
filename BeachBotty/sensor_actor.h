#ifndef SERIAL_COMMUNICATION_H
#define SERIAL_COMMUNICATION_H

#include <Arduino.h>
#include <Servo.h>
#include "config.h"
#include "velocity_sensor.h"

// Parameters for controller
extern float controller_params[];

extern VelocitySensor sensor_right;
extern VelocitySensor sensor_left;

extern float angle_servo_1;

// Function prototypes
void sensor_right_isr();
void sensor_left_isr();
void sensor_actor_task();
void set_motor_outputs(Motor* motor, float control_output);
int speed_to_pwm(float speed);

#endif
