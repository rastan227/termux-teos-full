import pytest
from unittest.mock import AsyncMock, patch
from app.plugins.plugin_manager import PluginManager
from app.plugins.base_plugin import BasePlugin

pytestmark = pytest.mark.asyncio

class MockPlugin(BasePlugin):
    name = "mock"
    display_name = "Mock"
    version = "1.0"
    installed = False
    enabled = False
    
    async def on_install(self):
        self.installed = True
        return True
    
    async def on_enable(self):
        self.enabled = True
        return True
    
    async def on_disable(self):
        self.enabled = False
        return True
    
    async def on_uninstall(self):
        self.installed = False
        return True

async def test_plugin_lifecycle():
    plugin = MockPlugin()
    assert await plugin.on_install() == True
    assert plugin.installed == True
    assert await plugin.on_enable() == True
    assert plugin.enabled == True
    assert await plugin.on_disable() == True
    assert plugin.enabled == False
    assert await plugin.on_uninstall() == True
    assert plugin.installed == False

async def test_plugin_manager_discover():
    with patch("app.plugins.plugin_manager.importlib.import_module") as mock_import:
        mock_module = AsyncMock()
        mock_import.return_value = mock_module
        # Simplified test
        plugins = await PluginManager.discover_plugins()
        assert isinstance(plugins, dict)
