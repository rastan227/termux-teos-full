# نمونه‌های استفاده از API TEOS

## احراز هویت

### دریافت توکن (برای ادمین‌ها با رمز عبور)
```bash
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456789, "password": "admin_pass"}'

