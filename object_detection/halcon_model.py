import halcon as ha
import os
from loguru import logger
import ast
from dotenv import load_dotenv

load_dotenv()

DIRPATH = os.getenv("DIRPATH")
DLMODELPATH = os.getenv("DLMODELPATH")
DICTPATH = os.getenv("DICTPATH")
RUNTIME = os.getenv("RUNTIME")

def main():

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

    while True:
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
        # # logger.debug(f"{json_dict=}")
        #
        # result = []
        # if 'bbox_class_name' in json_dict and type(json_dict['bbox_class_name']) == list:
        #     print(json_dict)
        #     for i in range(len(json_dict['bbox_class_name'])):
        #         #x_center = (json_dict['bbox_col1'][i] + json_dict['bbox_col2'][i]) / 2
        #         x_center = (json_dict['bbox_col1'][i] + ((json_dict['bbox_col2'][i])-(json_dict['bbox_col1'][i]))/2)
        #         #y_center = (json_dict['bbox_row1'][i] + json_dict['bbox_row2'][i]) / 2
        #         y_center = (json_dict['bbox_row1'][i] + ((json_dict['bbox_row2'][i])-(json_dict['bbox_row1'][i]))/2)
        #         result.append([json_dict['bbox_class_name'][i], x_center,y_center])
        # elif 'bbox_class_name' in json_dict and type(json_dict['bbox_col1']) == float:
        #     x_center = json_dict['bbox_col1'] + ((json_dict['bbox_col2'] - json_dict['bbox_col1'])) / 2
        #     y_center = json_dict['bbox_row1'] + ((json_dict['bbox_row2'] - json_dict['bbox_row1'])) / 2
        #     result.append([json_dict['bbox_class_name'], x_center, y_center])

        logger.debug(f"{json_dict=}")

if __name__ == '__main__':

    main()