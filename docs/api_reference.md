# مرجع کامل API پروژه TEOS

## مقدمه
پایه API: `https://your-domain.com/api`
همه درخواست‌ها (به جز endpoints عمومی) نیاز به توکن JWT در هدر `Authorization: Bearer <token>` دارند.

## احراز هویت

### POST /api/auth/login
ورود کاربر با Telegram ID (یا ایمیل/رمز عبور برای ادمین‌ها)

**پارامترها:**
```json
{
  "telegram_id": 123456789,
  "password": "optional"
}
