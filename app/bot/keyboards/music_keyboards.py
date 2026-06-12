from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_music_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 جدیدترین", callback_data="music_cat_new"),
         InlineKeyboardButton(text="🔥 محبوب‌ترین", callback_data="music_cat_popular")],
        [InlineKeyboardButton(text="📈 ترند", callback_data="music_cat_trending"),
         InlineKeyboardButton(text="🎲 تصادفی", callback_data="music_random")],
        [InlineKeyboardButton(text="🎵 سبک‌ها", callback_data="music_genres"),
         InlineKeyboardButton(text="🔍 جستجو", callback_data="music_search")],
        [InlineKeyboardButton(text="🤖 پیشنهاد AI", callback_data="music_recommend"),
         InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu")]
    ])

def get_music_genres_keyboard() -> InlineKeyboardMarkup:
    genres = ["پاپ", "رپ", "سنتی", "کلاسیک", "الکترونیک", "راک", "جاز", "بلوز"]
    buttons = []
    for genre in genres:
        buttons.append([InlineKeyboardButton(text=genre, callback_data=f"music_genre_{genre}")])
    buttons.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="music_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_song_detail_keyboard(song_id: int, liked: bool = False) -> InlineKeyboardMarkup:
    like_text = "❤️ لایک" if not liked else "✅ لایک شده"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬇️ دانلود", callback_data=f"download_{song_id}"),
         InlineKeyboardButton(text=like_text, callback_data=f"like_{song_id}")],
        [InlineKeyboardButton(text="🎶 پلی لیست", callback_data="playlist_add"),
         InlineKeyboardButton(text="📢 گزارش", callback_data=f"report_{song_id}")],
        [InlineKeyboardButton(text="🔙 بازگشت به لیست", callback_data="music_categories")]
    ])
    return kb

def get_now_playing_keyboard(song_id: int, is_playing: bool = True) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏸️ توقف", callback_data="pause"),
         InlineKeyboardButton(text="⏭️ بعدی", callback_data="next")],
        [InlineKeyboardButton(text="📥 دانلود", callback_data=f"download_{song_id}")]
    ])
