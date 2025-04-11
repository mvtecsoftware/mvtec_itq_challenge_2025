#ifndef CONFIG_H
#define CONFIG_H

#include <Servo.h>

//#define COMPILE_FOR_UNO // Whether to compile for Uno or for Mega

#define V_MAX 0.3 // Maximum velocity of the robot in m/s

// Motor structure
struct Motor {
    int dir_pin_1;
    int dir_pin_2;
    int pwm_pin;
    float velocity;
};

// Declare motor instances
extern Motor motor_right;
extern Motor motor_left;

// Declare servo instances
extern Servo servo_1;
extern Servo servo_2;
extern Servo servo_3;

#endif  // CONFIG_H

