#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
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

# LINE API
LINE_URL = 'https://notify-api.line.me/api/notify'

DB_PATH = config['COMMON']['HOME_PATH'] + '/aquarium.sqlite'
SH_PATH = config['COMMON']['HOME_PATH'] + '/manage_aquarium/sh'


def main():
    dt_now = datetime.datetime.now()
    unixtime = int(datetime.datetime.timestamp(dt_now))
    adjust_unixime = unixtime // 600 * 600
    print(adjust_unixime)
    summary_data(adjust_unixime)


# 1時間, 6時間, 24時間ごとの平均を記録する
def summary_data(unixtime):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    datetimefrom = unixtime - 3600
    datetimeto = unixtime + 540

    df = pd.read_sql_query(sql=f"SELECT date, time, unixtime, air_temp, air_humid, water_temp, water_ph \
            from aquarium where unixtime between {datetimefrom} and {datetimeto} ;", con=connection)
    air_temp_avg = df["air_temp"].mean().round(1)
    air_humid_avg = df["air_humid"].mean().round(1)
    water_temp_avg = df["water_temp"].mean().round(1)
    water_ph_avg = df["water_ph"].mean().round(2)

    print(df)
    print(f"{air_temp_avg},{air_humid_avg},{water_temp_avg},{water_ph_avg}")

    dt_jst_aware = datetime.datetime.fromtimestamp(unixtime, datetime.timezone(datetime.timedelta(hours=9)))
    date = dt_jst_aware.strftime('%Y/%m/%d')
    time = dt_jst_aware.strftime('%H:%M:%S')
    print(f"{date} {time}")
    # try:
    #     # CREATE（「id、name」のテーブルを作成）
    #     cursor.execute("CREATE TABLE IF NOT EXISTS aquarium \
    #         (id integer primary key autoincrement, \
    #          date TEXT, \
    #          time TEXT, \
    #          unixtime integer, \
    #          air_temp REAL, \
    #          air_humid REAL, \
    #          water_temp REAL, \
    #          water_ph REAL)")

    #     # INSERT
    #     cursor.execute("INSERT INTO aquarium(date, time, unixtime, air_temp, air_humid, water_temp, water_ph)\
    #          VALUES(?,?,?,?,?,?,?)", (date, time, unixtime, temp, humid, w_temp, w_ph))

    # except sqlite3.Error as e:
    #     print_error('sqlite3.Error occurred:', e.args[0])

    connection.commit()
    connection.close()



if __name__ == '__main__':
    main()
    
