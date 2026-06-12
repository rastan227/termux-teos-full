import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class User:
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: str
    role: str
    wallet_balance: int

@strawberry.type
class Music:
    id: int
    title: str
    artist: str
    genre: str
    plays: int
    likes: int

@strawberry.type
class Service:
    id: int
    name: str
    price: int
    period: str
    is_active: bool

@strawberry.type
class Order:
    id: int
    order_number: str
    total_price: int
    status: str
    created_at: datetime

@strawberry.input
class UserFilter:
    role: Optional[str] = None
    is_active: Optional[bool] = None

@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info) -> User:
        # Get current user from context
        user = info.context["user"]
        return User(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            role=user.role.value,
            wallet_balance=user.wallet_balance
        )
    
    @strawberry.field
    async def music(self, id: int) -> Optional[Music]:
        from app.services.music_service import MusicService
        song = await MusicService.get_song_by_id(id)
        if song:
            return Music(
                id=song.id,
                title=song.title,
                artist=song.artist,
                genre=song.genre,
                plays=song.plays,
                likes=song.likes
            )
        return None
    
    @strawberry.field
    async def popular_music(self, limit: int = 10) -> List[Music]:
        from app.services.music_service import MusicService
        songs = await MusicService.get_most_popular(limit)
        return [
            Music(
                id=s["id"],
                title=s["title"],
                artist=s["artist"],
                genre=s.get("genre", ""),
                plays=s.get("plays", 0),
                likes=s.get("likes", 0)
            ) for s in songs
        ]
    
    @strawberry.field
    async def my_orders(self, info) -> List[Order]:
        user = info.context["user"]
        from app.services.order_service import OrderService
        result = await OrderService.get_user_orders(user.telegram_id, page=1, limit=50)
        return [
            Order(
                id=o["id"],
                order_number=o["order_number"],
                total_price=o["final_price"],
                status=o["status"],
                created_at=datetime.fromisoformat(o["created_at"])
            ) for o in result["items"]
        ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def like_music(self, info, music_id: int) -> bool:
        user = info.context["user"]
        from app.services.music_service import MusicService
        return await MusicService.like_song(user.telegram_id, music_id)

schema = strawberry.Schema(query=Query, mutation=Mutation)
