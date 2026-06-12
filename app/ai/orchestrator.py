import logging
from typing import Dict, Any, List, Optional
from app.ai.intent_classifier import IntentClassifier
from app.ai.response_generator import ResponseGenerator
from app.ai.memory_manager import MemoryManager
from app.ai.recommendation_engine import RecommendationEngine
from app.ai.moderation_engine import ModerationEngine
from app.core.config import settings
from app.services.user_service import UserService
import json

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """Main AI orchestrator for TEOS - handles intent, memory, response, recommendations"""
    
    def __init__(self):
        self.intent_classifier = None
        self.response_generator = None
        self.memory_manager = None
        self.recommendation_engine = None
        self.moderation_engine = None
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
        self.intent_classifier = IntentClassifier()
        self.response_generator = ResponseGenerator()
        self.memory_manager = MemoryManager()
        self.recommendation_engine = RecommendationEngine()
        self.moderation_engine = ModerationEngine()
        await self.intent_classifier.load_models()
        await self.recommendation_engine.load()
        self._initialized = True
        logger.info("AI Orchestrator initialized")
    
    async def process_message(self, user_id: int, message: str, context: Dict = None) -> Dict[str, Any]:
        """Process user message and return AI response with metadata"""
        if not settings.AI_ENABLED or not self._initialized:
            return {"fallback": True, "response": "AI is disabled", "confidence": 0}
        
        # 1. Moderation check
        is_safe, reason = await self.moderation_engine.check_message(message)
        if not is_safe:
            logger.warning(f"Unsafe message from {user_id}: {reason}")
            return {"fallback": True, "response": "پیام شما حاوی محتوای نامناسب است.", "confidence": 0}
        
        # 2. Intent classification
        intent_result = await self.intent_classifier.predict(message)
        intent = intent_result.get("intent", "unknown")
        confidence = intent_result.get("confidence", 0)
        entities = intent_result.get("entities", {})
        
        # 3. Retrieve memory
        memory = await self.memory_manager.get_user_memory(user_id, session_context=context)
        
        # 4. Generate response
        if confidence < settings.AI_CONFIDENCE_THRESHOLD:
            response = "متوجه منظور شما نشدم. لطفاً از گزینه‌های منو استفاده کنید."
            fallback = True
        else:
            response = await self.response_generator.generate(
                intent=intent,
                entities=entities,
                user_id=user_id,
                memory=memory,
                context=context
            )
            fallback = False
        
        # 5. Store interaction in memory
        await self.memory_manager.store_interaction(user_id, message, response, intent, confidence)
        
        # 6. Update user preferences if needed
        if intent in ["music_request", "genre_preference"]:
            await self._update_user_preferences(user_id, entities)
        
        return {
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "fallback": fallback,
            "suggestions": intent_result.get("suggestions", [])
        }
    
    async def recommend_music(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get personalized music recommendations"""
        if not self._initialized:
            await self.initialize()
        return await self.recommendation_engine.get_recommendations(user_id, limit)
    
    async def recommend_services(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get service recommendations based on user history"""
        return await self.recommendation_engine.get_service_recommendations(user_id, limit)
    
    async def _update_user_preferences(self, user_id: int, entities: Dict):
        """Update user preferences in database"""
        user = await UserService.get_user_by_telegram_id(user_id)
        if not user:
            return
        genres = entities.get("genres", [])
        if genres:
            current = json.loads(user.favorite_genres) if user.favorite_genres else []
            new = list(set(current + genres))[:10]
            user.favorite_genres = json.dumps(new)
            await UserService.update_user(user_id, {"favorite_genres": user.favorite_genres})
    
    async def get_ai_stats(self) -> Dict:
        """Get AI engine statistics"""
        return {
            "intents_processed": await self.intent_classifier.get_stats(),
            "memory_entries": await self.memory_manager.get_total_entries(),
            "recommendations_generated": await self.recommendation_engine.get_stats()
        }
