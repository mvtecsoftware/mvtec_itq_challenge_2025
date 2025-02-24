
#include <Servo.h>

// At the moment not actually attached to the robot
Servo servo_1;  // create servo object to control a servo
Servo servo_2;  // create servo object to control a servo

// Buffer for receiving serial port messages
#define BUFFER_SIZE 10
char in_buffer[BUFFER_SIZE];
int dest_index=0;

// Related to drive motors
struct Motor
{
  int dir_pin_1;
  int dir_pin_2;
  int pwm_pin;
};
Motor motor_right={3,4,2};
Motor motor_left={5,6,7};
int stearing=0;
int motor_power=0;

// Watchdog to detect if the application on the jetson nano is still communicating 
// and stop the motors if it is not
int watchdog_last_value=0;
int watchdog_current_value=0;
bool controlling_application_alive=false;
unsigned long last_wd_change=0;

/////////////////////////////////////////////////////////////////////
// Helper functions
/////////////////////////////////////////////////////////////////////

// Send confirmations messages through the secondary serial port
void confirm_command()
{
  Serial.write(&in_buffer[1],6);
  Serial.write(" OK\n");
}
// Send error messages through the secondary serial port
void confirm_error()
{
  Serial.write(&in_buffer[0],10);
  Serial.write(" NOK\n");
}

// Set outputs to drive the motors
// we adjust the speed by using pwm functionality.
// val is assumed to be between -155 and 155
void set_motor_power(Motor* motor,int val)
{
  if(val==0)
  {
    digitalWrite(motor->dir_pin_1, LOW);
    digitalWrite(motor->dir_pin_2, LOW);
    analogWrite(motor->pwm_pin,0);
  }
  else if(val>0)
  {
    if(!controlling_application_alive)
    {
      return;
    }
    digitalWrite(motor->dir_pin_1, HIGH);
    digitalWrite(motor->dir_pin_2, LOW);
    analogWrite(motor->pwm_pin,(abs(val)+100>255)?255:abs(val)+100);
  }
  else
  {
    if(!controlling_application_alive)
    {
      return;
    }
    digitalWrite(motor->dir_pin_1, LOW);
    digitalWrite(motor->dir_pin_2, HIGH);
    analogWrite(motor->pwm_pin,(abs(val)+100>255)?255:abs(val)+100);
  }

}

// Analyze the serial port buffer and determine which command was sent
// Very simple implementation, could be replaced by using a library for example
//
// Commands must be sent in the following format throught the serial port 
// :<Command>=<Value>!
// 
// Examples:
// :ML=512!  -> Motor left, maximum forward speed
// :ML=256!  -> Motor left, stop (speed =0)
// :ML=0!    -> Motor left, maximum backward speed
// Same is possible for motor right and so on
void analyze_command()
{
    int val=0;
    if(strncmp(&in_buffer[1],"MR=",3)==0)
    {
      // left motor
      val=atoi(&in_buffer[4]);
      val= val-155;
      set_motor_power(&motor_right,val);
      confirm_command();
      
    }
    else if (strncmp(&in_buffer[1],"ML=",3)==0)
    {
      // right motor
      val=atoi(&in_buffer[4]);
      val= val-155;
      set_motor_power(&motor_left,val);
      confirm_command();
    }
    else if (strncmp(&in_buffer[1],"S1=",3)==0)
    {
      // servo 1
      val=atoi(&in_buffer[4]);
      servo_1.write(val);
      confirm_command();
    }
    else if (strncmp(&in_buffer[1],"S2=",3)==0)
    {
      // servo 2
      val=atoi(&in_buffer[4]);
      servo_1.write(val);
      confirm_command();
    }
    else if (strncmp(&in_buffer[1],"WD=",3)==0)
    {
      // watchdog
      watchdog_current_value=atoi(&in_buffer[4]);
    }
    else
    {
        confirm_error();
    }
}

// Arduino setup function is executed once after power on
void setup() {
  // initialize both serial ports:
  Serial.begin(9600);
  Serial1.begin(9600);
  servo_1.attach(8);
  servo_2.attach(9);
  pinMode(2, OUTPUT); 
  pinMode(3, OUTPUT); 
  pinMode(4, OUTPUT); 
  pinMode(5, OUTPUT); 
  pinMode(6, OUTPUT); 
  pinMode(7, OUTPUT); 

  for(int i=0;i<BUFFER_SIZE;i++)
  {
    in_buffer[i]='\0';
  }
}

// Arduino main loop is executed continuously. There is no escape
void loop() {

  if (Serial1.available()>0) {
    // Commands must be sent in the following format throught the serial port 
    // :<Command>=<Value>!
    // 
    // Examples:
    // :ML=512!  -> Motor left, maximum forward speed
    // :ML=256!  -> Motor left, stop (speed =0)
    // :ML=0!    -> Motor left, maximum backward speed
    // Same is possible for motor right and so on
    int new_byte=Serial1.read();
    if(new_byte=='!')
    {
      //analyze received chars
      in_buffer[dest_index]=new_byte;
      if(in_buffer[0]==':')
      {
        //really analyze received chars
        analyze_command();
      }
      else
      {
        confirm_error();
      }
      dest_index=0;
    }
    else
    {
      if(dest_index < BUFFER_SIZE)
      {
        in_buffer[dest_index]=new_byte;  
        dest_index++;
      }
    }
  }

  // Check each loop if we are still receiving commands
  if(watchdog_current_value!=watchdog_last_value)
  {
    watchdog_last_value=watchdog_current_value;
    controlling_application_alive=true;
    last_wd_change=millis();
  }
  else
  {
    // no change... check how long is this already happenning 
    // and stop the motors if it is more than 500 ms ago that we detected any activity from the jetson side
    if(millis()-last_wd_change>500)
    {
      controlling_application_alive=false;
      // switch off motors explicitly
      set_motor_power(&motor_right,0);
      set_motor_power(&motor_left,0);
    }
  }
  
}
