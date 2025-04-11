#include <Arduino.h>
#include <Servo.h>
#include "serial_communication.h"
#include "sensor_actor.h"
#include "lowpass_filter.h"
#include "config.h"

// Instantiate servos
#ifndef COMPILE_FOR_UNO
// On Mega create instances for all servos
Servo servo_1;
Servo servo_2;
Servo servo_3;
float angle_servo_1 = 0.0;
float angle_servo_2 = 0.0;
float angle_servo_3 = 0.0;
#else
// On Uno only create an instance for a single test servo
Servo servo_1;
float angle_servo_1 = 0.0;
#endif

// Define motors (pwm_pin for wach motor must support PWM)
Motor motor_right = {3, 4, 2, 0.0};
Motor motor_left = {5, 6, 7, 0.0};

// Define velocity sensors (pin 1 for each sensor must support hardware interrupts)
VelocitySensor sensor_right(20, A0);
VelocitySensor sensor_left(21, A1);

// Define ISRs for velocity sensors (need to be static functions, therefore methods of objects can't be used directly)
void sensor_right_isr(){
  sensor_right.sensor_ISR();
}
void sensor_left_isr(){
  sensor_left.sensor_ISR();
}

// Placeholder functions
void sensor_actor_task();

// ISR for sensor actor task (timer 2 has 8 bit couter for both Mega and Uno)
ISR(TIMER2_COMPA_vect) {
    sensor_actor_task();
}


// Timer setup
void setupTimers() {
    cli(); // Disable global interrupts

    TCCR2A = 0;
    TCCR2B = 0;
    TCNT2 = 0;
    OCR2A = 255; // Maximum value for longest period possible (16.384ms)
    TCCR2A |= (1 << WGM21); // CTC Mode
    TCCR2B |= (1 << CS22) | (1 << CS21) | (1 << CS20); // Prescaler 1024
    TIMSK2 |= (1 << OCIE2A); // Enable Timer2 Compare Match Interrupt

    sei(); // Enable global interrupts
}


// Setup function
void setup() {
  // initialize serial ports:
  Serial.begin(9600); // for debugging via USB
  #ifndef COMPILE_FOR_UNO
  Serial1.begin(9600); // For communicating with NVIDIA shield
  #endif

  // Pin setup
  #ifndef COMPILE_FOR_UNO
  // Pins for H-bridges
  pinMode(2, OUTPUT); 
  pinMode(3, OUTPUT); 
  pinMode(4, OUTPUT); 
  pinMode(5, OUTPUT); 
  pinMode(6, OUTPUT); 
  pinMode(7, OUTPUT);
  // Attach servos
  servo_1.attach(8);
  servo_2.attach(9);
  servo_3.attach(10);
  // Attach ISRs
  pinMode(sensor_left.sensorPin1,INPUT); // Probably unnecessary
  pinMode(sensor_left.sensorPin2,INPUT); // Probably unnecessary
  pinMode(sensor_right.sensorPin1,INPUT); // Probably unnecessary
  pinMode(sensor_right.sensorPin2,INPUT); // Probably unnecessary
  attachInterrupt(digitalPinToInterrupt(sensor_right.sensorPin1), sensor_right_isr, RISING);
  attachInterrupt(digitalPinToInterrupt(sensor_left.sensorPin1), sensor_left_isr, RISING);
  #else
  // Attach servo
  servo_1.attach(8);
  // Attach ISRs
  attachInterrupt(digitalPinToInterrupt(sensor_right.sensorPin1), sensor_right_isr, RISING);
  attachInterrupt(digitalPinToInterrupt(sensor_left.sensorPin1), sensor_left_isr, RISING);
  
  #endif

  setupTimers();
}

void loop() {
    // Execute serial communication task continuously
    serial_communication_task();
    delay(100); // Slowdown is unnecessary, if the receiver can handle high frequency of messages
}



