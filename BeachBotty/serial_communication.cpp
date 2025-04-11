#include <Arduino.h>
#include "serial_communication.h"
#include "config.h"
#include "sensor_actor.h"

int dest_index = 0;

// Watchdog variables
int watchdog_last_value = 0;
int watchdog_current_value = 0;
bool controlling_application_alive = false;
unsigned long last_wd_change = 0;

void confirm_command() {
    Serial.write(" OK\n");
}

void confirm_error() {
    Serial.write(" NOK\n");
}

void analyze_command(String in_buffer) {
    int val = 0;
    if (strncmp(&in_buffer[1], "MR=", 3) == 0) {
        val = atoi(&in_buffer[4]);
        val = (val > 310) ? 310 : val;
        val = (val < 0) ? 0 : val;
        motor_right.velocity = val_to_speed(val);
        confirm_command();
    } else if (strncmp(&in_buffer[1], "ML=", 3) == 0) {
        val = atoi(&in_buffer[4]);
        val = (val > 310) ? 310 : val;
        val = (val < 0) ? 0 : val;
        motor_left.velocity = val_to_speed(val);
        confirm_command();
    } else if (strncmp(&in_buffer[1], "S1=", 3) == 0) {
        float angle = atof(&in_buffer[4]);
        servo_1.write(angle);
        confirm_command();
    }
    #ifndef COMPILE_FOR_UNO
    else if (strncmp(&in_buffer[1], "S2=", 3) == 0) {
        float angle = atof(&in_buffer[4]);
        servo_2.write(angle);
        confirm_command();
    } else if (strncmp(&in_buffer[1], "S3=", 3) == 0) {
        float angle = atof(&in_buffer[4]);
        servo_3.write(angle);
        confirm_command();
    }
    #endif
    else if (strncmp(&in_buffer[1], "WD=", 3) == 0) {
        watchdog_current_value = atoi(&in_buffer[4]);
    } else {
        confirm_error();
    }
}

float val_to_speed(int val) {
  return -V_MAX + (2*V_MAX) * val / 310;
}

void serial_communication_task() {
    // Test broken pin
    //Serial.println(analogRead(sensor_right.sensorPin2));

    // Print velocity
    #ifndef COMPILE_FOR_UNO
    Serial1.print(sensor_right.velocity, 5);
    Serial1.print(",");
    Serial1.println(sensor_left.velocity, 5);
    #endif
    Serial.print(sensor_right.velocity, 5);
    Serial.print(",");
    Serial.println(sensor_left.velocity, 5);

    // Process commands from Serial
    while (Serial.available()) {
        String line = Serial.readStringUntil('\n'); // Read until '\n'
        line.trim(); // Remove any leading/trailing whitespace

        if (line.length() > 0 && line[0] == ':') {  
            analyze_command(line); // Process command if valid
        }
    }

    #ifndef COMPILE_FOR_UNO
    // Process commands from Serial1
    while (Serial1.available()) {
        String line = Serial1.readStringUntil('\n'); // Read until '\n'
        line.trim(); // Remove any leading/trailing whitespace

        if (line.length() > 0 && line[0] == ':') {  
            analyze_command(line); // Process command if valid
        }
    }
    #endif

    // Watchdog
    if (watchdog_current_value != watchdog_last_value) {
        watchdog_last_value = watchdog_current_value;
        controlling_application_alive = true;
        last_wd_change = millis();
    } else {
        if (millis() - last_wd_change > 500) {
            controlling_application_alive = false;
            // motor_left.velocity = 0.0;
            // motor_right.velocity = 0.0;
        }
    }
}
