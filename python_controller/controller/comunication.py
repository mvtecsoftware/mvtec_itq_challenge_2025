import socket

class Transceiver:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


    def send_data(self, data):
        # Create a new socket for each connection attempt
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect((self.ip, self.port))  # Connect to the server
            client.sendall(data.encode())  # Send data
        except ConnectionRefusedError:
            print("Error: Could not connect to server. Make sure the server is running.")
        finally:
            client.close()  # Close the socket after sending the message

class ReceiverController:
    def __init__(self, ip, port, controller):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(1)
        self.controller = controller
        self.running = True

    def __del__(self):
        print("Server stopped.")
        self.soft_kill()


    def listen(self):
        while self.running:
            self.conn, self.addr = self.server.accept()
            data = self.conn.recv(1024).decode()
            self.conn.close()
            self.data_recognition_controller(data)

    def soft_kill(self):
        self.running = False
        self.conn.close()


    def data_recognition_controller(self, data):
        try:
            if data[0] == "M":
                self.controller.set_mode(int(data[1]))

            elif data[0] == "S":
                if len(data) == 1:
                    self.controller.go_stop()
                else:
                    self.controller.set_speed(int(data[1:4]))
                return

            if self.controller.mode == 1:
                if data[0] == "F":
                    self.controller.go_forward()
                    return
                elif data[0] == "B":
                    self.controller.go_back()
                    return
                elif data[0] == "R":
                    self.controller.go_right()
                    return
                elif data[0] == "L":
                    self.controller.go_left()
                    return

            elif self.controller.mode == 4:
                if data[0] == "E":
                    self.controller.error_update(int(data[1:]))
                if data[0] == "P":
                    self.controller.follower.set_Pgain(int(data[1:]))

            elif self.controller.mode == 5:
                if data[0] == "R":
                    self.controller.odometry_test()

            elif self.controller.mode == 6:
                # angle
                if data[0] == "A":
                    self.controller.differential.set_angle(int(data[1:]))
                    self.controller.odometry_reset()

                # distance
                elif data[0] == "D":
                    self.controller.differential.set_distance(int(data[1:]))
                    self.controller.odometry_reset()

                # linear gain
                elif data[0] == "P":
                    self.controller.differential.set_gain_linear(int(data[1:]))

                # angle gain
                elif data[0] == "L":
                    self.controller.differential.set_gain_angular(int(data[1:]))
            else:
                print("Unknown command")
        except Exception as e:
            print("Message error:", data, "Error:", str(e))

class Receiver:
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(1)
        self.running = True
        self.data = ""


    def __del__(self):
        print("Server stopped.")
        self.soft_kill()

    def listen(self):
        while self.running:
            self.conn, self.addr = self.server.accept()
            self.data = self.conn.recv(1024).decode()
            self.conn.close()

    def soft_kill(self):
        self.running = False
        self.conn.close()

