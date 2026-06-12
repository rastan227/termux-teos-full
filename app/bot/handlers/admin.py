from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.services.user_service import UserService
from app.services.music_service import MusicService
from app.services.wallet_service import WalletService
from app.services.ticket_service import TicketService
from app.services.notification_service import NotificationService
from app.bot.keyboards.admin_keyboards import get_admin_main_keyboard
from app.core.config import settings
from app.models.user import UserRole
import logging

router = Router()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    # In production, check role from DB
    from app.services.user_service import UserService
    import asyncio
    user = asyncio.run(UserService.get_user_by_telegram_id(user_id))
    return user and user.is_admin()

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    user = await UserService.get_user_by_telegram_id(message.from_user.id)
    if not user or not user.is_admin():
        await message.answer("⛔ شما دسترسی ادمین ندارید.")
        return
    await message.answer("🎛️ **پنل مدیریت**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                         parse_mode="Markdown", 
                         reply_markup=get_admin_main_keyboard(user.role))

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    user_stats = await UserService.get_user_stats()
    music_stats = await MusicService.get_admin_stats()
    text = (
        f"📊 **آمار سیستم**\n\n"
        f"👥 کاربران کل: {user_stats['total_users']}\n"
        f"🟢 فعال: {user_stats['active_users']}\n"
        f"🔴 مسدود: {user_stats['banned_users']}\n"
        f"👑 ادمین‌ها: {user_stats['admins']}\n\n"
        f"🎵 آهنگ‌ها: {music_stats['total_songs']}\n"
        f"▶️ پخش کل: {music_stats['total_plays']}\n"
        f"❤️ لایک: {music_stats['total_likes']}\n"
        f"📋 گزارش‌های در انتظار: {music_stats['pending_reports']}"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]]))
    await callback.answer()

@router.callback_query(F.data == "admin_payments")
async def admin_payments(callback: CallbackQuery):
    pending = await WalletService.get_pending_requests(callback.from_user.id, limit=20)
    if not pending:
        await callback.answer("هیچ درخواست شارژ در انتظاری وجود ندارد.", show_alert=True)
        return
    text = "💰 **درخواست‌های شارژ در انتظار:**\n\n"
    for req in pending:
        text += f"🔹 ID: {req['id']} | کاربر: {req['user_id']} | مبلغ: {req['amount']:,} تومان | روش: {req['method']}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"تأیید {req['id']}", callback_data=f"approve_payment_{req['id']}"),
         InlineKeyboardButton(text=f"رد {req['id']}", callback_data=f"reject_payment_{req['id']}")] for req in pending[:5]
    ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("approve_payment_"))
async def approve_payment(callback: CallbackQuery):
    request_id = int(callback.data.split("_")[-1])
    success = await WalletService.approve_payment_request(request_id, callback.from_user.id)
    if success:
        await callback.answer("✅ درخواست شارژ تأیید شد.", show_alert=True)
        await admin_payments(callback)  # Refresh
    else:
        await callback.answer("❌ خطا در تأیید.", show_alert=True)

@router.callback_query(F.data == "admin_tickets")
async def admin_tickets(callback: CallbackQuery):
    tickets = await TicketService.get_all_tickets_for_admin(status="open", page=1, limit=10)
    if not tickets["items"]:
        await callback.answer("تیکت باز وجود ندارد.", show_alert=True)
        return
    text = "🎫 **تیکت‌های باز:**\n\n"
    for t in tickets["items"]:
        text += f"#{t['number']} | {t['subject']} | اولویت: {t['priority']}\n"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"مشاهده تیکت {t['number']}", callback_data=f"view_ticket_{t['id']}") for t in tickets["items"][:3]],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
    ]))
    await callback.answer()
