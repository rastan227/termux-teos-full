
import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, CallbackQuery, User as TgUser, Chat
from app.bot.dispatcher import create_dispatcher
from app.bot.handlers.start import cmd_start
from app.bot.handlers.music import cmd_music, music_category_callback
from app.services.user_service import UserService

pytestmark = pytest.mark.asyncio

class TestBotIntegration:
    
    @pytest.fixture
    def mock_user(self):
        return TgUser(id=123456, is_bot=False, first_name="Test", username="testuser")
    
    @pytest.fixture
    def mock_message(self, mock_user):
        msg = AsyncMock(spec=Message)
        msg.from_user = mock_user
        msg.text = "/start"
        msg.answer = AsyncMock()
        return msg
    
    async def test_start_command(self, mock_message):
        with patch("app.bot.handlers.start.UserService.get_or_create") as mock_get:
            mock_user = AsyncMock()
            mock_user.role = "user"
            mock_get.return_value = mock_user
            await cmd_start(mock_message, AsyncMock())
            mock_message.answer.assert_called_once()
    
    async def test_music_command(self, mock_message):
        with patch("app.bot.handlers.music.MusicService.get_songs_by_category") as mock_songs:
            mock_songs.return_value = {"items": [], "pages": 1}
            await cmd_music(mock_message)
            mock_message.answer.assert_called_once()
    
    async def test_full_purchase_flow(self):
        # Simulate user clicking through purchase
        pass
