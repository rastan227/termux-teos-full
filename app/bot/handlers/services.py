from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.services.service_catalog import ServiceCatalogService
from app.services.wallet_service import WalletService
from app.services.order_service import OrderService
from app.bot.states.order_states import OrderStates
from app.core.config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("services"))
async def cmd_services(message: types.Message):
    if not settings.FEATURE_VPN_ENABLED:
        await message.answer("❌ بخش سرویس‌ها در حال حاضر غیرفعال است.")
        return
    
    services = await ServiceCatalogService.get_all_services(page=1, limit=10)
    if not services["items"]:
        await message.answer("هیچ سرویسی یافت نشد.")
        return
    
    text = "🛒 **خدمات و سرویس‌های موجود**\n\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for s in services["items"]:
        text += f"🔹 **{s['name']}** - {s['price']:,} تومان\n"
        kb.inline_keyboard.append([InlineKeyboardButton(text=f"📦 {s['name']}", callback_data=f"service_{s['id']}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 منوی اصلی", callback_data="main_menu")])
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@router.callback_query(F.data.startswith("service_"))
async def service_detail(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    service = await ServiceCatalogService.get_service_by_id(service_id)
    if not service:
        await callback.answer("سرویس یافت نشد.", show_alert=True)
        return
    
    await state.update_data(service_id=service_id, price=service.price)
    
    text = (
        f"📦 **{service.name}**\n\n"
        f"📝 {service.description or 'توضیحاتی موجود نیست'}\n"
        f"💰 قیمت: {service.price:,} تومان\n"
        f"📆 دوره: {service.period}\n"
        f"📊 موجودی: {'نامحدود' if service.stock == -1 else service.stock}\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 خرید", callback_data=f"buy_{service.id}"),
         InlineKeyboardButton(text="🔙 بازگشت", callback_data="services_back")],
        [InlineKeyboardButton(text="🎁 درخواست تست (در صورت وجود)", callback_data=f"test_{service.id}")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def start_purchase(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    service = await ServiceCatalogService.get_service_by_id(service_id)
    if not service or not service.is_active:
        await callback.answer("سرویس غیرفعال است.", show_alert=True)
        return
    
    await state.update_data(service_id=service_id)
    # Ask for quantity if service allows >1
    if service.max_per_user > 1:
        await callback.message.answer("تعداد مورد نیاز را وارد کنید (پیش‌فرض ۱):")
        await state.set_state(OrderStates.waiting_for_quantity)
    else:
        await state.update_data(quantity=1)
        await confirm_purchase(callback, state)
    await callback.answer()

async def confirm_purchase(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_id = data["service_id"]
    quantity = data.get("quantity", 1)
    service = await ServiceCatalogService.get_service_by_id(service_id)
    total = service.price * quantity
    user_id = callback.from_user.id
    balance = await WalletService.get_balance(user_id)
    
    if balance["available"] < total:
        await callback.message.answer(f"❌ موجودی کیف پول شما کافی نیست. نیاز: {total:,} تومان - موجودی: {balance['available']:,} تومان\nلطفاً کیف پول خود را شارژ کنید.")
        return
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تأیید خرید", callback_data="confirm_purchase"),
         InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_purchase")]
    ])
    await callback.message.edit_text(f"🛒 **تأیید خرید**\n\nسرویس: {service.name}\nتعداد: {quantity}\nقیمت کل: {total:,} تومان\n\nآیا برای خرید تأیید می‌کنید؟", reply_markup=kb)

@router.callback_query(F.data == "confirm_purchase")
async def process_purchase(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order = await OrderService.create_order(
        user_id=callback.from_user.id,
        service_id=data["service_id"],
        quantity=data.get("quantity", 1)
    )
    if order:
        await callback.message.edit_text(f"✅ سفارش شما با شماره {order.order_number} ثبت شد. در حال پردازش...")
        # پردازش خودکار تحویل سرویس
        delivered = await OrderService.deliver_order(order.id)
        if delivered:
            await callback.message.answer(f"🎉 سرویس شما فعال شد. جزئیات ارسال شد.")
    else:
        await callback.message.edit_text("❌ خطا در ثبت سفارش. لطفاً بعداً تلاش کنید.")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "services_back")
async def back_to_services(callback: CallbackQuery):
    await cmd_services(callback.message)
    await callback.answer()
