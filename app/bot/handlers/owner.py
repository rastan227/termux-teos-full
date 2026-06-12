from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.services.user_service import UserService
from app.services.plugin_service import PluginService
from app.services.backup_service import BackupService
from app.services.auto_update_service import AutoUpdateService
from app.core.config import settings
from app.models.user import UserRole

router = Router()

def is_owner(user_id: int) -> bool:
    # در تولید از دیتابیس چک می‌شود
    return user_id in settings.ADMIN_IDS  # Simplified

@router.message(Command("owner"))
async def cmd_owner(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("⛔ دسترسی غیرمجاز.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 مدیریت ادمین‌ها", callback_data="owner_admins")],
        [InlineKeyboardButton(text="🧩 مدیریت پلاگین‌ها", callback_data="owner_plugins")],
        [InlineKeyboardButton(text="💾 پشتیبان و بازیابی", callback_data="owner_backup")],
        [InlineKeyboardButton(text="🔄 به‌روزرسانی سیستم", callback_data="owner_update")],
        [InlineKeyboardButton(text="⚙️ تنظیمات سیستم", callback_data="owner_settings")],
        [InlineKeyboardButton(text="📊 مانیتورینگ", callback_data="owner_monitoring")]
    ])
    await message.answer("⚙️ **پنل مالک**", reply_markup=kb)

@router.callback_query(F.data == "owner_admins")
async def owner_admins(callback: CallbackQuery):
    admins = await UserService.get_all_users(role=UserRole.SUPER_ADMIN)
    text = "👑 **لیست ادمین‌ها:**\n\n"
    for a in admins["items"]:
        text += f"🔹 {a['first_name']} (@{a['username']}) - نقش: {a['role']}\n"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ افزودن ادمین", callback_data="add_admin")], [InlineKeyboardButton(text="🔙 بازگشت", callback_data="owner_back")]]))
    await callback.answer()

@router.callback_query(F.data == "owner_plugins")
async def owner_plugins(callback: CallbackQuery):
    plugins = await PluginService.get_installed_plugins()
    text = "🧩 **پلاگین‌های نصب شده:**\n\n"
    for p in plugins:
        text += f"• {p['display_name']} v{p['version']} - {'فعال' if p['enabled'] else 'غیرفعال'}\n"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت", callback_data="owner_back")]]))
    await callback.answer()

@router.callback_query(F.data == "owner_backup")
async def owner_backup(callback: CallbackQuery):
    await callback.message.edit_text("💾 **مدیریت پشتیبان**\n\nدکمه زیر را برای ایجاد پشتیبان جدید بزنید:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📀 ایجاد پشتیبان", callback_data="create_backup")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="owner_back")]
    ]))
    await callback.answer()

@router.callback_query(F.data == "create_backup")
async def create_backup_action(callback: CallbackQuery):
    await callback.message.edit_text("در حال ایجاد پشتیبان... لطفاً صبر کنید.")
    backup_path = await BackupService.create_backup()
    await callback.message.edit_text(f"✅ پشتیبان با موفقیت ایجاد شد: {backup_path}")
    await callback.answer()

@router.callback_query(F.data == "owner_update")
async def owner_update(callback: CallbackQuery):
    await callback.message.edit_text("🔄 **به‌روزرسانی سیستم**\n\nآیا از انجام به‌روزرسانی مطمئن هستید؟", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ بله، به‌روزرسانی", callback_data="perform_update")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="owner_back")]
    ]))
    await callback.answer()

@router.callback_query(F.data == "perform_update")
async def perform_update(callback: CallbackQuery):
    await callback.message.edit_text("در حال به‌روزرسانی...")
    success = await AutoUpdateService.perform_update("")  # URL from config
    if success:
        await callback.message.edit_text("✅ به‌روزرسانی انجام شد. سرویس در حال ریستارت است.")
    else:
        await callback.message.edit_text("❌ خطا در به‌روزرسانی.")
    await callback.answer()
