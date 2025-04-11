#ifndef SERIAL_COMMUNICATION_H
#define SERIAL_COMMUNICATION_H

#include <Arduino.h>
#include "config.h"
#include "velocity_sensor.h"
#include "sensor_actor.h"

extern VelocitySensor sensor_right;
extern VelocitySensor sensor_left;

// Watchdog variables
extern int watchdog_last_value;
extern int watchdog_current_value;
extern bool controlling_application_alive;
extern unsigned long last_wd_change;

// Function prototypes
void confirm_command();
void confirm_error();
void analyze_command();
void serial_communication_task();
float val_to_speed(int val);

#endif
