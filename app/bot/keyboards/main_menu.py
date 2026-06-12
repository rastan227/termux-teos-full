from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.models.user import UserRole

def get_main_menu_keyboard(role: UserRole) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🎵 موزیک"), KeyboardButton(text="🛒 سرویس‌ها")],
        [KeyboardButton(text="💰 کیف پول"), KeyboardButton(text="🎫 پشتیبانی")],
        [KeyboardButton(text="👤 پروفایل"), KeyboardButton(text="⭐ دعوت دوستان")],
    ]
    if role in [UserRole.MUSIC_ADMIN, UserRole.SUPER_ADMIN, UserRole.OWNER]:
        buttons.append([KeyboardButton(text="🎛️ پنل مدیریت موزیک")])
    if role in [UserRole.SERVICE_ADMIN, UserRole.SUPER_ADMIN, UserRole.OWNER]:
        buttons.append([KeyboardButton(text="📦 پنل مدیریت سرویس")])
    if role == UserRole.OWNER:
        buttons.append([KeyboardButton(text="⚙️ پنل مالک")])
    
    buttons.append([KeyboardButton(text="❓ راهنما"), KeyboardButton(text="ℹ️ درباره")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_inline_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار", callback_data="admin_stats"),
         InlineKeyboardButton(text="👥 کاربران", callback_data="admin_users")],
        [InlineKeyboardButton(text="🎵 مدیریت موزیک", callback_data="admin_music"),
         InlineKeyboardButton(text="🛒 مدیریت سفارشات", callback_data="admin_orders")],
        [InlineKeyboardButton(text="💰 درخواست‌های شارژ", callback_data="admin_payments"),
         InlineKeyboardButton(text="🎫 تیکت‌ها", callback_data="admin_tickets")],
        [InlineKeyboardButton(text="🔙 خروج", callback_data="main_menu")]
    ])

def get_owner_inline_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 مدیریت Tenant‌ها", callback_data="owner_tenants"),
         InlineKeyboardButton(text="🧩 پلاگین‌ها", callback_data="owner_plugins")],
        [InlineKeyboardButton(text="🔄 به‌روزرسانی سیستم", callback_data="owner_update"),
         InlineKeyboardButton(text="💾 پشتیبان", callback_data="owner_backup")],
        [InlineKeyboardButton(text="⚙️ تنظیمات عمومی", callback_data="owner_settings"),
         InlineKeyboardButton(text="👑 مدیریت ادمین‌ها", callback_data="owner_admins")],
        [InlineKeyboardButton(text="🔙 خروج", callback_data="main_menu")]
    ])
