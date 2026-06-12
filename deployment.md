# راهنمای کامل استقرار TEOS در محیط Production

## فهرست
1. [پیش‌نیازها](#پیش‌نیازها)
2. [تنظیم متغیرهای محیطی](#تنظیم-متغیرهای-محیطی)
3. [اجرای مهاجرت دیتابیس](#اجرای-مهاجرت-دیتابیس)
4. [اجزای سرویس‌ها](#اجزای-سرویس‌ها)
5. [تنظیم Webhook](#تنظیم-webhook)
6. [مانیتورینگ](#مانیتورینگ)
7. [به‌روزرسانی](#به‌روزرسانی)
8. [پشتیبان‌گیری و بازیابی](#پشتیبان‌گیری-و-بازیابی)
9. [عکس‌برداری از خطاها](#عکس‌برداری-از-خطاها)

---

## پیش‌نیازها

- **سرور**: Ubuntu 22.04 یا 24.04 (توصیه می‌شود)
- **منابع حداقل**: 4GB RAM، 2 هسته CPU، 50GB فضای ذخیره‌سازی
- **نرم‌افزارهای نصب شده**:
  - Docker Engine 24+
  - Docker Compose Plugin v2+
  - Git
  - curl, wget, jq
- **دامنه معتبر با رکورد A** (برای webhook و پنل مدیریت)
- **گواهی SSL** (از Let's Encrypt یا خریداری شده)
- **توکن ربات تلگرام** که از @BotFather دریافت کرده‌اید

### نصب سریع پیش‌نیازها روی Ubuntu

```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# نصب Docker Compose Plugin
sudo apt install docker-compose-plugin -y

# نصب Git و ابزارها
sudo apt install git curl jq -y

# خروج و ورود مجدد برای اعمال گروه docker
newgrp docker
