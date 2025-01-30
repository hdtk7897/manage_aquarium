from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AquaEnv(Base):
    __tablename__ = "aquarium"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    time = Column(String)
    air_temp = Column(Float)
    air_himid = Column(Float)
    water_temp = Column(Float)
    water_ph = Column(Float)
