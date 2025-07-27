#!usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import datetime

old_dbpath = '/home/hdtk7897/aquarium.sqlite'
new_dbpath = '/home/hdtk7897/aquarium2.sqlite'

# データベース接続とカーソル生成
# dppathと同名のファイルがなければ、DBファイルが作成されます。
old_connection = sqlite3.connect(old_dbpath)
new_connection = sqlite3.connect(new_dbpath)

# 自動コミットにする場合は下記を指定（コメントアウトを解除のこと）
# connection.isolation_level = None
old_cursor = old_connection.cursor()
new_cursor = new_connection.cursor()

old_db_col = ["id", "date", "time", "air_temp", "air_himid", "water_temp", "water_ph"]
new_db_col = ["unixtime", "air_temp", "air_humid", "water_temp", "water_ph"]

try:
    old_cursor.execute("SELECT * from aquarium;")
    
    while True:
        old_row = old_cursor.fetchone()
        
        if old_row is None:
            break
        
        old_dict = dict(zip(old_db_col, old_row))
    #    print(old_dict)
        datetime_obj = datetime.datetime.strptime(old_dict["date"] + "_" + old_dict["time"],'%Y/%m/%d_%H:%M:%S')
        unixtime = int(datetime.datetime.timestamp(datetime_obj))
    #    print(unixtime)
        
        new_cursor.execute("insert into aquarium(date, time, unixtime, air_temp, air_humid, water_temp, water_ph) values(?,?,?,?,?,?,?)"\
                           ,(old_dict["date"], old_dict["time"], unixtime, old_dict["air_temp"], old_dict["air_himid"], old_dict["water_temp"], old_dict["water_ph"]))

except sqlite3.Error as e:
    print('sqlite3.Error occurred:', e.args[0])

# 保存を実行（忘れると保存されないので注意）
new_connection.commit()

# 接続を閉じる
#connection.close()
