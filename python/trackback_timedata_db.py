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

db_col = ["id", "date", "time", "unixtime", "temp", "humid", "w_temp", "w_ph", \
          "unittime", "time_group", "fan_sw"]

try:
    db_cursor.execute("SELECT id, unixttime from aquarium;")
    
    while True:
        db_row = db_cursor.fetchone()
        
        if db_row is None:
            break
        
        db_dict = dict(zip(["id","unixtime"], db_row))
        print(db_dict)

        unittime, time_group = calc_unittime_and_group(db_dict["unixtime"])

        db_cursor.execute(f"update aquarium SET unittime = {unittime}, time_group = {time_group} WHERE id = {db_dict["id"]};")

        # db_cursor.execute("insert into aquarium(date, time, unixtime, air_temp, air_humid, water_temp, water_ph) values(?,?,?,?,?,?,?)"\
        #                    ,(old_dict["date"], old_dict["time"], unixtime, old_dict["air_temp"], old_dict["air_himid"], old_dict["water_temp"], old_dict["water_ph"]))

except sqlite3.Error as e:
    print('sqlite3.Error occurred:', e.args[0])

# 保存を実行（忘れると保存されないので注意）
db_connection.commit()

# 接続を閉じる
db_connection.close()
