#!/usr/bin/env python3
import asyncio
from app.core.database import async_session_maker
from app.models.user import User, UserRole
from app.models.music import Music
from app.models.service import Service, ServiceType, ServicePeriod

async def create_sample_data():
    async with async_session_maker() as session:
        # Sample users
        users = [
            User(telegram_id=111111, username="user1", first_name="کاربر", role=UserRole.USER, wallet_balance=100000),
            User(telegram_id=222222, username="admin1", first_name="مدیر", role=UserRole.SUPER_ADMIN, wallet_balance=0),
        ]
        for u in users:
            session.add(u)
        
        # Sample music
        music = [
            Music(title="آهنگ یک", artist="هنرمند یک", genre="پاپ", file_path="storage/music/song1.mp3", is_active=True),
            Music(title="آهنگ دو", artist="هنرمند دو", genre="رپ", file_path="storage/music/song2.mp3", is_active=True),
        ]
        for m in music:
            session.add(m)
        
        # Sample services
        services = [
            Service(name="VPN ماهانه", slug="vpn-monthly", price=50000, period=ServicePeriod.MONTHLY, is_active=True),
            Service(name="VPN سالانه", slug="vpn-yearly", price=500000, period=ServicePeriod.ANNUAL, is_active=True),
        ]
        for s in services:
            session.add(s)
        
        await session.commit()
        print("Sample data created")

if __name__ == "__main__":
    asyncio.run(create_sample_data())
