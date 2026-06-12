# راهنمای مشارکت در توسعه TEOS

## قوانین کلی
- از Conventional Commits استفاده کنید: `feat: add new endpoint`, `fix: resolve bug in wallet`, `docs: update api reference`
- کد باید با Black فرمت شود (`black .`)
- قبل از ارسال PR، تمام تست‌ها را اجرا کنید (`pytest tests/`)
- حتماً تست‌های مربوط به تغییرات خود را بنویسید
- مستندات را به‌روز کنید (API، README، docs/)

## فرآیند مشارکت

1. **Issue جدید باز کنید** (در صورت عدم وجود) و توضیح دهید چه مشکلی را حل می‌کنید یا چه قابلیتی اضافه می‌کنید.
2. **برنچ خود را از `develop` ایجاد کنید** (نه از `main`).
   ```bash
   git checkout -b feature/my-feature develop
