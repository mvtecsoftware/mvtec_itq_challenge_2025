import socket
import socket_source

# x - value mean digit
# Sxxx - speed set from 0 to 100
# Mx - mode of controller
# F - move forward in mode 1
# B - move backward in mode 1
# R - turn right in mode 1
# L - turn left in mode 1
# S - stop in mode 1
adress = socket_source.local_host_address
port = socket_source.controller_port

while True:
    user_input = input("Enter something: ")
    print("You entered:", user_input)

    # Create a new socket for each connection attempt
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((adress, port))  # Connect to the server
        client.sendall(user_input.encode())  # Send data
    except ConnectionRefusedError:
        print("Error: Could not connect to server. Make sure the server is running.")
    finally:
        client.close()  # Close the socket after sending the message
