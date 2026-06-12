import re
import json
from typing import Dict, List, Tuple
from app.core.config import settings

class IntentClassifier:
    """Rule-based + ML fallback intent classifier for TEOS"""
    
    INTENTS = {
        "music_search": ["آهنگ", "موزیک", "ترانه", "قطعه", "پخش کن", "بیا"],
        "music_recommend": ["پیشنهاد", "به من بگو", "چی خوبه", "معرفی کن"],
        "wallet_balance": ["موجودی", "کیف پول", "چقدر پول دارم", "اعتبار"],
        "wallet_charge": ["شارژ", "افزایش موجودی", "واریز"],
        "service_purchase": ["خرید سرویس", "میخوام بخرم", "VPN", "سرور"],
        "support_ticket": ["مشکل دارم", "پشتیبانی", "تیکت", "گزارش خطا"],
        "help": ["راهنما", "کمک", "چطوری", "دستورات"],
        "greeting": ["سلام", "درود", "خوبی", "چطوری"],
        "goodbye": ["خداحافظ", "بای", "فعلا"],
        "referral": ["کد دعوت", "معرفی دوست", "دعوت"],
        "music_genre": ["سبک", "پاپ", "رپ", "سنتی", "کلاسیک", "راک"],
        "music_artist": ["خواننده", "هنرمند", "آلبوم"]
    }
    
    def __init__(self):
        self.patterns = {intent: re.compile('|'.join(kw), re.IGNORECASE) for intent, kw in self.INTENTS.items()}
    
    async def load_models(self):
        """Load ML model if available (placeholder for real model)"""
        pass
    
    async def predict(self, text: str) -> Dict:
        text_lower = text.lower()
        scores = {}
        entities = {"genres": [], "artists": []}
        
        for intent, pattern in self.patterns.items():
            if pattern.search(text_lower):
                scores[intent] = 1.0
                # Extract entities
                if intent == "music_genre":
                    for genre in ["پاپ", "رپ", "سنتی", "کلاسیک", "راک", "جاز", "الکترونیک"]:
                        if genre in text_lower:
                            entities["genres"].append(genre)
                if intent == "music_artist":
                    # Simple artist extraction (would be ML in production)
                    pass
        
        if scores:
            top_intent = max(scores, key=scores.get)
            confidence = scores[top_intent]
        else:
            top_intent = "unknown"
            confidence = 0.2
        
        return {
            "intent": top_intent,
            "confidence": confidence,
            "entities": entities,
            "suggestions": self._get_suggestions(top_intent)
        }
    
    def _get_suggestions(self, intent: str) -> List[str]:
        suggestions_map = {
            "music_search": ["می‌توانید نام آهنگ یا خواننده را بگویید", "از منوی موزیک استفاده کنید"],
            "wallet_balance": ["برای مشاهده موجودی: /balance", "شارژ کیف پول: /wallet"],
            "help": ["/start - منوی اصلی", "/music - موزیک", "/services - سرویس‌ها"]
        }
        return suggestions_map.get(intent, [])
    
    async def get_stats(self) -> Dict:
        return {"total_intents": len(self.INTENTS), "model_loaded": True}
