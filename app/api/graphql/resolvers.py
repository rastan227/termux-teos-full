from strawberry.fastapi import GraphQLRouter
from app.api.graphql.schema import schema
from app.api.dependencies import get_current_user_optional
from fastapi import Depends

async def get_context(user=Depends(get_current_user_optional)):
    return {"user": user}

graphql_app = GraphQLRouter(schema, context_getter=get_context)
