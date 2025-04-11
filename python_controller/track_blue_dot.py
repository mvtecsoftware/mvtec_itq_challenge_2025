import halcon as ha
import os
import serial


if __name__ == "__main__":
    # program = ha.HDevProgram("~/MVTec-NaviGators/image_processing/blue_dot_detection.hdev")
    program = ha.HDevProgram("/home/makeathon/MVTec-NaviGators/image_processing/blue_dot_detection.hdev")

    init_procedure = ha.HDevProcedure.load_local(program, 'init_acq')
    init_proc_call = ha.HDevProcedureCall(init_procedure)
    init_proc_call.execute()
    acq_handle = init_proc_call.get_output_control_param_by_name("AcqHandle")

    ser = serial.Serial("/dev/ttyUSB0")  # open serial port
    print(ser.name)
    heart_beat: bool = True

    while(True):
        image = ha.grab_image_async(acq_handle, -1)
        # print(image)

        detect_cup_procedure = ha.HDevProcedure.load_local(program, 'detect_cup')
        detect_cup_proc_call = ha.HDevProcedureCall(detect_cup_procedure)
        detect_cup_proc_call.set_input_iconic_param_by_name('Image1', image)
        detect_cup_proc_call.execute()

        radius = detect_cup_proc_call.get_output_control_param_by_name('Radius')
        row = detect_cup_proc_call.get_output_control_param_by_name('Row')
        column = detect_cup_proc_call.get_output_control_param_by_name('Column')

        print("Radius: " + str(radius))
        print("Row: " + str(row))
        print("Column: " + str(column))

        if len(column) > 0:
            if column[0] < 780:
                command_left: str = ":ML=" + str(130) + "!"
                command_right: str = ":MR=" + str(180) + "!"
            elif column[0] > 820:
                command_left: str = ":ML=" + str(180) + "!"
                command_right: str = ":MR=" + str(130) + "!"
            else:
                command_left: str = ":ML=" + str(155) + "!"
                command_right: str = ":MR=" + str(155) + "!"
        else:
            command_left: str = ":ML=" + str(155) + "!"
            command_right: str = ":MR=" + str(155) + "!"

        command_heart_beat: str = ":WD=" + str(int(heart_beat)) + "!"
        ser.write(command_heart_beat.encode())
        ser.write(command_left.encode())
        ser.write(command_right.encode())
        heart_beat = not heart_beat

# def call_procedure():

#     program = ha.HDevProgram(os.path.join(PATH, 'python_hdevengine_example.hdev'))
#     procedure = ha.HDevProcedure.load_local(program, 'process_apples')

#     img = ha.read_image('Fotolia_45332982_S.jpg')

#     proc_call = ha.HDevProcedureCall(procedure)
#     proc_call.set_input_iconic_param_by_name('Image', img)
#     proc_call.execute()

#     region_closing = proc_call.get_output_iconic_param_by_name('RegionClosing')
#     area = proc_call.get_output_control_param_by_name('Area')
#     row = proc_call.get_output_control_param_by_name('Row')
#     column = proc_call.get_output_control_param_by_name('Column')

#     return region_closing, area, row, column


# if __name__ == '__main__':
#     # Call HDevelop Program
#     #region_closing, area, row, column = call_program()

#     # Call HDevelop Local Procedure
#     region_closing, area, row, column = call_procedure()

#     # Print results
#     print("Number of apples in image foreground:", len(area))
#     print("Apples pixel area: ", area)
#     print("Apples center row: ", row)
#     print("Apples center column: ", column)