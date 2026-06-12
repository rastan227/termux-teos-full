from typing import Dict, List, Optional
from app.services.music_service import MusicService
from app.services.wallet_service import WalletService
from app.core.config import settings

class ResponseGenerator:
    """Generate contextual responses based on intent and user data"""
    
    async def generate(self, intent: str, entities: Dict, user_id: int, memory: Dict, context: Dict) -> str:
        if intent == "music_search":
            query = entities.get("query", "")
            results = await MusicService.search_songs(query, page=1)
            if results["items"]:
                return f"🎵 نتایج جستجو برای '{query}':\n" + "\n".join([f"- {s['title']} - {s['artist']}" for s in results["items"][:5]])
            else:
                return f"هیچ آهنگی برای '{query}' یافت نشد. لطفاً عبارت دیگری را جستجو کنید."
        
        elif intent == "music_recommend":
            recs = await MusicService.get_recommendations(user_id, limit=5)
            if recs:
                return "🤖 پیشنهادات ویژه برای شما:\n" + "\n".join([f"- {s['title']} - {s['artist']}" for s in recs])
            else:
                return "در حال حاضر پیشنهادی ندارم. لطفاً بعداً تلاش کنید."
        
        elif intent == "wallet_balance":
            balance = await WalletService.get_balance(user_id)
            return f"💰 موجودی کیف پول شما: {balance['balance']:,} تومان\nقابل برداشت: {balance['available']:,} تومان"
        
        elif intent == "wallet_charge":
            return "برای شارژ کیف پول، لطفاً از منوی کیف پول استفاده کنید یا دستور /wallet را وارد کنید."
        
        elif intent == "service_purchase":
            return "برای مشاهده و خرید سرویس‌ها، از دستور /services استفاده کنید."
        
        elif intent == "support_ticket":
            return "برای ایجاد تیکت پشتیبانی، از دستور /ticket استفاده کنید."
        
        elif intent == "greeting":
            return f"سلام! خوش برگشتی. چطور می‌توانم به شما کمک کنم؟"
        
        elif intent == "goodbye":
            return "خداحافظ! برای بازگشت /start را بزنید."
        
        elif intent == "referral":
            user = await UserService.get_user_by_telegram_id(user_id)
            if user and user.referral_code:
                return f"کد دعوت شما: `{user.referral_code}`\nبا دعوت هر دوست، ۵,۰۰۰ تومان جایزه دریافت می‌کنید."
            return "کد دعوت شما موجود نیست. لطفاً با پشتیبانی تماس بگیرید."
        
        else:
            return "چطور می‌توانم به شما کمک کنم؟ از منوی اصلی استفاده کنید یا /help را بزنید."
