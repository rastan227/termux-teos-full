#!/usr/bin/env python3
"""Initialize database with default data for TEOS"""

import asyncio
from app.core.database import engine, Base
from app.models.user import User, UserRole
from app.models.service import Service, ServiceType, ServicePeriod
from app.models.settings import SystemSetting
from app.services.user_service import UserService

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create owner user
    owner = await UserService.get_or_create(
        telegram_id=123456789,  # Change this
        username="owner",
        first_name="Owner",
        last_name="TEOS"
    )
    owner.role = UserRole.OWNER
    owner.wallet_balance = 0
    
    # Create default services
    service1 = Service(
        name="VPN Pro 1 Month",
        slug="vpn-pro-1m",
        description="VPN با سرعت بالا و پشتیبانی از ۵ دستگاه",
        type=ServiceType.VPN,
        category="vpn",
        price=150000,
        period=ServicePeriod.MONTHLY,
        spec_data={"bandwidth": "Unlimited", "servers": 50, "devices": 5},
        is_active=True
    )
    service2 = Service(
        name="VPN Pro 1 Year",
        slug="vpn-pro-1y",
        price=1500000,
        period=ServicePeriod.ANNUAL,
        is_active=True
    )
    
    async with engine.begin() as conn:
        from sqlalchemy import insert
        await conn.execute(insert(Service), [service1.__dict__, service2.__dict__])
    
    # Create default settings
    settings_data = [
        ("system_name", "TEOS", "string", "System display name"),
        ("music_enabled", "true", "bool", "Enable music module"),
        ("wallet_enabled", "true", "bool", "Enable wallet module"),
        ("referral_bonus", "5000", "int", "Referral bonus amount"),
    ]
    for key, value, vtype, desc in settings_data:
        setting = SystemSetting(key=key, value=value, value_type=vtype, description=desc)
        # Insert logic
    
    print("✅ Database initialized with default data")

if __name__ == "__main__":
    asyncio.run(init())
