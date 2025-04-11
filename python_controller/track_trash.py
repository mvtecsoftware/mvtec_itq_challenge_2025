import halcon as ha
import os
from loguru import logger
import ast
from dotenv import load_dotenv
import serial
import math
import controller.comunication as communication

ip_address = '127.0.0.1'
port_controller = 3000
port_status = 5001

load_dotenv()

DIRPATH = os.getenv("DIRPATH")
DLMODELPATH = os.getenv("DLMODELPATH")
DICTPATH = os.getenv("DICTPATH")
RUNTIME = os.getenv("RUNTIME")

def get_trash_positions():

    # load program from path
    program = ha.HDevProgram(os.path.join(DIRPATH, 'Halcon_Programm_Detection.hdev'))

    # call init_detection procedure with all parameters needed
    init_detection_procedure = ha.HDevProcedure.load_local(program, 'init_detection')

    proc_call = ha.HDevProcedureCall(init_detection_procedure)
    proc_call.set_input_control_param_by_name('DLModelPath', DLMODELPATH)
    proc_call.set_input_control_param_by_name('DictPath', DICTPATH)
    proc_call.set_input_control_param_by_name('MinConfidence', 0.5)
    proc_call.set_input_control_param_by_name('MaxOverlap', 0.5)
    proc_call.set_input_control_param_by_name('MaxOverlapClassAgnostic', 0.5)
    proc_call.execute()

    # read init_detection output
    dl_model_handle = proc_call.get_output_control_param_by_name('DLModelHandle')
    dict_handle = proc_call.get_output_control_param_by_name('DictHandle')

    # call init_camera procedure
    init_camera_procedure = ha.HDevProcedure.load_local(program, 'init_camera')
    proc_call = ha.HDevProcedureCall(init_camera_procedure)
    proc_call.execute()

    # read _init_camera output
    acq_handle = proc_call.get_output_control_param_by_name('AcqHandle')

    # set dl parameters (cpu/gpu)
    set_dl_device_procedure = ha.HDevProcedure.load_local(program, 'set_dl_device')

    proc_call = ha.HDevProcedureCall(set_dl_device_procedure)
    proc_call.set_input_control_param_by_name('runtime', RUNTIME)
    proc_call.set_input_control_param_by_name('DLModelHandle', dl_model_handle)
    proc_call.execute()
    dl_device_handle = proc_call.get_output_control_param_by_name('DLDeviceHandles')

    # call detect_objects procedure
    detect_objects_procedure = ha.HDevProcedure.load_local(program, 'detect_objects')
    proc_call = ha.HDevProcedureCall(detect_objects_procedure)
    proc_call.set_input_control_param_by_name('AcqHandle', acq_handle)
    proc_call.set_input_control_param_by_name('DictHandle', dict_handle)
    proc_call.set_input_control_param_by_name('DLModelHandle', dl_model_handle)
    proc_call.execute()
    dl_result = proc_call.get_output_control_param_by_name('DLResult')
    json_dict = proc_call.get_output_control_param_by_name('JsonString')

    json_dict = ast.literal_eval(json_dict[0])
    logger.debug(f"{json_dict=}")


    target_x_value = 0.0
    target_y_value = 0.0
    if 'world_y' in json_dict and 'world_x' in json_dict and type(json_dict['world_x']) == list:
        x_positions = json_dict['world_x']
        y_positions = json_dict['world_y']

        smallest_y_value = sorted(y_positions)[0]
        index_of_smallest_y_value = y_positions.index(smallest_y_value)

        target_y_value = smallest_y_value
        target_x_value = x_positions[index_of_smallest_y_value]

    elif 'world_y' in json_dict and 'world_x' in json_dict and type(json_dict['world_x']) == float:
        target_y_value = json_dict['world_x']
        target_x_value = json_dict['world_y']

    else:
        return None, None

    # print(target_x_value)
    # print(target_y_value)

    # Add another 0.25m to the y distance
    # The camera detects all objects in a coordinate system in front of the robot
    # The origin of the CS is aroung 0.10m in front of the robot and the center of the robot adds another 0.15m
    target_y_value = target_y_value + 0.25 
    
    angle_diff = math.atan2(target_x_value, target_y_value)
    angle_degree = math.degrees(angle_diff)
    distance = pow(pow(target_x_value, 2) + pow(target_y_value, 2), 0.5)

    return angle_diff, distance


if __name__ == '__main__':
    communication_controller = communication.Transceiver(ip_address, port_controller)
    communication_status = communication.Transceiver(ip_address, port_status)
    detect = False
    while True:
        angle, distance = get_trash_positions()

        if angle is not None and distance is not None:
            if not detect:
                communication_status.send_data("f")
                communication_controller.send_data("M6")
            communication_controller.send_data("A" + str(angle*100))
            communication_controller.send_data("D" + str(distance*100))

        # sorted_data_by_nearest = sorted(result, key=lambda item: item[2], reverse=True)
        
        # target = sorted_data_by_nearest[0]
        # print(sorted_data_by_nearest)
        # print(target)