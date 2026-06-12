"""Analytics plugin for TEOS - provides advanced stats"""
from app.plugins.base_plugin import BasePlugin
from aiogram import Router, types
from aiogram.filters import Command
from app.services.stats_service import StatsService
from app.core.database import async_session_maker
from app.models.user import User, UserRole
from app.models.order import Order
from app.models.transaction import Transaction
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("advanced_stats"))
async def advanced_stats(message: types.Message):
    # Check if user is admin
    user_id = message.from_user.id
    async with async_session_maker() as session:
        user = await session.get(User, user_id)
        if not user or not user.is_admin():
            await message.answer("⛔ دسترسی غیرمجاز")
            return
    
    # Gather stats
    daily = await StatsService.get_daily_stats()
    top_services = await StatsService.get_top_services(5)
    top_songs = await StatsService.get_top_songs(5)
    system_metrics = await StatsService.get_system_metrics()
    
    text = (
        f"📈 **آمار پیشرفته TEOS**\n\n"
        f"📊 **آمار روزانه:**\n"
        f"کاربران جدید: {daily['new_users']}\n"
        f"سفارشات جدید: {daily['new_orders']}\n"
        f"درآمد: {daily['revenue']:,} تومان\n"
        f"پخش موزیک: {daily['music_plays']}\n\n"
        f"🎵 **آهنگ‌های برتر:**\n"
    )
    for idx, s in enumerate(top_songs[:3], 1):
        text += f"{idx}. {s['title']} - {s['artist']} ({s['plays']} پخش)\n"
    text += f"\n🛒 **سرویس‌های پرفروش:**\n"
    for idx, s in enumerate(top_services[:3], 1):
        text += f"{idx}. سرویس {s['service_id']} - {s['order_count']} سفارش\n"
    text += f"\n💻 **متریک‌های سیستم:**\n"
    text += f"CPU: {system_metrics.get('cpu_usage_percent', 0)}%\n"
    text += f"RAM: {system_metrics.get('memory_usage_mb', 0)} MB\n"
    text += f"API requests today: {system_metrics.get('total_api_requests_today', 0)}\n"
    
    await message.answer(text, parse_mode="Markdown")

class AnalyticsPlugin(BasePlugin):
    name = "analytics_plugin"
    display_name = "Advanced Analytics"
    version = "1.0.0"
    author = "TEOS Team"
    description = "Provides advanced analytics and reporting"
    
    async def on_install(self):
        logger.info("Analytics plugin installed")
        return True
    
    async def on_enable(self):
        logger.info("Analytics plugin enabled")
        from app.bot.dispatcher import dp
        dp.include_router(router)
        return True
    
    async def on_disable(self):
        logger.info("Analytics plugin disabled")
        from app.bot.dispatcher import dp
        if router in dp.router.routers:
            dp.router.routers.remove(router)
        return True
    
    async def on_uninstall(self):
        logger.info("Analytics plugin uninstalled")
        return True
