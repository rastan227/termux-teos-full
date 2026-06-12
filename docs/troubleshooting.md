# راهنمای عیب‌یابی TEOS

## مشکلات رایج و راه‌حل‌ها

### 1. ربات پاسخ نمی‌دهد
- بررسی کنید که ربات در حال اجرا است: `docker-compose ps`
- لاگ‌ها را ببینید: `docker-compose logs bot --tail=50`
- توکن ربات را در `.env` بررسی کنید
- Webhook را چک کنید: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

### 2. خطای اتصال به دیتابیس
- اطمینان از اجرای PostgreSQL: `docker-compose up -d postgres`
- لاگ دیتابیس: `docker-compose logs postgres`
- بررسی credentials در `.env`

### 3. Webhook تنظیم نمی‌شود
- سرور باید از طریق HTTPS قابل دسترس باشد (SSL معتبر)
- فایروال پورت ۴۴۳ را باز کرده باشد
- مسیر `/webhook` در nginx تنظیم شده باشد

### 4. خطای مهاجرت دیتابیس
- بررسی نسخه فعلی: `alembic current`
- اعمال مهاجرت: `alembic upgrade head`
- در صورت خطا، از `alembic downgrade -1` سپس دوباره upgrade کنید

### 5. مصرف حافظه بالا
- محدودیت حافظه را در docker-compose تنظیم کنید
- جمع‌آوری garbage: `docker system prune -a`

### 6. پرداخت تأیید نمی‌شود
- درخواست شارژ در pending است: ادمین باید تأیید کند
- موجودی کیف پول کافی نیست: شارژ کنید

### 7. دانلود آهنگ انجام نمی‌شود
- فایل آهنگ در مسیر `storage/music` وجود دارد؟
- مجوز دسترسی کاربر بررسی شود

### 8. خطای ۵۰۰ در API
- لاگ API را ببینید: `docker-compose logs api --tail=100`
- بررسی کنید که دیتابیس در دسترس است

### 9. ربات در حالت polling کار نمی‌کند
- مطمئن شوید webhook قبلاً حذف شده باشد
- تنظیم `USE_WEBHOOK=false` در `.env`

### 10. بکاپ خودکار انجام نمی‌شود
- cron job باید فعال باشد (در scheduler.py)
- دایرکتوری `/backups` باید writeable باشد

## لاگ‌ها
- ربات: `logs/teos.log`
- خطاها: `logs/error.log`
- Docker: `docker-compose logs`

## بازنشانی کامل
```bash
docker-compose down -v
docker-compose run --rm bot alembic upgrade head
docker-compose up -d
Eof
