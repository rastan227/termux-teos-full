from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.services.ticket_service import TicketService
from app.bot.states.support_states import SupportStates
from app.services.notification_service import NotificationService
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("ticket"))
async def cmd_ticket(message: types.Message, state: FSMContext):
    await message.answer("🎫 **پشتیبانی**\n\nلطفاً موضوع تیکت خود را وارد کنید:")
    await state.set_state(SupportStates.waiting_for_subject)

@router.message(SupportStates.waiting_for_subject)
async def ticket_subject(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("لطفاً شرح مشکل خود را بنویسید:")
    await state.set_state(SupportStates.waiting_for_message)

@router.message(SupportStates.waiting_for_message)
async def ticket_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ticket = await TicketService.create_ticket(
        telegram_id=message.from_user.id,
        subject=data["subject"],
        message=message.text
    )
    if ticket:
        await message.answer(f"✅ تیکت شما با شماره {ticket.ticket_number} ثبت شد. به زودی پاسخ داده می‌شود.")
        # اطلاع به ادمین‌ها
        await NotificationService.broadcast_to_admins(f"🎫 تیکت جدید: {ticket.ticket_number} از کاربر {message.from_user.id}")
    else:
        await message.answer("❌ خطا در ثبت تیکت. لطفاً بعداً تلاش کنید.")
    await state.clear()

@router.message(Command("mytickets"))
async def my_tickets(message: types.Message):
    tickets = await TicketService.get_user_tickets(message.from_user.id)
    if not tickets["items"]:
        await message.answer("هیچ تیکتی ثبت نکرده‌اید.")
        return
    text = "🎫 **لیست تیکت‌های شما:**\n\n"
    for t in tickets["items"]:
        text += f"#{t['number']} - {t['subject']} - وضعیت: {t['status']}\n"
    await message.answer(text)
