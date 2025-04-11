from enum import Enum
from time import time
import serial

class DriveState(Enum):
    INIT = 0
    ZIG = 1
    ZAG = 2
    TURN_LEFT = 3
    TURN_RIGHT = 4
    SHORT_MOVE = 5

def send_drive_command(serial_con: serial.Serial, v_left: float, v_right: float):
    command_left: str = ":ML=" + str(v_left) + "!"
    command_right: str = ":MR=" + str(v_right) + "!"
    serial_con.write(command_left.encode())
    serial_con.write(command_right.encode())

def send_heart_beat(serial_con: serial.Serial, heart_beat: bool):
    command_heart_beat: str = ":WD=" + str(int(heart_beat)) + "!"
    serial_con.write(command_heart_beat.encode())

if __name__ == "__main__":
    ser = serial.Serial("/dev/ttyUSB0")  # open serial port
    print(ser.name)
    heart_beat: bool = True

    last_state: DriveState = DriveState.INIT
    current_state: DriveState = DriveState.INIT

    trans_velocity: float = 0.8 * 155
    turning_velocity: float = 0.5 * 155

    zig_move_time: float = 3.0 * 10**9
    zag_move_time: float = 3.0 * 10**9
    short_move_time: float = 1.0 * 10**9
    turn_left_time: float = 0.8 * 10**9
    turn_right_time: float = 0.8 * 10**9

    finished: bool = False
    while not finished:
        # Send Heartbeat and reverse boolean
        send_heart_beat(ser, heart_beat)
        heart_beat = not heart_beat

        if current_state == DriveState.INIT:
            start_time_movement = time.time_ns()
            last_state = DriveState.INIT
            current_state = DriveState.ZIG
        elif current_state == DriveState.ZIG:
            send_drive_command(ser, 155 + trans_velocity, 155 + trans_velocity)
            if time.time_ns() - start_time_movement > zig_move_time:
                start_time_movement = time.time_ns()
                last_state = DriveState.ZIG
                current_state = DriveState.TURN_LEFT
        elif current_state == DriveState.ZAG:
            send_drive_command(ser, 155 + trans_velocity, 155 + trans_velocity)
            if time.time_ns() - start_time_movement > zag_move_time:
                start_time_movement = time.time_ns()
                last_state = DriveState.ZAG
                current_state = DriveState.TURN_RIGHT
        elif current_state == DriveState.TURN_LEFT:
            send_drive_command(ser, 155 - turning_velocity, 155 + turning_velocity)
            if time.time_ns() - start_time_movement > turn_left_time:
                start_time_movement = time.time_ns()
                if last_state == DriveState.ZIG:
                    last_state = DriveState.TURN_LEFT
                    current_state = DriveState.SHORT_MOVE
                if last_state == DriveState.SHORT_MOVE:
                    last_state = DriveState.TURN_LEFT
                    current_state = DriveState.ZAG
        elif current_state == DriveState.TURN_RIGHT:
            send_drive_command(ser, 155 + turning_velocity, 155 - turning_velocity)
            if time.time_ns() - start_time_movement > turn_right_time:
                start_time_movement = time.time_ns()
                if last_state == DriveState.ZAG:
                    last_state = DriveState.TURN_RIGHT
                    current_state = DriveState.SHORT_MOVE
                if last_state == DriveState.SHORT_MOVE:
                    last_state = DriveState.TURN_RIGHT
                    current_state = DriveState.ZIG
        elif current_state == DriveState.SHORT_MOVE:
            send_drive_command(ser, 155 + trans_velocity, 155 + trans_velocity)
            if time.time_ns() - start_time_movement > short_move_time:
                start_time_movement = time.time_ns()
                if last_state == DriveState.TURN_LEFT:
                    last_state = DriveState.SHORT_MOVE
                    current_state = DriveState.TURN_LEFT
                elif last_state == DriveState.TURN_RIGHT:
                    last_state = DriveState.SHORT_MOVE
                    current_state = DriveState.TURN_RIGHT
