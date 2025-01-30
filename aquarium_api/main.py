from fastapi import FastAPI
from strawberry.asgi import GraphQL

from schema import schema

# import pandas as pd
# import sqlite3
# import configparser



# # (2) User型定義
# @strawberry.type
# class User:
#     name: str
#     age: int

# # (3) Queryクラス定義
# @strawberry.type
# class Query:
#     @strawberry.field
#     def user(self) -> User:
#         data = read_item(31310)
#         return User(name=data, age=22)

# # (4) スキーマ定義
# schema = strawberry.Schema(query=Query)

# # (5) GraphQLエンドポイント
# graphql_app = GraphQLRouter(schema)

# (6) FastAPIインスタンス作成
app = FastAPI()

# (7) レスポンス出力
@app.get("/")
async def index():
    return {"message": "Welcome to the Aquarium API"}

app.add_route("/graphql", GraphQL(schema))
