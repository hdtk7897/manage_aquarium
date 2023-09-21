#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import smbus
import subprocess
import datetime
import requests
import pprint
import serial
import re
import RPi.GPIO as GPIO
import sqlite3
import json

# 温湿度計
i2c = smbus.SMBus(1)
address = 0x5c

# 水温計
SENSOR_ID = "28-3c1b04572da2"
SENSOR_W1_SLAVE = "/sys/bus/w1/devices/" + SENSOR_ID + "/w1_slave"
ERR_VAL = 85000
TEMP_WARN = 28.0

# ファン
FAN_ON = 26.5
FAN_OFF = 25.0
GPIO_FAN = 17

# ph
ARDUINO_CON=serial.Serial('/dev/ttyACM0', 9600)

# 出力
OUTPUT_DIR = "/home/pi/log"
ERROR_FILE = "error.log"

# LINE API
LINE_URL = 'https://notify-api.line.me/api/notify'
TOKEN = 'pY5mO6MnPlFt9q66FiG6QAWtUfwcyIN2KF5l1eFdoq9'

DB_PATH = 'aquarium.sqlite'


def main():
    
    dt_now = datetime.datetime.now()
    temp, humid = get_temp_humid()
    w_temp = get_water_temp()
    w_ph = get_ph()
    if w_temp >= TEMP_WARN:
        notice_line(w_temp)
    out_log(dt_now, str(temp), str(humid), str(w_temp), str(w_ph), OUTPUT_DIR)
    out_sqlite(dt_now, str(temp), str(humid), str(w_temp), str(w_ph))
    set_fan(dt_now, w_temp)
#    print_error('test')
#    print(result)

def out_log(dt_now, temp, humid, w_temp, w_ph, log_path):
    date_file = 'temp{0}.log'.format(dt_now.strftime('%Y%m%d'))
    file_path = '{0}/{1}'.format(OUTPUT_DIR, date_file)
    date = dt_now.strftime('%Y/%m/%d')
    time = dt_now.strftime('%H:%M:%S')
#    result = '{0} 温度={1:0.1f}℃ 湿度={2:0.1f}% 水温={3}℃'.format(dt_out, temperature, humidity, water_temp)
    result = ', '.join([date, time, temp, humid, w_temp, w_ph])
    with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
        f.write(result+'\n')

def set_fan(dt_now, w_temp):
    date_file = 'temp{0}.log'.format(dt_now.strftime('%Y%m%d'))
    file_path = '{0}/{1}'.format(OUTPUT_DIR, date_file)

    # GPIO番号指定の準備
    GPIO.setmode(GPIO.BCM)

    # LEDピンを出力に設定
    GPIO.setup(GPIO_FAN, GPIO.OUT)

    if w_temp >= FAN_ON:
        GPIO.output(GPIO_FAN, 1)
        with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
            f.write('fan on\n')

    if w_temp <= FAN_OFF:
        GPIO.output(GPIO_FAN, 0)
        with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
            f.write('fan off\n')


def out_sqlite(dt_now, temp, humid, w_temp, w_ph):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    date = dt_now.strftime('%Y/%m/%d')
    time = dt_now.strftime('%H:%M:%S')

    try:
        # CREATE（「id、name」のテーブルを作成）
        cursor.execute("CREATE TABLE IF NOT EXISTS aquarium \
            (id integer primary key autoincrement, \
             date TEXT, \
             time TEXT, \
             air_temp REAL, \
             air_himid REAL, \
             water_temp REAL, \
             water_ph REAL)")

        # INSERT
        cursor.execute("INSERT INTO aquarium(date, time, air_temp, air_himid, water_temp, water_ph)\
             VALUES(?,?,?,?,?,?)", (date, time, temp, humid, w_temp, w_ph))

    except sqlite3.Error as e:
        print_error('sqlite3.Error occurred:', e.args[0])

    connection.commit()
    connection.close()


def notice_line(temp):
    try:
        headers = {'accept':'application/json','Authorization': 'Bearer {}'.format(TOKEN) } 
        message = 'message= temperature:{}'.format(temp) 
#        print(headers)
        r_get = requests.post(LINE_URL, params=message, headers=headers)
#        print(r_get.url)
        print(r_get.text)
    except requests.exceptions.RequestException as e:
        print_error("APIエラー : ",e)    

def get_water_temp():
    try:
        res = subprocess.check_output(["cat", SENSOR_W1_SLAVE])
        if res is not None:
            temp_val = res.split(b"=")
            if temp_val[-1] == ERR_VAL:
                print_error("Got value:85000. Circuit is ok, but something wrong happens...")
                sys.exit(1)

            return round(float(temp_val[-1]) / 1000, 1)
        else:
            print_error('none {1}', res)

    except Exception as e:
        print_error(e.message)
        return None
        
def get_temp_humid():
    try:
        i2c.write_i2c_block_data(address,0x00,[])
    except:
        pass

    # 読み取り命令
    i2c.write_i2c_block_data(address,0x03,[0x00,0x04])

    # データ受取
    time.sleep(0.015)
    block = i2c.read_i2c_block_data(address,0,6)
    humidity = float(block[2] << 8 | block[3])/10
    temperature = float(block[4] << 8 | block[5])/10
    
    return temperature, humidity

def get_ph():
    try:
        arduino_val=ARDUINO_CON.readline() # byte code
        decode_val=arduino_val.strip().decode('utf-8')
    #    dict_val=json.loads('{"key":"value"}')
    #    dict_val=json.loads('{"voltage" : "777.16", "ph" : "7.45"}')
    #    m = re.match(r'ch: ([0-9]*)', decode_val)
    #    m = re.match(r'([a-z]+)@([a-z]+)\.([a-z]+)', dict_val)
        m = re.search(r'ph : ([0-9\.]*)', decode_val)
        if m:
            return m.groups()[0]
        else:
            return 0
    except Exception as e:
        print_error(e.message)
        return None
    
def print_error(e):
    dt_now = datetime.datetime.now()
    file_path = '{0}/{1}'.format(OUTPUT_DIR, ERROR_FILE)
    dt = dt_now.strftime('%Y/%m/%d %H:%M:%S')
    result = '[{0}] {1}'.format(dt, e)
    with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
        f.write(result+'\n')
    print('Error: {}'.format(e))
    sys.exit(1)


if __name__ == '__main__':
    main()
