#include <Arduino.h>
#include <Servo.h>
#include "sensor_actor.h"
#include "config.h"
#include "velocity_sensor.h"

// Parameters for controller
float controller_params[] = {1.0, 1.0}; // P and I values for PI controllers
float controller_i_value_left = 0.0;
float controller_i_value_right = 0.0;
float servo_dir = 1.0;

// Read data from sensors and compute / apply control outputs
void sensor_actor_task() {

    // Compute control outputs
    float control_error_left = motor_left.velocity - sensor_left.velocity;
    controller_i_value_left += controller_params[1]*0.01*control_error_left;
    controller_i_value_left = controller_i_value_left > V_MAX ? V_MAX : controller_i_value_left; // Anti-windup
    controller_i_value_left = controller_i_value_left < -V_MAX ? -V_MAX : controller_i_value_left;
    float control_output_left = controller_params[0]*control_error_left + controller_i_value_left;
    
    float control_error_right = motor_right.velocity - sensor_right.velocity;
    controller_i_value_right += controller_params[1]*0.01*control_error_right;
    controller_i_value_right = controller_i_value_right > V_MAX ? V_MAX : controller_i_value_right;
    controller_i_value_right = controller_i_value_right < -V_MAX ? -V_MAX : controller_i_value_right;
    float control_output_right = controller_params[0]*control_error_right + controller_i_value_right;

    control_output_left = motor_left.velocity;
    control_output_right = motor_right.velocity;

    // Decay velocities
    sensor_right.updateVelocity();
    sensor_left.updateVelocity();

    // Print velocity
    /*test_counter += 1;
    if(test_counter % 1000 == 0){
      Serial.print("right: ");
      Serial.println(motor_right.velocity, 10);
      Serial.print(",left: ");
      Serial.print(motor_left.velocity, 10);
    }*/

    // Set motor outputs
    set_motor_outputs(&motor_left, control_output_left);
    set_motor_outputs(&motor_right, control_output_right);

    // Set angle of servo 1
    if(angle_servo_1 > 130){
      servo_dir = -1;
    }else if(angle_servo_1 < 5){
      servo_dir = 1;
    }
    angle_servo_1 += servo_dir*0.5;
    servo_1.write(angle_servo_1);
}

void set_motor_outputs(Motor* motor, float control_output){
    int pwm_val = speed_to_pwm(control_output);
    //Serial.println(pwm_val);
    if (pwm_val == 0) {
        digitalWrite(motor->dir_pin_1, LOW);
        digitalWrite(motor->dir_pin_2, LOW);
        analogWrite(motor->pwm_pin, 0);
    } else if (pwm_val > 0) {
        digitalWrite(motor->dir_pin_1, HIGH);
        digitalWrite(motor->dir_pin_2, LOW);
        analogWrite(motor->pwm_pin, abs(pwm_val));
    } else {
        digitalWrite(motor->dir_pin_1, LOW);
        digitalWrite(motor->dir_pin_2, HIGH);
        analogWrite(motor->pwm_pin, abs(pwm_val));
    }
}

int speed_to_pwm(float speed){
  int pwm_val = round(-254.0 + 508.0 * (speed + V_MAX) / (2*V_MAX));
  pwm_val = (pwm_val > 254) ? 254 : pwm_val;
  pwm_val = (pwm_val < -254) ? -254 : pwm_val;
  return pwm_val;
}