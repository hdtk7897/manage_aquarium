import serial
import traceback
import time

class USBSerial:
    def __init__(self, path):
        try:
            self.serialport = serial.Serial(
                port=path,
                baudrate=19200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.5,
            )
        except serial.SerialException:
            print('error')
            print(traceback.format_exc())

        self.serialport.reset_input_buffer()
        self.serialport.reset_output_buffer()
        time.sleep(1)

    def send_serial(self, cmd):
        print("send data : {0}".format(cmd))
        try:
            cmd.rstrip()
            self.serialport.write((cmd + "\n").encode("utf-8"))
        except serial.SerialException:
            print(traceback.format_exc())

    def receive_serial(self):
        try:
            rcvdata = self.serialport.readline()
        except serial.SerialException:
            print(traceback.format_exc())
        return rcvdata.decode("utf-8").rstrip()

if __name__ == '__main__':
    path = "/dev/ttyACM0" 
    uno = USBSerial(path)
    while True:
        input_data = input("input data:")
        uno.send_serial(input_data)
        data = uno.receive_serial()
        print("recv data : {0}".format(data))
        
