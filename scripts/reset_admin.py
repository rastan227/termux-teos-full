#!/usr/bin/env python3
import asyncio
from app.services.user_service import UserService
from app.models.user import UserRole

async def reset():
    telegram_id = int(input("Enter Telegram ID: "))
    user = await UserService.get_user_by_telegram_id(telegram_id)
    if user:
        user.role = UserRole.OWNER
        print(f"User {telegram_id} is now OWNER")
    else:
        print("User not found, creating new owner...")
        user = await UserService.get_or_create(telegram_id, "admin", "Admin", "User")
        user.role = UserRole.OWNER
        print("Owner created")
    from app.core.database import async_session_maker
    async with async_session_maker() as session:
        session.add(user)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(reset())
