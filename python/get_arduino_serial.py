import serial
import time

def main():
    con=serial.Serial('/dev/ttyACM0', 9600)
    print('connected.')
    while 1:
        str=con.readline() # byte code
        print (str.strip().decode('utf-8')) # decoded string

if __name__ == '__main__':
    main()