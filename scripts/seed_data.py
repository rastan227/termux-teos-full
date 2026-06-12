#!/usr/bin/env python3
import asyncio
from app.core.database import async_session_maker, engine, Base
from app.models.user import User, UserRole
from app.models.service import Service, ServiceType, ServicePeriod
from app.models.music import Music
from app.models.settings import SystemSetting

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_maker() as session:
        owner = User(
            telegram_id=123456789,
            username="owner",
            first_name="TEOS",
            last_name="Owner",
            role=UserRole.OWNER,
            wallet_balance=0,
            referral_code="OWNER123"
        )
        session.add(owner)
        
        services = [
            Service(
                name="VPN Basic 1 Month",
                slug="vpn-basic-1m",
                type=ServiceType.VPN,
                price=100000,
                period=ServicePeriod.MONTHLY,
                is_active=True,
                spec_data={"bandwidth": "50GB", "devices": 2}
            ),
            Service(
                name="VPN Pro 1 Year",
                slug="vpn-pro-1y",
                type=ServiceType.VPN,
                price=1000000,
                period=ServicePeriod.ANNUAL,
                is_active=True,
                spec_data={"bandwidth": "Unlimited", "devices": 5}
            )
        ]
        for s in services:
            session.add(s)
        
        music = Music(
            title="Sample Song",
            artist="Sample Artist",
            genre="Pop",
            category="new",
            file_path="storage/music/sample.mp3",
            is_active=True
        )
        session.add(music)
        
        settings_list = [
            SystemSetting(key="system_name", value="TEOS", value_type="string"),
            SystemSetting(key="referral_bonus", value="5000", value_type="int"),
            SystemSetting(key="music_enabled", value="true", value_type="bool"),
        ]
        for s in settings_list:
            session.add(s)
        
        await session.commit()
        print("✅ Database seeded successfully")

if __name__ == "__main__":
    asyncio.run(seed())
