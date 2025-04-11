import serial

ser = serial.Serial("/dev/ttyUSB0")  # open serial port
print(ser.name)

chain_velocity: int = 200

heart_beat: bool = True

command_left: str = ":ML=" + str(chain_velocity) + "!"
command_right: str = ":MR=" + str(chain_velocity) + "!"

while(1):
    command_heart_beat: str = ":WD=" + str(int(heart_beat)) + "!"
    ser.write(command_heart_beat.encode())
    ser.write(command_left.encode())
    ser.write(command_right.encode())
    heart_beat = not heart_beat
