import asyncio
from typing import List, AsyncGenerator
import strawberry
from strawberry import Schema

from models import AquaEnv
from database import get_db


@strawberry.type
class AquaEnvType:
    id: int
    date: str
    time: str
    air_temp: float
    air_humid: float
    water_temp: float
    water_ph: float

@strawberry.type
class Query:
    @strawberry.field
    async def aquaenv(self, start_at: str , limit: int = 100) -> List[AquaEnvType]:
            db=get_db()
            aquaenvList = db.query(AquaEnv)\
                .order_by(AquaEnv.date.desc(), AquaEnv.time.desc())\
                .limit(limit).all()
            return [AquaEnvType(\
                 id=aquaenv.id,\
                 date=aquaenv.date,\
                 time=aquaenv.time,\
                 air_temp=aquaenv.air_temp,\
                 air_humid=aquaenv.air_himid,\
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
             air_himid=air_humid, water_temp=water_temp, \
             water_ph=water_ph)
        db.add(aquaenv)
        db.commit()
        db.refresh(aquaenv)
        return AquaEnvType(id=aquaenv.id, date=aquaenv.date, \
             time=aquaenv.time, air_temp=aquaenv.air_temp, \
             air_humid=aquaenv.air_himid, water_temp=aquaenv.water_temp,\
             water_ph=aquaenv.water_ph) 



schema = Schema(query=Query, mutation=Mutation)

