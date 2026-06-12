"""Sample plugin for TEOS"""
from app.plugins.base_plugin import BasePlugin
from aiogram import Router, types
from aiogram.filters import Command
from app.core.database import async_session_maker
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("plugin_test"))
async def plugin_test(message: types.Message):
    await message.answer("✅ پلاگین نمونه با موفقیت کار می‌کند!")

@router.message(Command("plugin_stats"))
async def plugin_stats(message: types.Message):
    async with async_session_maker() as session:
        from sqlalchemy import select, func
        result = await session.execute(select(func.count()).select_from(User))
        count = result.scalar()
    await message.answer(f"📊 تعداد کاربران: {count}")

class SamplePlugin(BasePlugin):
    name = "sample_plugin"
    display_name = "Sample Plugin"
    version = "1.0.0"
    author = "TEOS Team"
    description = "A sample plugin demonstrating TEOS plugin system"
    
    async def on_install(self):
        logger.info("Sample plugin installed")
        # Create any plugin-specific tables here
        return True
    
    async def on_enable(self):
        logger.info("Sample plugin enabled")
        from app.bot.dispatcher import dp
        dp.include_router(router)
        return True
    
    async def on_disable(self):
        logger.info("Sample plugin disabled")
        from app.bot.dispatcher import dp
        if router in dp.router.routers:
            dp.router.routers.remove(router)
        return True
    
    async def on_uninstall(self):
        logger.info("Sample plugin uninstalled")
        return True
