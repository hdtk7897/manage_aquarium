import asyncio
from typing import List, AsyncGenerator
import strawberry
from strawberry import Schema
from sqlalchemy import func

from models import AquaEnv
from database import get_db

@strawberry.type
class AquaEnvType:
    id: int
    date: str
    time: str
    unixtime: int
    unit_time:int
    time_group:int
    air_temp: float
    air_humid: float
    water_temp: float
    water_ph: float
    fan_sw:str

@strawberry.type
class Query:
    @strawberry.field
    async def aquaenv(self, startAt: int = 0, endAt: int = 32472111600, timeGroup: int = 0, limit: int = 100) -> List[AquaEnvType]:
            db=get_db()
            
            aquaenvList = db.query(AquaEnv).filter(AquaEnv.time_group >= timeGroup)


            if startAt == 0:
                aquaenvList = aquaenvList.filter(AquaEnv.unixtime <= endAt)\
                    .order_by(AquaEnv.unixtime.desc())\
                    .limit(limit).all()
            else:
                aquaenvList = aquaenvList.filter(AquaEnv.unixtime > startAt)\
                    .filter(AquaEnv.unixtime <= endAt)\
                    .order_by(AquaEnv.unixtime.asc())\
                    .limit(limit).all()
                

            return [AquaEnvType( \
                 id=aquaenv.id,\
                 date=aquaenv.avg_date,\
                 time=aquaenv.avg_time,\
                 unixtime=aquaenv.avg_unixtime,\
                 unit_time=aquaenv.unit_time,
                 air_temp=aquaenv.air_temp,\
                 air_humid=aquaenv.air_humid,\
                 water_temp=aquaenv.water_temp,\
                 water_ph=aquaenv.water_ph,\
                 time_group=aquaenv.time_group, \
                 fan_sw=aquaenv.fan_sw 
                ) for aquaenv in aquaenvList]

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_aquaenv(
        self, \
        date: str, \
        time: str, \
        air_temp: float, \
        air_humid: float, \
        water_temp: float,\
        water_ph: float
    ) -> AquaEnvType:
        db=get_db() 
        aquaenv = AquaEnv(
             date=date, \
             time=time, \
             air_temp=air_temp,\
             air_humid=air_humid, \
             water_temp=water_temp, \
             water_ph=water_ph)
        db.add(aquaenv)
        db.commit()
        db.refresh(aquaenv)
        return AquaEnvType(
            id=aquaenv.id, \
            date=aquaenv.date, \
            time=aquaenv.time, \
            air_temp=aquaenv.air_temp, \
            air_humid=aquaenv.air_humid, \
            water_temp=aquaenv.water_temp,\
            water_ph=aquaenv.water_ph) 



schema = Schema(query=Query, mutation=Mutation)

