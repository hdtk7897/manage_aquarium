from fastapi import FastAPI
import pandas as pd
import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('/etc/manage_aquarium.ini')

DB_PATH = config['COMMON']['HOME_PATH'] + '/aquarium.sqlite'


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/aquadata/")
def read_item_noparam():
    return read_item(10)

@app.get("/aquadata/{item_id}")
def  read_item(item_id: int, q: str = None):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM aquarium order by date desc, time desc limit 100', conn)
    narrow_df = df.head(item_id)
    print(narrow_df)
    return {narrow_df.T.to_json()}