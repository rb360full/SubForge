# SubForge - Multiple Subscriptions Update Summary

## تغییرات اعمال شده

### 1. **Model Updates** (src/models/subscription.py)
   - تغییر `output_path` به `subscription_name` در مدل Subscription
   - اضافه شدن `@property` به نام `output_path` برای تولید پویا نام فایل
   - فرمت: `{subscription_name}.txt`

### 2. **Configuration Changes** (config/subscriptions.json)
   - تغییر schema: `output_path` → `subscription_name`
   - مثال:
     ```json
     {
       "name": "default",
       "enabled": true,
       "subscription_name": "Telegram-List1",
       "format": "plain"
     }
     ```

### 3. **Config Loader Updates** (src/core/config.py)
   - بروز رسانی `_load_subscriptions` برای خواندن `subscription_name` به جای `output_path`
   - فیلتر کردن metadata با کلیدهای جدید

### 4. **Runner Updates** (src/runner.py)
   - تولید نام فایل پویا: `subscriptions/{subscription.output_path}`
   - از property `output_path` استفاده که `subscription_name` را تبدیل می‌کند

### 5. **Workflow Updates** (.github/workflows/update.yml)
   - تغییر `git add` برای شامل کردن کل دایرکتوری `subscriptions/`
   - تغییر artifact path برای شامل کردن کل `subscriptions/` directory
   - این کار اجازه می‌دهد تا هر تعداد subscription فایل generate شود

### 6. **Helper Scripts Updates**
   - **decode_default.py**: پذیرش command-line arguments برای نام فایل
     ```bash
     python subscriptions/decode_default.py "Telegram-List2.txt"
     ```
   - **decode_default.ps1**: پذیرش parameters برای dynamic output
     ```powershell
     & .\subscriptions\decode_default.ps1 -Input "Telegram-List2.txt"
     ```

### 7. **Documentation**
   - ایجاد `docs/SUBSCRIPTIONS.md` برای راهنمایی configuration
   - بروز رسانی `subscriptions/README.md`
   - بروز رسانی `README.md` برای اشاره به multiple files

### 8. **Tests Updates** (tests/)
   - بروز رسانی test_models.py برای تست `subscription_name` property
   - تأیید که `output_path` درست generate می‌شود

## How to Use Multiple Subscriptions

### مثال 1: اضافه کردن Telegram-List2

ویرایش `config/subscriptions.json`:
```json
{
  "subscriptions": [
    {
      "name": "default",
      "enabled": true,
      "subscription_name": "Telegram-List1",
      "format": "plain"
    },
    {
      "name": "list2",
      "enabled": true,
      "subscription_name": "Telegram-List2",
      "format": "plain"
    }
  ]
}
```

### فایل‌های generate شده:
- `subscriptions/Telegram-List1.txt` و `subscriptions/Telegram-List1.decoded.txt`
- `subscriptions/Telegram-List2.txt` و `subscriptions/Telegram-List2.decoded.txt`

### Disabling a subscription:
```json
{
  "name": "list2",
  "enabled": false,
  "subscription_name": "Telegram-List2",
  "format": "plain"
}
```

## اطلاعات اضافی

- فیلم subscription_name منطبق است با نام فایل output (بدون extension)
- تمام subscriptions enabled از طریق workflow process می‌شود
- Workflow بطور خودکار تمام فایل‌های جدید را commit و push می‌کند
- Helper scripts اکنون generic هستند و با هر نام فایل کار می‌کنند

## Backwards Compatibility Note

اگر فایل‌های قدیمی دارید:
- `default.txt` → `Telegram-List1.txt`
- `default.decoded.txt` → `Telegram-List1.decoded.txt`

نام‌ها تغییر داده شده‌اند و configuration بروز رسانی شده است.
