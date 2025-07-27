
# 1時間, 6時間, 24時間ごとの平均を記録する
def summary_data(unixtime):
    air_temp_avg, air_humid_avg, water_temp_avg, water_ph_avg = extract_average_data(unixtime)

    dt_jst_aware = datetime.datetime.fromtimestamp(unixtime, datetime.timezone(datetime.timedelta(hours=9)))
    date = dt_jst_aware.strftime('%Y/%m/%d')
    time = dt_jst_aware.strftime('%H:%M:%S')
    # print(f"{date} {time}")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        # CREATE（「id、name」のテーブルを作成）
        cursor.execute("CREATE TABLE IF NOT EXISTS aquarium_avg \
            (id integer primary key autoincrement, \
            date	TEXT,\
            time	TEXT,\
            unixtime	integer,\
            range_group	integer,\
            air_temp_avg	REAL,\
            air_himid_avg	REAL,\
            water_temp_avg	REAL,\
            water_ph_avg	REAL)")

        # INSERT
        cursor.execute("INSERT INTO aquarium_avg(date, time, unixtime, range_group, air_temp_avg, air_humid_avg, water_temp_avg, water_ph_avg)\
             VALUES(?,?,?,?,?,?,?,?)", (date, time, unixtime, 60, air_temp_avg, air_humid_avg, water_temp_avg, water_ph_avg))
        
    except sqlite3.Error as e:
        print_error('sqlite3.Error occurred:', e.args[0])

    connection.commit()
    connection.close()


def extract_average_data(unixtime):
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

    # print(df)
    # print(f"{air_temp_avg},{air_humid_avg},{water_temp_avg},{water_ph_avg}")

    connection.close()
    return air_temp_avg, air_humid_avg, water_temp_avg, water_ph_avg
