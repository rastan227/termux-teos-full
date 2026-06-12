import pytest
from unittest.mock import AsyncMock, patch
from app.services.user_service import UserService
from app.services.music_service import MusicService
from app.services.wallet_service import WalletService
from app.models.user import User, UserRole

pytestmark = pytest.mark.asyncio

class TestUserService:
    
    async def test_get_or_create_new_user(self):
        with patch("app.services.user_service.async_session_maker") as mock_maker:
            mock_session = AsyncMock()
            mock_session.execute.return_value.scalar_one_or_none.return_value = None
            mock_maker.return_value.__aenter__.return_value = mock_session
            user = await UserService.get_or_create(12345, "testuser", "Test", "User")
            assert user.telegram_id == 12345
            assert user.role == UserRole.USER
    
    async def test_get_user_by_telegram_id(self):
        with patch("app.services.user_service.async_session_maker") as mock_maker:
            mock_session = AsyncMock()
            mock_user = User(telegram_id=12345, first_name="Test")
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
            mock_maker.return_value.__aenter__.return_value = mock_session
            user = await UserService.get_user_by_telegram_id(12345)
            assert user.telegram_id == 12345
    
    async def test_ban_user(self):
        with patch("app.services.user_service.async_session_maker") as mock_maker:
            mock_session = AsyncMock()
            mock_user = User(telegram_id=12345, role=UserRole.USER)
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
            mock_maker.return_value.__aenter__.return_value = mock_session
            result = await UserService.ban_user(12345, "spam", 999)
            assert result is True
            assert mock_user.is_banned is True

class TestWalletService:
    
    async def test_add_balance(self):
        with patch("app.services.wallet_service.async_session_maker") as mock_maker:
            mock_session = AsyncMock()
            mock_user = User(telegram_id=123, wallet_balance=0)
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
            mock_maker.return_value.__aenter__.return_value = mock_session
            tx = await WalletService.add_balance(123, 50000, "test")
            assert tx is not None
            assert mock_user.wallet_balance == 50000
    
    async def test_deduct_balance_insufficient(self):
        with patch("app.services.wallet_service.async_session_maker") as mock_maker:
            mock_session = AsyncMock()
            mock_user = User(telegram_id=123, wallet_balance=10000)
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
            mock_maker.return_value.__aenter__.return_value = mock_session
            tx = await WalletService.deduct_balance(123, 20000, "purchase")
            assert tx is None

class TestMusicService:
    
    async def test_get_song_by_id_not_found(self):
        with patch("app.services.music_service.async_session_maker") as mock_maker:
            mock_session = AsyncMock()
            mock_session.execute.return_value.scalar_one_or_none.return_value = None
            mock_maker.return_value.__aenter__.return_value = mock_session
            song = await MusicService.get_song_by_id(999)
            assert song is None
