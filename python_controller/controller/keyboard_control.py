import keyboard
import comunication
import time
import socket_source

speed = 80

print("Press W/A/S/D to move, R to increase speed, F to decrease speed,  Q to quit.")


communication = comunication.Transceiver(socket_source.remote_host_address, socket_source.remote_port)
communication.send_data('S' + str(speed))

while True:
    # Forward
    if keyboard.is_pressed('r'):
        speed = speed + 5
        if speed > 100:
            speed = 100
        communication.send_data('S' + str(speed))
    if keyboard.is_pressed('f'):
        speed = speed - 5
        if speed < 0:
            speed = 0
        communication.send_data('S' + str(speed))

    if keyboard.is_pressed("w"):
        communication.send_data('F')

    # Backward
    elif keyboard.is_pressed("s"):
        communication.send_data('B')

    # Left
    elif keyboard.is_pressed("a"):
        communication.send_data('L')

    # Right
    elif keyboard.is_pressed("d"):
        communication.send_data('R')

    # Quit
    elif keyboard.is_pressed("q"):
        communication.send_data('S')
        print("Exiting...")
        break
    # Stop
    else:
        communication.send_data('S')

    time.sleep(0.02)
