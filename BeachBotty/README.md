# Arduino Code

## Interrupts and Timer Usage

This project uses Timer2 to trigger an interrupt every 10 milliseconds. The interrupt is responsible for executing the `sensor_actor_task()`, which handles sensor readings and control outputs.

Timer2 is configured in CTC (Clear Timer on Compare Match) mode with a prescaler of 64. The compare match register (`OCR2A`) is set to 249, ensuring an interrupt is triggered every 10ms when running at 16MHz.

Global interrupts are enabled after configuring the timer to allow the execution of the interrupt service routine (ISR).

## Serial Communication

The project utilizes both `Serial` (default UART) and `Serial1` (secondary UART) for communication. `Serial.begin(9600)` initializes the default serial port, while `Serial1.begin(9600)` handles external communication.

Incoming commands are read from `Serial1` and stored in a buffer. Once a complete command is received (indicated by the `!` character), it is analyzed and executed accordingly. Commands control motor movements, watchdog signals, and other system operations.

A watchdog mechanism monitors the controlling application's activity. If no new watchdog signals are received within 500ms, the system assumes a failure and stops the motors for safety.

### Supported Serial Commands

- `:MR=<value>` - Sets right motor velocity (0-310)
- `:ML=<value>` - Sets left motor velocity (0-310)
- `:S1=<angle>` - Sets angle of servo 1
- `:S2=<angle>` - Sets angle of servo 2 (only on Mega)
- `:S3=<angle>` - Sets angle of servo 3 (only on Mega)
- `:WD=<value>` - Updates watchdog signal

## Motor Control

The project defines two motor objects (`motor_right` and `motor_left`) with associated direction and PWM control pins. Based on received commands, the motors are adjusted in speed and direction. If no valid commands are detected, the motors stop.

The system ensures proper motor control by applying safety constraints and preventing unintended movement when the controlling application is unresponsive.

The motor control mechanism includes:
- PI control loop to regulate motor velocity based on sensor feedback.
- Anti-windup protection for integral control.
- PWM output generation for speed control.

## Watchdog Mechanism

A watchdog mechanism tracks changes in received watchdog values. If the value remains unchanged for over 500ms, the system enters a failsafe mode, disabling motor movement. This prevents uncontrolled behavior if communication is lost.

If the watchdog value updates within the time frame, the system continues normal operation.

## Sensor and Velocity Measurement

The system includes velocity sensors for both left and right motors. Each sensor consists of:
- Two sensor pins (`sensorPin1`, `sensorPin2`) for quadrature encoding.
- Velocity calculation using timestamps from interrupts.
- Anti-glitch filtering via an optional Hampel filter.
- Gradual decay of velocity for smoothing.

Each sensor ISR measures the time between pulses and calculates velocity using the wheel radius and the number of encoder teeth. The calculated velocity is stored and optionally filtered to remove outliers.

The Hampel filter is implemented using:
- Median and Median Absolute Deviation (MAD) calculations.
- Outlier detection using a threshold factor (`HAMPEL_K`).
- Replacement of outliers with median values for smoother operation.

## Servo Control

The system supports servo control for one or more servos (depending on the board type). The servo angle is dynamically adjusted, oscillating between 5° and 130° to test movement and operation.

## Low-Pass Filter

A low-pass filter implementation is provided in `lowpass_filter.cpp` and `lowpass_filter.h`. This filter is designed to smooth out noisy signals using a second-order discrete-time filter. It is initialized with two parameters:
- `T_s`: The sampling time.
- `T_d`: The cutoff period that determines the filter's response time.

The filter uses a difference equation with precomputed coefficients to efficiently apply filtering to incoming data. It maintains a history of the last three input and output values to compute the next filtered value.

### Features of the Low-Pass Filter
- Second-order digital filter implementation.
- Precomputed coefficients for efficient filtering.
- History-based processing to maintain smooth output.
- First-pass initialization to ensure stable startup behavior.

**Note:** At the moment, `lowpass_filter.cpp` is not used anywhere in the project. It may be integrated in the future for processing sensor signals or refining control loops.

