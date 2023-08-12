#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import smbus
import subprocess
import datetime
import requests
import pprint

# 温湿度計
i2c = smbus.SMBus(1)
address = 0x5c

# 水温計
SENSOR_ID = "28-3c1b04572da2"
SENSOR_W1_SLAVE = "/sys/bus/w1/devices/" + SENSOR_ID + "/w1_slave"
ERR_VAL = 85000
TEMP_WARN = 28.0

# 出力
OUTPUT_DIR = "/home/pi/log"

# LINE API
LINE_URL = 'https://notify-api.line.me/api/notify'
TOKEN = 'pY5mO6MnPlFt9q66FiG6QAWtUfwcyIN2KF5l1eFdoq9'

def main():
    
    
    temp, humid = get_temp_humid()
    w_temp = get_water_temp()
    if w_temp >= TEMP_WARN:
        notice_line(w_temp)
    out_log(str(temp), str(humid), str(w_temp), OUTPUT_DIR)
#    print(result)

def out_log(temp, humid, w_temp, log_path):
    dt_now = datetime.datetime.now()
    date_file = 'temp{0}.log'.format(dt_now.strftime('%Y%m%d'))
    file_path = '{0}/{1}'.format(OUTPUT_DIR, date_file)
    date = dt_now.strftime('%Y/%m/%d')
    time = dt_now.strftime('%H:%M:%S')
#    result = '{0} 温度={1:0.1f}℃ 湿度={2:0.1f}% 水温={3}℃'.format(dt_out, temperature, humidity, water_temp)
    result = ', '.join([date, time, temp, humid, w_temp])
    with open(file_path, mode='a', encoding='UTF-8', newline='\n') as f:
        f.write(result+'\n')

def notice_line(temp):
    try:
        headers = {'accept':'application/json','Authorization': 'Bearer {}'.format(TOKEN) } 
        message = 'message= temperature:{}'.format(temp) 
#        print(headers)
        r_get = requests.post(LINE_URL, params=message, headers=headers)
#        print(r_get.url)
        print(r_get.text)
    except requests.exceptions.RequestException as e:
        print("APIエラー : ",e)    

def get_water_temp():
    try:
        res = subprocess.check_output(["cat", SENSOR_W1_SLAVE])
        if res is not None:
            temp_val = res.split(b"=")
            if temp_val[-1] == ERR_VAL:
                print("Got value:85000. Circuit is ok, but something wrong happens...")
                sys.exit(1)

            return round(float(temp_val[-1]) / 1000, 1)
        else:
            print('none {1}', res)

    except Exception as e:
        print(e.message)
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

if __name__ == '__main__':
    main()
    
