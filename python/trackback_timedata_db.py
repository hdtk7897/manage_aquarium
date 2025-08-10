#!usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import datetime
from thermohygrometer import calc_unittime_and_group 

dbpath = '/home/hdtk7897/aquarium.sqlite'

# データベース接続とカーソル生成
# dppathと同名のファイルがなければ、DBファイルが作成されます。
db_connection = sqlite3.connect(dbpath)

# 自動コミットにする場合は下記を指定（コメントアウトを解除のこと）
# connection.isolation_level = None
db_cursor = db_connection.cursor()
db_cursor2 = db_connection.cursor()

db_col = ["id", "date", "time", "unixtime", "temp", "humid", "w_temp", "w_ph", \
          "unittime", "time_group", "fan_sw"]

try:
    db_cursor.execute("SELECT id, unixtime, unit_time from aquarium;")
    count = 0
    
    while True:
        print("fetch")
        db_row = db_cursor.fetchone()
        if db_row is None  :
            print(f"break count:{count}")
            break
        
        db_dict = dict(zip(["id","unixtime","unit_time"], db_row))

        unittime, time_group = calc_unittime_and_group(db_dict["unixtime"])

        
        if db_dict["unit_time"] is None:
            count += 1
            print(f"unixtime:{db_dict['unixtime']}, unittime:{unittime}, time_group:{time_group}")

            db_cursor2.execute(f"update aquarium SET unit_time = {unittime}, time_group = {time_group} WHERE id = {db_dict['id']};")


except sqlite3.Error as e:
    print('sqlite3.Error occurred:', e.args[0])

# 保存を実行（忘れると保存されないので注意）
db_connection.commit()

# 接続を閉じる
db_connection.close()
