from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, BigInteger, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class MusicCategory(str, enum.Enum):
    NEW = "new"
    POPULAR = "popular"
    TRENDING = "trending"
    CLASSIC = "classic"
    RANDOM = "random"

class ModerationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"

class Music(Base):
    __tablename__ = "music"
    __table_args__ = (
        Index("idx_music_genre_active", "genre", "is_active"),
        Index("idx_music_category_plays", "category", "plays"),
        Index("idx_music_search_title", "title"),
        Index("idx_music_artist", "artist"),
    )
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(200), nullable=False)
    album = Column(String(200), nullable=True)
    genre = Column(String(50), nullable=False, index=True)
    category = Column(String(50), default=MusicCategory.NEW.value, index=True)
    duration = Column(Integer, default=0)  # seconds
    bitrate = Column(Integer, default=128)  # kbps
    file_size = Column(Integer, nullable=True)  # bytes
    file_format = Column(String(10), default="mp3")
    
    # Files
    file_path = Column(String(500), nullable=False)
    cover_url = Column(String(500), nullable=True)
    lyrics = Column(Text, nullable=True)
    
    # Stats
    plays = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Moderation
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_explicit = Column(Boolean, default=False)
    moderation_status = Column(String(20), default=ModerationStatus.PENDING.value)
    moderation_reason = Column(String(255), nullable=True)
    moderated_by = Column(BigInteger, nullable=True)
    moderated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Ownership
    uploaded_by = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)  # list of tags
    mood = Column(String(50), nullable=True)  # happy, sad, energetic, etc.
    language = Column(String(10), default="fa")  # persian, english, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    likes_rel = relationship("MusicLike", back_populates="music", cascade="all, delete-orphan")
    plays_rel = relationship("MusicPlay", back_populates="music", cascade="all, delete-orphan")
    reports = relationship("MusicReport", back_populates="music", cascade="all, delete-orphan")
    
    def increment_plays(self) -> None:
        self.plays += 1
    
    def increment_likes(self) -> None:
        self.likes += 1
    
    def increment_downloads(self) -> None:
        self.downloads += 1
    
    def update_rating(self, new_rating: int) -> None:
        total = self.avg_rating * self.rating_count
        self.rating_count += 1
        self.avg_rating = round((total + new_rating) / self.rating_count, 2)
    
    def approve(self, moderator_id: int) -> None:
        self.moderation_status = ModerationStatus.APPROVED.value
        self.is_active = True
        self.moderated_by = moderator_id
        self.moderated_at = func.now()
    
    def reject(self, moderator_id: int, reason: str) -> None:
        self.moderation_status = ModerationStatus.REJECTED.value
        self.is_active = False
        self.moderation_reason = reason
        self.moderated_by = moderator_id
        self.moderated_at = func.now()
    
    def to_dict(self, include_file: bool = False) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "genre": self.genre,
            "category": self.category,
            "duration": self.duration,
            "plays": self.plays,
            "likes": self.likes,
            "avg_rating": self.avg_rating,
            "is_featured": self.is_featured,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_file:
            data.update({
                "file_path": self.file_path,
                "cover_url": self.cover_url,
                "lyrics": self.lyrics,
                "file_size": self.file_size,
            })
        return data

class MusicLike(Base):
    __tablename__ = "music_likes"
    __table_args__ = (Index("idx_music_likes_user_music", "user_id", "music_id", unique=True),)
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    music_id = Column(Integer, ForeignKey("music.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="music_likes")
    music = relationship("Music", back_populates="likes_rel")

class MusicPlay(Base):
    __tablename__ = "music_plays"
    __table_args__ = (Index("idx_music_plays_user_music", "user_id", "music_id"), Index("idx_music_plays_date", "played_at"))
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    music_id = Column(Integer, ForeignKey("music.id", ondelete="CASCADE"), nullable=False)
    played_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_listened = Column(Integer, nullable=True)  # seconds
    source = Column(String(50), default="bot")  # bot, api, web
    
    user = relationship("User", back_populates="music_plays")
    music = relationship("Music", back_populates="plays_rel")

class MusicReport(Base):
    __tablename__ = "music_reports"
    
    id = Column(Integer, primary_key=True)
    music_id = Column(Integer, ForeignKey("music.id", ondelete="CASCADE"), nullable=False)
    reporter_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    reason = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    resolved_by = Column(BigInteger, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    music = relationship("Music", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="music_reports")
