import comunication
import time
import threading
import socket_source

communication_controller = comunication.Transceiver(socket_source.local_host_address, socket_source.controller_port)
communication_state = comunication.Receiver(socket_source.local_host_address, socket_source.state_port)
communication_remote = comunication.Receiver(socket_source.remote_host_address, socket_source.remote_port)

class Manager:
    def __init__(self
                 , search_object, remote_object):
        self.search = search_object
        self.remote = remote_object
        self.running = True

    def __del__(self):
        self.running = False

    def state_update(self):
        while self.running:
            if communication_state.data == "s":
                communication_controller.send_data("S")
                self.remote.remote_control = False
                self.search.searching = True
                print("Searching")

            elif communication_state.data == "f":
                communication_controller.send_data("S")
                self.search.i = 0
                self.search.searching = False
                self.remote.remote_control = False
                print("Found")

            elif communication_state.data == "r":
                communication_controller.send_data("S")
                self.search.searching = False
                self.remote.remote_control = True
                print("Remote")

            elif communication_state.data == "a":
                communication_controller.send_data("S")
                self.search.searching = False
                self.remote.remote_control = False
                print("Autonomous")

            communication_state.data = ""
            time.sleep(0.1)



class RemoteController:
    def __init__(self):
        self.remote_control = False
        self.running = True

    def __del__(self):
        self.running = False

    def control(self):
        while self.running:
            if self.remote_control:
                communication_controller.send_data(communication_remote.data)


class SearchAlgorithm:
    def __init__(self):
        communication_controller.send_data('M1')
        communication_controller.send_data('S60')
        self.searching = False
        self.running = True
        self.turning_time = 0.5
        self.forward_time = 1.0
        self.forward_speed = 50
        self.turning_speed = 100
        self.i = 0
        # [command, duration, speed]
        self.searching_command_list = [['F', self.forward_time, self.forward_speed],
                                       ['L', self.turning_time, self.turning_speed],
                                       ['F', self.forward_time, self.forward_speed],
                                       ['R', self.turning_time, self.turning_speed],
                                       ['F', self.forward_time, self.forward_speed],
                                       ['R', self.turning_time, self.turning_speed],
                                       ['F', self.forward_time, self.forward_speed],
                                       ['L', self.turning_time, self.turning_speed]]

    def __del__(self):
        self.running = False

    def search(self):
        while self.running:
            if self.searching:
                communication_controller.send_data('S' + str(self.searching_command_list[self.i][2]))
                self.interval_sender(self.searching_command_list[self.i][1], 0.05, self.searching_command_list[self.i][0])
                self.i+=1
                if self.i == len(self.searching_command_list):
                    self.i = 0



    def interval_sender(self, duration, interval, command):
        # Assuming communication_controller is already initialized
        start_time = time.time()  # Get the current time
        while (time.time() - start_time) < duration and self.searching:
            communication_controller.send_data(command)
            time.sleep(interval)  # Wait for 200 ms before sending again


search_algorithm = SearchAlgorithm()
remote = RemoteController()
manager = Manager(search_algorithm, remote)



remote_thread = threading.Thread(target=remote.control, daemon=True)
remote_thread.start()

search_thread = threading.Thread(target=search_algorithm.search, daemon=True)
search_thread.start()

# Start listening for incoming commands in a separate thread
manager_thread = threading.Thread(target=manager.state_update, daemon=True)
manager_thread.start()

communication_state_thread = threading.Thread(target=communication_state.listen, daemon=True)
communication_state_thread.start()

communication_remote_thread = threading.Thread(target=communication_remote.listen, daemon=True)
communication_remote_thread.start()
# Handle Ctrl+C gracefully
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    del communication_state
    del communication_remote
    del search_algorithm
    del manager
    print("\nCtrl+C detected. Exiting gracefully...")




