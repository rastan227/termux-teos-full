from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.services.music_service import MusicService
from app.services.ai_service import AIService
from app.bot.keyboards.music_keyboards import (
    get_music_categories_keyboard, get_music_pagination_keyboard,
    get_song_detail_keyboard, get_search_keyboard, get_now_playing_keyboard
)
from app.bot.states.music_states import MusicStates
from app.core.config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("music"))
async def cmd_music(message: types.Message):
    if not settings.FEATURE_MUSIC_ENABLED:
        await message.answer("❌ بخش موزیک در حال حاضر غیرفعال است.")
        return
    await message.answer("🎵 **کتابخانه موزیک TEOS**\n\nلطفاً دسته مورد نظر را انتخاب کنید:", 
                         parse_mode="Markdown", 
                         reply_markup=get_music_categories_keyboard())

@router.callback_query(F.data == "music_categories")
async def show_categories(callback: CallbackQuery):
    await callback.message.edit_text("🎵 **دسته‌بندی موزیک:**", 
                                     reply_markup=get_music_categories_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("music_cat_"))
async def music_category_callback(callback: CallbackQuery, page: int = 1):
    category = callback.data.split("_")[-1]
    data = await MusicService.get_songs_by_category(category, page=page, limit=8)
    if not data["items"]:
        await callback.answer("هیچ آهنگی در این دسته یافت نشد.", show_alert=True)
        return
    
    text = f"🎶 **لیست آهنگ‌ها - {category}** (صفحه {page}/{data['pages']})\n\n"
    for idx, song in enumerate(data["items"], 1):
        text += f"{idx}. 🎵 {song['title']} - {song['artist']} ⭐ {song['likes']} ❤️\n"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for song in data["items"]:
        kb.inline_keyboard.append([InlineKeyboardButton(text=f"🎵 {song['title'][:30]}", callback_data=f"song_{song['id']}")])
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ قبلی", callback_data=f"music_cat_{category}_page_{page-1}"))
    if page < data["pages"]:
        nav_buttons.append(InlineKeyboardButton(text="بعدی ➡️", callback_data=f"music_cat_{category}_page_{page+1}"))
    if nav_buttons:
        kb.inline_keyboard.append(nav_buttons)
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔍 جستجو", callback_data="music_search"),
                              InlineKeyboardButton(text="🎲 تصادفی", callback_data="music_random")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🎵 پیشنهاد هوشمند", callback_data="music_recommend")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="main_menu")])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("song_"))
async def song_detail(callback: CallbackQuery):
    song_id = int(callback.data.split("_")[1])
    song = await MusicService.get_song_by_id(song_id)
    if not song:
        await callback.answer("آهنگ یافت نشد.", show_alert=True)
        return
    
    await MusicService.record_play(callback.from_user.id, song_id)
    
    text = (
        f"🎤 **{song.title}**\n"
        f"👨‍🎤 خواننده: {song.artist}\n"
        f"🎵 سبک: {song.genre}\n"
        f"⏱️ مدت: {song.duration // 60}:{song.duration % 60:02d}\n"
        f"⭐ امتیاز: {song.avg_rating:.1f}/5\n"
        f"📀 پخش: {song.plays}\n"
        f"❤️ لایک: {song.likes}\n"
        f"📥 دانلود: {song.downloads}\n"
    )
    if song.lyrics:
        text += f"\n📝 متن (بخشی): {song.lyrics[:150]}..."
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_song_detail_keyboard(song_id))
    await callback.answer()

@router.callback_query(F.data.startswith("download_"))
async def download_song(callback: CallbackQuery):
    song_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    # Permission check: only users who have paid or free songs
    can_download = await MusicService.can_download(user_id, song_id)
    if not can_download:
        await callback.answer("⛔ شما مجوز دانلود این آهنگ را ندارید. از کیف پول خود استفاده کنید.", show_alert=True)
        return
    
    song = await MusicService.get_song_by_id(song_id)
    file_url = await MusicService.get_download_url(song_id, user_id)
    if file_url:
        await callback.message.answer_document(document=file_url, caption=f"🎵 {song.title} - {song.artist}")
        await MusicService.increment_downloads(song_id, user_id)
        await callback.answer("✅ دانلود شروع شد.", show_alert=False)
    else:
        await callback.answer("❌ خطا در دریافت فایل.", show_alert=True)

@router.callback_query(F.data.startswith("like_"))
async def like_song(callback: CallbackQuery):
    song_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    result = await MusicService.like_song(user_id, song_id)
    if result:
        await callback.answer("❤️ آهنگ مورد علاقه شما ثبت شد.", show_alert=False)
        # Update message to show liked
        await callback.message.edit_reply_markup(reply_markup=get_song_detail_keyboard(song_id, liked=True))
    else:
        await callback.answer("شما قبلاً این آهنگ را لایک کرده‌اید.", show_alert=False)

