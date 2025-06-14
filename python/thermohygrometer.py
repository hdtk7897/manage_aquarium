#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import json
import subprocess
from subprocess import PIPE
import datetime
import requests
import serial
import re
from gpiozero import LED
import sqlite3
import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('/etc/manage_aquarium.ini')

# # 水温計
TEMP_MIN = 24.5
TEMP_MAX = 29.5

# ファン
FAN_ON = 28.0
FAN_OFF = 26.5
GPIO_FAN = 17
GPIO_FAN_OPP = 27

# ph
ARDUINO_PATH = '/dev/ttyACM0'
ARDUINO_PORT = 9600
ARDUINO_RETRY = 3
ARDUINO_INTERVAL = 0.5


# 出力
LOG_DIR = config['COMMON']['HOME_PATH'] + "/log"
ERROR_FILE = "error.log"


DB_PATH = config['COMMON']['HOME_PATH'] + '/aquarium.sqlite'
SH_PATH = config['COMMON']['HOME_PATH'] + '/manage_aquarium/sh'


def main():
    dt_now = datetime.datetime.now()
    w_ph, w_temp, a_temp, a_humid = get_arduino()
    if float(w_temp) >= TEMP_MAX or float(w_temp) <= TEMP_MIN:
        notice_line(w_temp)
    fan_sw = set_fan(dt_now, w_temp)
    out_sqlite(dt_now, str(a_temp), str(a_humid), str(w_temp), str(w_ph), fan_sw)
#    print_error('test')
#    print(result)

def out_log(str, dt_now):
    date_file = 'temp{0}.log'.format(dt_now.strftime('%Y%m%d'))
    file_path = '{0}/{1}'.format(LOG_DIR, date_file)
    print(str)
    with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
        f.write(str+'\n')

def set_fan(dt_now, w_temp_string):
    w_temp = float(w_temp_string)
    date_file = 'temp{0}.log'.format(dt_now.strftime('%Y%m%d'))
    file_path = '{0}/{1}'.format(LOG_DIR, date_file)

#    set_gpio(GPIO_FAN_OPP, "on")

    if w_temp >= FAN_ON:
        set_gpio(GPIO_FAN, "on")
        set_gpio(GPIO_FAN_OPP, "off")
    
        with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
            f.write('fan on\n')
        print('fan on')
        return "ON"

    if w_temp <= FAN_OFF:
        set_gpio(GPIO_FAN, "off")
        set_gpio(GPIO_FAN_OPP, "on")
        with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
            f.write('fan off\n')
        print('fan off')
        return "OFF"
    
    val = get_gpio(GPIO_FAN_OPP)
    return "ON" if val == "lo" else "OFF"
        
#    time.sleep(10)

def set_gpio(num, sw):
    sh_cmd = SH_PATH + "/set_gpio.sh " + str(num) + " " + sw
    subprocess.Popen( sh_cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    print(sh_cmd)

def get_gpio(num):
    if num == GPIO_FAN_OPP:
        sh_cmd = SH_PATH + "/get_gpio.sh " + str(num) + " hi"
    else: 
        sh_cmd = SH_PATH + "/get_gpio.sh " + str(num)
    result = subprocess.Popen( sh_cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)

    line = result.stdout.readlines()[0].rstrip('\r\n')
    return line

def out_sqlite(dt_now, temp, humid, w_temp, w_ph, fan_sw):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    date = dt_now.strftime('%Y/%m/%d')
    time = dt_now.strftime('%H:%M:%S')
    unixtime = int(datetime.datetime.timestamp(dt_now))
    unittime, time_group = calc_unittime_and_group(unixtime)

    try:
        # CREATE（「id、name」のテーブルを作成）
        cursor.execute("CREATE TABLE IF NOT EXISTS aquarium \
            (id integer primary key autoincrement, \
             date TEXT, \
             time TEXT, \
             unixtime integer, \
             air_temp REAL, \
             air_humid REAL, \
             water_temp REAL, \
             water_ph REAL, \
             unittime integer, \
             time_group integer,\
             fan_sw TEXT")

        # INSERT
        cursor.execute("INSERT INTO aquarium(date, time, unixtime, air_temp, air_humid, \
                       water_temp, water_ph, unit_time, time_group, fan_sw)\
             VALUES(?,?,?,?,?,?,?,?,?)", (date, time, unixtime, temp, humid, \
                                          w_temp, w_ph, unittime, time_group, fan_sw))

    except sqlite3.Error as e:
        print_error(f'sqlite3.Error occurred:{e.args[0]}')

    connection.commit()
    connection.close()

def calc_unittime_and_group(unixtime):
    unittime = round(unixtime / 600) * 600

    time_group = 0
    # 24時間ごと
    if unittime % 86400 == 10800:
        time_group = 30
    # 6時間ごと
    elif unittime % 21600 == 10800:
        time_group = 20
    # 1時間ごと
    elif unittime % 3600 == 0:
        time_group = 10

    return unittime, time_group


def notice_line(message):
    try:
        sh_cmd = SH_PATH + "/notice_line.sh " + str(message)
        subprocess.Popen( sh_cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)

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
        ser = serial.Serial(ARDUINO_PATH, ARDUINO_PORT, timeout=1)
        arduino_val=ser.readline() # byte code
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

def get_arduino():
    ser = serial.Serial(ARDUINO_PATH, ARDUINO_PORT, timeout=1)
    ser.flush()
    time.sleep(2)
    for i in range(0, ARDUINO_RETRY):
        try:
#            ser.write(b"hi\n")
    #        arduino_val=ser.readline()
            arduino_val=ser.readline().decode('utf-8').rstrip()
    #        arduino_val=ser.readline().strip().decode('utf-8')
            l = arduino_val.split(',')
            kv = dict()
            for each_val in l:
                kv_arr = each_val.split(':')
                val = re.search(r'([0-9\.]*)', kv_arr[1].strip())
                kv[kv_arr[0].strip()] = val.group()
            if kv:
                return kv['pH'], kv['WT'], kv['T'], kv['H']

        except Exception as e:
            if i + 1 == ARDUINO_RETRY:
                if hasattr(e, 'message'):
                    print_error(e.message)
                else:
                    print_error(e)
                raise e
            time.sleep(ARDUINO_INTERVAL)
            print('retry')
            continue
    return 0, 0, 0, 0
    
def print_error(e):
    dt_now = datetime.datetime.now()
    file_path = '{0}/{1}'.format(LOG_DIR, ERROR_FILE)
    dt = dt_now.strftime('%Y/%m/%d %H:%M:%S')
    result = '[{0}] {1}'.format(dt, e)
    with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
        f.write(result+'\n')
    print('Error: {}'.format(e))
    sys.exit(1)


if __name__ == '__main__':
    main()
    
