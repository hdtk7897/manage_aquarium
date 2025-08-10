from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import datetime


Base = declarative_base()

class AquaEnv(Base):
    __tablename__ = "aquarium"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    time = Column(String)
    unixtime = Column(Integer)
    unit_time = Column(Integer)
    air_temp = Column(Float)
    air_humid = Column(Float)
    water_temp = Column(Float)
    water_ph = Column(Float)
    time_group  = Column(Integer)
    fan_sw = Column(String)

    @hybrid_property
    def avg_unixtime(self):
        return (self.unixtime/3600)*3600        
        # return round(self.unixtime/3600)*3600

    @hybrid_property
    def avg_date(self):
        return format(datetime.datetime.fromtimestamp(self.avg_unixtime, datetime.timezone.utc),'%Y/%m/%d')

    @hybrid_property
    def avg_time(self):
        return format(datetime.datetime.fromtimestamp(self.avg_unixtime, datetime.timezone.utc),'%H:%M:%S')
