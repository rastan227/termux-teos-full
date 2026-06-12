from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import json

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(128), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(String(20), default="string")  # string, int, bool, json
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)  # accessible via API without auth
    updated_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def get_value(self):
        if self.value_type == "int":
            return int(self.value) if self.value else 0
        elif self.value_type == "bool":
            return self.value.lower() == "true" if self.value else False
        elif self.value_type == "json":
            return json.loads(self.value) if self.value else {}
        return self.value
    
    def set_value(self, value):
        if self.value_type == "json":
            self.value = json.dumps(value)
        else:
            self.value = str(value)

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=True)
    title = Column(String(100), nullable=False)
    command = Column(String(50), nullable=True)  # bot command
    callback_data = Column(String(100), nullable=True)  # callback data
    url = Column(String(255), nullable=True)
    icon = Column(String(50), nullable=True)
    sort_order = Column(Integer, default=0)
    role_required = Column(String(50), nullable=True)  # minimum role
    is_active = Column(Boolean, default=True)
    condition = Column(Text, nullable=True)  # JSON condition
    tenant_id = Column(Integer, nullable=True)

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    trigger_type = Column(String(50), nullable=False)  # event, schedule, api
    trigger_config = Column(JSON, nullable=True)
    nodes = Column(JSON, nullable=False)  # workflow nodes
    edges = Column(JSON, nullable=False)  # connections
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
