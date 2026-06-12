# معماری نهایی TEOS - مستندات کامل

## نمای کلی
TEOS یک سیستم عامل سازمانی است که از Telegram به عنوان یکی از لایه‌های رابط استفاده می‌کند. معماری بر اساس اصول **لایه‌بندی، ماژولار بودن، plugin-driven و AI-orchestrated** طراحی شده است.

## لایه‌های اصلی

### 1. لایه زیرساخت (Infrastructure Layer)
- **ارکستراسیون**: Docker Swarm / Kubernetes (آماده)
- **پایگاه داده**: PostgreSQL (با پشتیبانی از JSONB و Full-Text Search)
- **کش و صف**: Redis (برای نشست‌ها، rate limiting، قفل توزیع‌شده)
- **مانیتورینگ**: Prometheus + Grafana
- **لاگ**: ساختار یافته JSON با چرخش خودکار

### 2. لایه هسته (Core Engine)
- User Engine: مدیریت کاربران، نقش‌ها، دسترسی‌ها
- Event Engine: رویدادهای سیستمی (آزادسازی منابع، ارسال نوتیف)
- Workflow Engine: (در حال توسعه) اجرای جریان‌های کاری بصری
- AI Engine: طبقه‌بندی نیت، حافظه، تولید پاسخ، پیشنهادات

### 3. لایه ماژول‌های بیزینس (Business Modules)
- Music Module: مدیریت آهنگ‌ها، پلی‌لیست، دانلود، لایک
- Service Module: فروش VPN، سرور و سایر سرویس‌ها
- Wallet Module: کیف پول، تراکنش‌ها، درخواست شارژ
- Ticket Module: پشتیبانی و تیکتینگ

### 4. لایه رابط (Interface Layer)
- Telegram Bot: (aiogram 3) با Webhook/Polling
- REST API: FastAPI با مستندات خودکار Swagger
- GraphQL API: (نمونه اولیه) برای کوئری‌های پیچیده
- Web Portal: پنل ادمین و مالک (React + Tailwind)

## جریان داده

### سناریو ۱: کاربر پیام می‌فرستد
User -> Telegram -> Bot Webhook -> Dispatcher -> Middleware -> Handler -> Core Service -> AI Orchestrator -> Response -> User

### سناریو ۲: خرید از طریق ربات
User -> /services -> انتخاب سرویس -> تأیید خرید -> WalletService -> OrderService -> NotificationEngine -> Delivery (API خارجی) -> WebhookConsumer -> تکمیل سفارش

### سناریو ۳: پنل ادمین
Admin -> Web Portal -> API Gateway -> Auth Middleware -> Permission Check -> Service -> Database -> Response

## امنیت
- **احراز هویت**: JWT (access + refresh) برای API، Telegram ID برای ربات
- **مجوزها**: RBAC مبتنی بر نقش (User, MusicAdmin, ServiceAdmin, SuperAdmin, Owner)
- **Rate Limiting**: به ازای کاربر + IP با Redis (۱۰۰ درخواست در دقیقه)
- **Anti-Spam**: بررسی محتوای پیام با الگوهای regex
- **Audit Log**: ثبت تمام عملیات حساس در جدول audit_logs
- **Webhook Signature**: تأیید امضای درخواست‌های ورودی

## مقیاس‌پذیری
- **Horizontal Scaling**: Stateless بودن API و Bot (با استفاده از Redis برای نشست‌ها)
- **Database**: Pool اتصال (۲۰ اتصال پیش‌فرض)، پشتیبانی از read replicas
- **Cache**: کش کردن لیست‌های پرتکرار (آهنگ‌های محبوب، تنظیمات سیستم)
- **Async**: استفاده از async/await در همه جای Python

## مانیتورینگ و هشدار
- **متریک‌های سفارشی**: تعداد کاربران فعال، تراکنش‌ها، درخواست‌های API
- **Health Checks**: `/health` برای API و ربات
- **Alerts**: نرخ خطا > ۵٪، زمان پاسخ > ۱ ثانیه، پایین بودن دیتابیس

## پشتیبان و بازیابی
- **Backup Schedule**: روزانه ساعت ۲ بامداد (قابل تنظیم)
- **Retention**: ۷ روز نگهداری
- **بازیابی**: اسکریپت `restore.sh` با قابلیت rollback

## اتوآپدیت
- **استراتژی**: بررسی نسخه جدید از GitHub، بکاپ خودکار، اعمال مهاجرت، ریستارت
- **Rollback**: با استفاده از نسخه قبلی و downgrade migration

## تصمیمات فنی مهم
- **زبان اصلی**: Python 3.12 (برای سرعت توسعه و اکوسیستم async)
- **Telegram Framework**: aiogram 3 (پشتیبانی از webhook، FSM، middleware)
- **Database ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **AI**: ترکیب rule-based + OpenAI API (قابل تعویض با مدل‌های محلی)

## محدودیت‌ها و چشم‌انداز آینده
- **فعلاً پشتیبانی از پرداخت واقعی** (Mock mode فعال است)
- **GraphQL در مرحله نمونه** (برای توسعه آینده)
- **Workflow Engine در برنامه‌های بعدی** (اکنون به صورت کد سخت)

برای مشارکت یا پرسش، به مستندات `CONTRIBUTING.md` و `README.md` مراجعه کنید.