@router.callback_query(F.data == "music_search")
async def search_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔍 **لطفاً نام آهنگ، خواننده یا سبک را وارد کنید:**", parse_mode="Markdown")
    await state.set_state(MusicStates.waiting_for_search_query)
    await callback.answer()

@router.message(MusicStates.waiting_for_search_query)
async def process_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("لطفاً حداقل ۲ کاراکتر وارد کنید.")
        return
    
    results = await MusicService.search_songs(query, page=1)
    if not results["items"]:
        await message.answer("❌ هیچ نتیجه‌ای برای جستجوی شما یافت نشد.")
    else:
        text = f"🔎 **نتایج جستجو برای '{query}':**\n\n"
        kb = InlineKeyboardMarkup(inline_keyboard=[])
        for song in results["items"][:15]:
            kb.inline_keyboard.append([InlineKeyboardButton(text=f"🎵 {song['title']} - {song['artist']}", callback_data=f"song_{song['id']}")])
        kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="music_categories")])
        await message.answer(text, parse_mode="Markdown", reply_markup=kb)
    await state.clear()

@router.callback_query(F.data == "music_random")
async def random_song(callback: CallbackQuery):
    song = await MusicService.get_random_song()
    if song:
        await callback.message.edit_text("🎲 **آهنگ تصادفی:**")
        # show detail
        await song_detail(callback)  # Need to create new callback with song_id
        # Simpler: create fake callback with song_id
        callback.data = f"song_{song.id}"
        await song_detail(callback)
    else:
        await callback.answer("هیچ آهنگی یافت نشد.", show_alert=True)

@router.callback_query(F.data == "music_recommend")
async def recommend_songs(callback: CallbackQuery):
    user_id = callback.from_user.id
    recs = await MusicService.get_recommendations(user_id, limit=5)
    if not recs:
        await callback.answer("پیشنهادی وجود ندارد.", show_alert=True)
        return
    text = "🤖 **پیشنهادات ویژه برای شما (بر اساس سلیقه و AI):**\n\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for idx, song in enumerate(recs, 1):
        text += f"{idx}. {song['title']} - {song['artist']}\n"
        kb.inline_keyboard.append([InlineKeyboardButton(text=f"🎵 {song['title']}", callback_data=f"song_{song['id']}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="music_categories")])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()

# Admin music management
@router.callback_query(F.data == "admin_music_panel")
async def admin_music_panel(callback: CallbackQuery):
    from app.bot.keyboards.admin_keyboards import get_admin_music_keyboard
    await callback.message.edit_text("🎛️ **پنل مدیریت موزیک**\n\nعملیات مورد نظر را انتخاب کنید:", 
                                     reply_markup=get_admin_music_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_music_add")
async def admin_add_song_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("➕ **افزودن آهنگ جدید**\n\nلطفاً اطلاعات آهنگ را به صورت زیر ارسال کنید:\n`عنوان | خواننده | سبک | دسته`\nمثال: `بهار | همایون شجریان | سنتی | new`")
    await state.set_state(MusicStates.waiting_for_song_title)
    await callback.answer()

@router.message(MusicStates.waiting_for_song_title)
async def admin_process_add_song_title(message: types.Message, state: FSMContext):
    # Store data and ask for file
    await state.update_data(song_info=message.text)
    await message.answer("📁 لطفاً فایل MP3 آهنگ را ارسال کنید.")
    await state.set_state(MusicStates.waiting_for_song_file)

@router.message(MusicStates.waiting_for_song_file, F.document)
async def admin_process_add_song_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    song_info = data.get("song_info", "").split("|")
    if len(song_info) < 4:
        await message.answer("❌ فرمت اطلاعات نامعتبر. لطفاً دوباره تلاش کنید.")
        await state.clear()
        return
    
    title = song_info[0].strip()
    artist = song_info[1].strip()
    genre = song_info[2].strip()
    category = song_info[3].strip()
    
    file = message.document
    file_path = f"storage/music/{file.file_id}.mp3"
    await message.bot.download_file(file.file_id, destination=file_path)
    
    song = await MusicService.add_song({
        "title": title,
        "artist": artist,
        "genre": genre,
        "category": category,
        "duration": 0  # Would need ffprobe to get duration
    }, file_path, message.from_user.id)
    
    await message.answer(f"✅ آهنگ '{title}' با موفقیت اضافه شد. شناسه: {song.id}")
    await state.clear()
