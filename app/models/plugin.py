from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PluginStatus(str, enum.Enum):
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"

class Plugin(Base):
    __tablename__ = "plugins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)
    display_name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    author = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    
    status = Column(String(20), default=PluginStatus.INSTALLED.value)
    
    entry_point = Column(String(255), nullable=False)  # module path
    config_schema = Column(JSON, nullable=True)  # JSON schema for settings
    settings = Column(JSON, nullable=True)
    
    dependencies = Column(JSON, nullable=True)  # list of plugin names
    permissions_required = Column(JSON, nullable=True)  # list of permissions
    
    installed_at = Column(DateTime(timezone=True), server_default=func.now())
    enabled_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def is_enabled(self) -> bool:
        return self.status == PluginStatus.ENABLED.value
    
    def enable(self) -> None:
        self.status = PluginStatus.ENABLED.value
        self.enabled_at = func.now()
    
    def disable(self) -> None:
        self.status = PluginStatus.DISABLED.value
    
    def get_setting(self, key: str, default=None):
        if self.settings:
            return self.settings.get(key, default)
        return default
    
    def set_setting(self, key: str, value):
        if self.settings is None:
            self.settings = {}
        self.settings[key] = value

class PluginInstallation(Base):
    __tablename__ = "plugin_installations"
    
    id = Column(Integer, primary_key=True)
    plugin_id = Column(Integer, ForeignKey("plugins.id"), nullable=False)
    installed_by = Column(Integer, nullable=False)
    version = Column(String(32), nullable=False)
    installed_at = Column(DateTime(timezone=True), server_default=func.now())
    logs = Column(Text, nullable=True)
