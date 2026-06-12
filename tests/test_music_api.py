import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_list_songs(client: AsyncClient):
    response = await client.get("/api/music/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

@pytest.mark.asyncio
async def test_search_songs(client: AsyncClient):
    response = await client.get("/api/music/search", params={"q": "love"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

@pytest.mark.asyncio
async def test_get_song_not_found(client: AsyncClient):
    response = await client.get("/api/music/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_popular_songs(client: AsyncClient):
    response = await client.get("/api/music/popular", params={"limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5

@pytest.mark.asyncio
async def test_trending_songs(client: AsyncClient):
    response = await client.get("/api/music/trending")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_recommendations_unauthorized(client: AsyncClient):
    response = await client.get("/api/music/recommendations")
    assert response.status_code == 401  # Requires auth

# Mock tests for service layer
@pytest.mark.asyncio
async def test_music_service_get_song():
    from app.services.music_service import MusicService
    with patch("app.services.music_service.async_session_maker") as mock:
        mock_session = AsyncMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        mock.return_value.__aenter__.return_value = mock_session
        song = await MusicService.get_song_by_id(1)
        assert song is None
