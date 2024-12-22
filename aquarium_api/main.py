import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL

# (2) User型定義
@strawberry.type
class User:
    name: str
    age: int

# (3) Queryクラス定義
@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Shota", age=22)

# (4) スキーマ定義
schema = strawberry.Schema(query=Query)

# (5) GraphQLエンドポイント
graphql_app = GraphQL(schema)

# (6) FastAPIインスタンス作成
app = FastAPI()

# (7) レスポンス出力
app.add_route("/graphql", graphql_app)