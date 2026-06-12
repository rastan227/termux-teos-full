from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.services.user_service import UserService
from app.bot.keyboards.main_menu import get_main_menu_keyboard
from app.core.config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    
    # Check if there's a referral code in the start parameter
    args = message.text.split()
    referrer_code = None
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_code = args[1][4:]
        await UserService.apply_referral(user_id, referrer_code)
    
    user = await UserService.get_or_create(user_id, username, first_name, last_name)
    
    welcome_text = (
        f"✨ **به TEOS خوش آمدید** {first_name}! ✨\n\n"
        "🔹 **سیستم عامل سازمانی مبتنی بر Telegram**\n"
        "🔹 **پخش موزیک با کیفیت**\n"
        "🔹 **خرید سرویس‌های VPN و سرور**\n"
        "🔹 **کیف پول هوشمند**\n"
        "🔹 **پشتیبانی ۲۴ ساعته**\n\n"
        "لطفاً یکی از بخش‌های زیر را انتخاب کنید:"
    )
    
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard(user.role))
    logger.info(f"User {user_id} started the bot")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📚 **راهنمای جامع TEOS** 📚\n\n"
        "**دستورات عمومی:**\n"
        "/start - منوی اصلی\n"
        "/music - بخش موزیک\n"
        "/services - خدمات و سرویس‌ها\n"
        "/wallet - کیف پول\n"
        "/ticket - پشتیبانی\n"
        "/profile - مشاهده پروفایل\n"
        "/balance - نمایش موجودی\n\n"
        "**دستورات مدیریتی (فقط ادمین):**\n"
        "/admin - پنل مدیریت\n"
        "/stats - آمار سیستم\n\n"
        "**پشتیبانی:**\n"
        "در صورت نیاز به راهنمایی، تیکت پشتیبانی ایجاد کنید.\n\n"
        "🌐 **پنل وب:** admin.teos.local"
    )
    await message.answer(help_text, parse_mode="Markdown")

@router.message(Command("profile"))
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    user = await UserService.get_user_by_telegram_id(user_id)
    if not user:
        await message.answer("کاربر یافت نشد. لطفاً دوباره /start را بزنید.")
        return
    
    profile_text = (
        f"👤 **پروفایل کاربری**\n\n"
        f"🔹 نام: {user.first_name} {user.last_name or ''}\n"
        f"🔹 نام کاربری: @{user.username or 'ندارد'}\n"
        f"🔹 نقش: {user.role.value}\n"
        f"🔹 موجودی کیف پول: {user.wallet_balance:,} تومان\n"
        f"🔹 کل خریدها: {user.total_orders}\n"
        f"🔹 دانلودها: {user.total_downloads}\n"
        f"🔹 کد دعوت: `{user.referral_code}`\n"
        f"🔹 تعداد دعوت‌ها: {user.referral_count}\n\n"
        f"📅 تاریخ عضویت: {user.created_at.strftime('%Y-%m-%d')}"
    )
    await message.answer(profile_text, parse_mode="Markdown")

@router.message(Command("balance"))
async def cmd_balance(message: types.Message):
    from app.services.wallet_service import WalletService
    balance_info = await WalletService.get_balance(message.from_user.id)
    text = f"💰 **موجودی کیف پول شما:**\n\nموجودی کل: {balance_info['balance']:,} تومان\nدر انتظار: {balance_info['hold']:,} تومان\nقابل برداشت: {balance_info['available']:,} تومان"
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "🔙 بازگشت")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    user = await UserService.get_user_by_telegram_id(message.from_user.id)
    await message.answer("منوی اصلی:", reply_markup=get_main_menu_keyboard(user.role))
