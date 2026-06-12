from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.services.music_service import MusicService
from app.api.dependencies import get_current_user, require_permission
from app.models.user import User
import logging

router = APIRouter(prefix="/music", tags=["music"])
logger = logging.getLogger(__name__)

# Schemas
class SongCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    artist: str = Field(..., min_length=1, max_length=200)
    album: Optional[str] = None
    genre: str = Field(..., min_length=1, max_length=50)
    category: str = "new"
    duration: int = 0
    lyrics: Optional[str] = None

class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class SongResponse(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str]
    genre: str
    plays: int
    likes: int
    avg_rating: float
    is_featured: bool

class SongListResponse(BaseModel):
    items: List[SongResponse]
    total: int
    page: int
    pages: int

# Endpoints
@router.get("/", response_model=SongListResponse)
async def list_songs(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get list of songs by category"""
    result = await MusicService.get_songs_by_category(category or "all", page, limit)
    return result

@router.get("/search")
async def search_songs(
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=50)
):
    """Search songs by title, artist, or album"""
    return await MusicService.search_songs(q, page, limit)

@router.get("/popular", response_model=List[SongResponse])
async def popular_songs(limit: int = Query(20, le=100)):
    """Get most popular songs"""
    return await MusicService.get_most_popular(limit)

@router.get("/new", response_model=List[SongResponse])
async def new_releases(limit: int = Query(20, le=100)):
    """Get newest songs"""
    return await MusicService.get_new_releases(limit)

@router.get("/trending", response_model=List[SongResponse])
async def trending_songs(limit: int = Query(20, le=100)):
    """Get trending songs (most plays in last 7 days)"""
    return await MusicService.get_trending(limit)

@router.get("/recommendations")
async def recommendations(
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, le=50)
):
    """AI-powered song recommendations for current user"""
    return await MusicService.get_recommendations(current_user.telegram_id, limit)

@router.get("/random")
async def random_song():
    """Get a random song"""
    song = await MusicService.get_random_song()
    if not song:
        raise HTTPException(status_code=404, detail="No songs found")
    return song

@router.get("/{song_id}", response_model=SongResponse)
async def get_song(song_id: int):
    song = await MusicService.get_song_by_id(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_song(
    data: SongCreate,
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("upload_music"))
):
    """Upload new song (admin only)"""
    import aiofiles
    import os
    from datetime import datetime
    
    # Validate file type
    if not file.filename.endswith(('.mp3', '.m4a', '.ogg')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only MP3, M4A, OGG allowed.")
    
    file_path = f"storage/music/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    os.makedirs("storage/music", exist_ok=True)
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    song = await MusicService.add_song(data.dict(), file_path, current_user.telegram_id)
    return {"id": song.id, "message": "Song created successfully"}

@router.put("/{song_id}")
async def update_song(
    song_id: int,
    data: SongUpdate,
    current_user: User = Depends(require_permission("edit_music"))
):
    updated = await MusicService.update_song(song_id, data.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"message": "Song updated"}

@router.delete("/{song_id}")
async def delete_song(
    song_id: int,
    hard: bool = False,
    current_user: User = Depends(require_permission("delete_music"))
):
    await MusicService.delete_song(song_id, soft_delete=not hard)
    return {"message": "Song deleted"}

@router.post("/{song_id}/like")
async def like_song(
    song_id: int,
    current_user: User = Depends(get_current_user)
):
    result = await MusicService.like_song(current_user.telegram_id, song_id)
    if not result:
        raise HTTPException(status_code=400, detail="Already liked")
    return {"message": "Song liked"}

@router.delete("/{song_id}/like")
async def unlike_song(
    song_id: int,
    current_user: User = Depends(get_current_user)
):
    result = await MusicService.unlike_song(current_user.telegram_id, song_id)
    if not result:
        raise HTTPException(status_code=404, detail="Like not found")
    return {"message": "Song unliked"}

@router.post("/{song_id}/report")
async def report_song(
    song_id: int,
    reason: str = Query(..., min_length=3),
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    await MusicService.report_song(current_user.telegram_id, song_id, reason, description)
    return {"message": "Report submitted"}

@router.get("/admin/stats")
async def admin_stats(
    current_user: User = Depends(require_permission("view_music_stats"))
):
    return await MusicService.get_admin_stats()

@router.get("/admin/pending-reports")
async def pending_reports(
    current_user: User = Depends(require_permission("moderate_music"))
):
    reports = await MusicService.get_pending_reports()
    return {"reports": reports}

@router.post("/admin/moderate/{song_id}")
async def moderate_song(
    song_id: int,
    action: str = Query(..., regex="^(approve|reject|delete)$"),
    reason: Optional[str] = None,
    current_user: User = Depends(require_permission("moderate_music"))
):
    result = await MusicService.moderate_song(song_id, action, current_user.telegram_id, reason)
    if not result:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"message": f"Song {action}d"}
