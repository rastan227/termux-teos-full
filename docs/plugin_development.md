# راهنمای توسعه پلاگین در TEOS

## مقدمه
پلاگین‌ها ماژول‌های مستقلی هستند که می‌توانند بدون تغییر هسته اصلی به TEOS اضافه شوند. هر پلاگین یک کلاس پایتون است که از `BasePlugin` ارث‌بری می‌کند.

## ساختار پایه پلاگین

```python
from app.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    display_name = "My Awesome Plugin"
    version = "1.0.0"
    author = "Your Name"
    description = "Description of what this plugin does"
    
    async def on_install(self):
        # ایجاد جداول، تنظیمات اولیه
        pass
    
    async def on_enable(self):
        # ثبت هندلرها، اضافه کردن منوها
        pass
    
    async def on_disable(self):
        # پاکسازی منابع
        pass
    
    async def on_uninstall(self):
        # حذف جداول و داده‌ها
        pass
