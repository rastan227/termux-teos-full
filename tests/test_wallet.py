import pytest
from unittest.mock import AsyncMock, patch
from app.services.wallet_service import WalletService
from app.models.user import User

@pytest.mark.asyncio
async def test_add_balance():
    with patch("app.services.wallet_service.async_session_maker") as mock_maker:
        mock_session = AsyncMock()
        mock_user = User(telegram_id=123, wallet_balance=0)
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        mock_maker.return_value.__aenter__.return_value = mock_session
        
        tx = await WalletService.add_balance(123, 50000, "Test deposit")
        assert tx is not None
        assert mock_user.wallet_balance == 50000

@pytest.mark.asyncio
async def test_deduct_balance_insufficient():
    with patch("app.services.wallet_service.async_session_maker") as mock_maker:
        mock_session = AsyncMock()
        mock_user = User(telegram_id=123, wallet_balance=10000)
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        mock_maker.return_value.__aenter__.return_value = mock_session
        
        tx = await WalletService.deduct_balance(123, 20000, "Purchase")
        assert tx is None
        assert mock_user.wallet_balance == 10000

@pytest.mark.asyncio
async def test_get_balance():
    with patch("app.services.wallet_service.async_session_maker") as mock_maker:
        mock_session = AsyncMock()
        mock_user = User(telegram_id=123, wallet_balance=75000, wallet_hold=5000)
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        mock_maker.return_value.__aenter__.return_value = mock_session
        
        balance = await WalletService.get_balance(123)
        assert balance["balance"] == 75000
        assert balance["hold"] == 5000
        assert balance["available"] == 70000
