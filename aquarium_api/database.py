# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import configparser
from models import Base

config = configparser.ConfigParser()
config.read('/etc/manage_aquarium.ini')

DB_PATH = config['COMMON']['HOME_PATH'] + '/aquarium.sqlite'

engine = create_engine("sqlite:///" + DB_PATH)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
       db.close()