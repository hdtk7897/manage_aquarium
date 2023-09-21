#!usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

# データベースファイルのパス
# 慣例的に拡張子に、”.sqlite”をつけるらしい。
dbpath = 'sample_db.sqlite'

# データベース接続とカーソル生成
# dppathと同名のファイルがなければ、DBファイルが作成されます。
connection = sqlite3.connect(dbpath)

# 自動コミットにする場合は下記を指定（コメントアウトを解除のこと）
# connection.isolation_level = None
cursor = connection.cursor()

try:
    # CREATE（「id、name」のテーブルを作成）
    cursor.execute("CREATE TABLE IF NOT EXISTS mytable (id INTEGER, name TEXT)")

    # INSERT
    cursor.execute("INSERT INTO mytable VALUES(1, '佐藤')")

    cursor.execute("INSERT INTO mytable (id, name) VALUES (?,?)",(2,'加藤'))

    # パラメータが1つの場合には最後に , がないとエラー。('鈴木') ではなく ('鈴木',)
    cursor.execute("INSERT INTO mytable VALUES (3, ?)", ('鈴木',))

    cursor.execute("INSERT INTO mytable VALUES (?, ?)", (4, '高橋'))

    cursor.execute("INSERT INTO mytable VALUES (:id, :name)",{'id': 5, 'name': '田中'})

    # 複数レコードを一度に挿入 executemany メソッドを使用
    persons = [
        (6, '伊藤'),
        (7, '渡辺'),
    ]
    cursor.executemany("INSERT INTO mytable VALUES (?, ?)", persons)

    # わざと主キー重複エラーを起こして例外を発生させてみる
#    cursor.execute("INSERT INTO mytable VALUES (1, '佐藤')")

except sqlite3.Error as e:
    print('sqlite3.Error occurred:', e.args[0])

# 保存を実行（忘れると保存されないので注意）
connection.commit()

# 接続を閉じる
connection.close()
