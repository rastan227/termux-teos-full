from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.services.wallet_service import WalletService
from app.services.payment_service import PaymentService
from app.bot.states.wallet_states import WalletStates
from app.core.config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("wallet"))
async def cmd_wallet(message: types.Message):
    user_id = message.from_user.id
    balance_info = await WalletService.get_balance(user_id)
    text = (
        f"💰 **کیف پول شما**\n\n"
        f"موجودی کل: {balance_info['balance']:,} تومان\n"
        f"موجودی در انتظار: {balance_info['hold']:,} تومان\n"
        f"موجودی قابل استفاده: {balance_info['available']:,} تومان\n\n"
        f"⬇️ برای شارژ کیف پول از دکمه زیر استفاده کنید."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 شارژ کیف پول", callback_data="wallet_charge")],
        [InlineKeyboardButton(text="📜 تاریخچه تراکنش‌ها", callback_data="wallet_history")],
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
    ])
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@router.callback_query(F.data == "wallet_charge")
async def wallet_charge(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💰 **شارژ کیف پول**\n\nلطفاً مبلغ مورد نظر (به تومان) را وارد کنید:\nحداقل شارژ: ۱۰,۰۰۰ تومان")
    await state.set_state(WalletStates.waiting_for_amount)
    await callback.answer()

@router.message(WalletStates.waiting_for_amount)
async def process_charge_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.replace(",", ""))
        if amount < 10000:
            await message.answer("❌ حداقل مبلغ شارژ ۱۰,۰۰۰ تومان است.")
            return
        await state.update_data(amount=amount)
        
        # Show payment methods
        methods = ["کارت به کارت", "درگاه پرداخت آنلاین (در حال توسعه)", "ارسال رسید دستی"]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=m, callback_data=f"pay_method_{i}")] for i, m in enumerate(methods)
        ])
        await message.answer("روش پرداخت را انتخاب کنید:", reply_markup=kb)
        await state.set_state(WalletStates.waiting_for_payment_method)
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید.")

@router.callback_query(F.data.startswith("pay_method_"))
async def process_payment_method(callback: CallbackQuery, state: FSMContext):
    method_index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    amount = data.get("amount")
    
    if method_index == 0:  # کارت به کارت
        # Mock payment info
        await callback.message.edit_text(
            f"💳 **اطلاعات کارت به کارت**\n\n"
            f"مبلغ: {amount:,} تومان\n"
            f"شماره کارت: `6037-9975-1234-5678`\n"
            f"به نام: TEOS Enterprise\n"
            f"شماره شبا: `IR123456789012345678901234`\n\n"
            f"پس از واریز، رسید را ارسال کنید."
        )
        await callback.message.answer("لطفاً تصویر رسید را ارسال کنید:")
        await state.set_state(WalletStates.waiting_for_receipt)
    else:
        await callback.answer("این روش در حال راه‌اندازی است.", show_alert=True)
    await callback.answer()

@router.message(WalletStates.waiting_for_receipt, F.photo)
async def process_receipt(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    data = await state.get_data()
    amount = data.get("amount")
    
    # Save receipt request
    receipt_url = f"https://t.me/teos_bot?file_id={file_id}"  # Simplified
    payment_request = await PaymentService.create_payment_request(
        user_id=message.from_user.id,
        amount=amount,
        method="card",
        receipt_image=receipt_url
    )
    await message.answer(f"✅ درخواست شارژ شما ثبت شد. کد پیگیری: {payment_request.id}\nپس از تأیید ادمین، موجودی شما افزایش می‌یابد.")
    await state.clear()

@router.callback_query(F.data == "wallet_history")
async def wallet_history(callback: CallbackQuery, page: int = 1):
    user_id = callback.from_user.id
    data = await WalletService.get_transactions(user_id, page=page, limit=10)
    if not data["items"]:
        await callback.answer("هیچ تراکنشی یافت نشد.", show_alert=True)
        return
    text = f"📜 **تاریخچه تراکنش‌ها** (صفحه {page}/{data['pages']})\n\n"
    for tx in data["items"]:
        sign = "+" if tx["amount"] > 0 else ""
        text += f"{tx['created_at'][:10]} - {sign}{tx['amount']:,} تومان - {tx['description']}\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    if page > 1:
        kb.inline_keyboard.append([InlineKeyboardButton(text="⬅️ قبلی", callback_data=f"wallet_history_page_{page-1}")])
    if page < data["pages"]:
        kb.inline_keyboard.append([InlineKeyboardButton(text="بعدی ➡️", callback_data=f"wallet_history_page_{page+1}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="wallet_back")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()
