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
    air_temp: float
    air_humid: float
    water_temp: float
    water_ph: float

@strawberry.type
class Query:
    @strawberry.field
    async def aquaenv(self, startAt: int = 0, endAt: int = 32472111600, recordPerDay: int = 0, limit: int = 100) -> List[AquaEnvType]:
            db=get_db()
            
            filter_time = []
            # match recordPerDay:
            #     case 1:
            #         filter_time = ["12:00"]

            #     case 2:
            #         print('2??')

            #     case _:
            #         print('??????')
            if startAt == 0:
                aquaenvList = db.query(AquaEnv)\
                    .filter(AquaEnv.unixtime <= endAt)\
                    .order_by(AquaEnv.unixtime.desc())\
                    .limit(limit).all()
            else:
                aquaenvList = db.query(AquaEnv)\
                    .filter(AquaEnv.unixtime > startAt)\
                    .filter(AquaEnv.unixtime <= endAt)\
                    .order_by(AquaEnv.unixtime.asc())\
                    .limit(limit).all()
                # aquaenvList = db.query(AquaEnv, \
                #         func.avg(AquaEnv.air_temp))\
                #     .filter(AquaEnv.unixtime > startAt)\
                #     .filter(AquaEnv.unixtime <= endAt)\
                #     .group_by(AquaEnv.avg_unixtime)\
                #     .order_by(AquaEnv.unixtime.asc())\
                #     .limit(limit).all()
                

            return [AquaEnvType(\
                 id=aquaenv.id,\
                 date=aquaenv.avg_date,\
                 time=aquaenv.avg_time,\
                 unixtime=aquaenv.avg_unixtime,\
                 air_temp=aquaenv.air_temp,\
                 air_humid=aquaenv.air_humid,\
                 water_temp=aquaenv.water_temp,\
                 water_ph=aquaenv.water_ph,\
                ) for aquaenv in aquaenvList]

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_aquaenv(self, date: str, time: str, \
             air_temp: float, air_humid: float, water_temp: float,\
             water_ph: float) -> AquaEnvType:
        db=get_db() 
        aquaenv = AquaEnv(date=date, time=time, air_temp=air_temp,\
             air_humid=air_humid, water_temp=water_temp, \
             water_ph=water_ph)
        db.add(aquaenv)
        db.commit()
        db.refresh(aquaenv)
        return AquaEnvType(id=aquaenv.id, date=aquaenv.date, \
             time=aquaenv.time, air_temp=aquaenv.air_temp, \
             air_humid=aquaenv.air_humid, water_temp=aquaenv.water_temp,\
             water_ph=aquaenv.water_ph) 



schema = Schema(query=Query, mutation=Mutation)

