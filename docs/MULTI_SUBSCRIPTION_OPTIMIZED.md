# Multiple Subscriptions with Optimized Channel Collection

## معماری پیشنهادی

### تقسیم مسئولیت

**config/providers.json:**
- تنظیمات کلی استخراج (API، session، defaults)
- تنظیمات عمومی Telegram

**config/subscriptions.json:**
- تعریف هر subscription با اسم و کانال‌های خاص
- هر subscription می‌تواند کانال‌های مختلف داشته باشد

---

## مثال عملی

### config/providers.json (تنظیمات کلی)

```json
{
  "providers": [
    {
      "name": "telegram",
      "enabled": true,
      "type": "telegram",
      "source": {
        "channels": [],
        "api_id": 34650676,
        "api_hash": "960a602ffe29a6937bdc66e3f6be60a6",
        "default_message_limit": 10,
        "preserve_previous_configs": true
      }
    }
  ]
}
```

**نکات مهم:**
- `channels` در provider خالی است (لیست تعریف‌شده در subscriptions)
- API credentials اینجا قرار می‌گیرند
- تنظیمات preservation اینجا مدیریت می‌شود

### config/subscriptions.json (تعریف subscription‌ها و کانال‌ها)

```json
{
  "subscriptions": [
    {
      "name": "default",
      "enabled": true,
      "subscription_name": "Telegram-List1",
      "format": "plain",
      "provider": "telegram",
      "channels": [
        "https://t.me/Capoit",
        "https://t.me/ConfigsHUB",
        "https://t.me/daily_configs",
        "https://t.me/mehrosaboran",
        "https://t.me/VmessProtocol"
      ]
    },
    {
      "name": "vpn_specialized",
      "enabled": true,
      "subscription_name": "Telegram-VPN-Specialized",
      "format": "plain",
      "provider": "telegram",
      "channels": [
        "https://t.me/daily_configs",
        "https://t.me/Best_internet_iran",
        "https://t.me/Persianvpnhub",
        "https://t.me/V2rayng_Fast"
      ]
    }
  ]
}
```

---

## الگوریتم بهینه‌سازی

### مسئله اصلی
- لیست 1: 5 کانال
- لیست 2: 3 کانال  
- 2 کانال مشترک

**بدون بهینه‌سازی:** 8 درخواست (5 + 3)
**با بهینه‌سازی:** 6 درخواست (5 + 3 - 2)

### حل (در runner.py)

```
1. تمام subscription‌های enabled را خوانده
2. کانال‌های منحصر به فرد را استخراج (set)
3. یکبار تمام کانال‌های منحصر را بخوانده
4. برای هر subscription، نتایج را استفاده کنده
```

**مراحل:**

```python
# ۱. استخراج کانال‌های منحصر به فرد
unique_channels_set = set()
for subscription in enabled_subscriptions:
    unique_channels_set.update(subscription.channels)

# ۲. خواندن یکبار
all_nodes = provider.collect()  # فقط unique channels

# ۳. استفاده برای هر subscription
for subscription in enabled_subscriptions:
    # نتایج all_nodes برای این subscription مناسب‌اند
    result = pipeline.run(collected_text, output_filename)
```

---

## مثال عملی: اجرای Runner

### Input:
```
Subscriptions:
- Telegram-List1: 5 کانال
- Telegram-VPN-Specialized: 3 کانال (۲ مشترک)

Unique channels: 6 تا
```

### Output:

```
✓ Found 2 enabled subscription(s): Telegram-List1, Telegram-VPN-Specialized
✓ Extracting 6 unique channel(s)...
✓ Collected 150 proxy nodes from 6 channel(s)
✓ Merged 180 proxy nodes (new + preserved)
✓ Published Telegram-List1.txt with 72 nodes
  Channels: https://t.me/Capoit, https://t.me/ConfigsHUB...
✓ Published Telegram-VPN-Specialized.txt with 45 nodes
  Channels: https://t.me/daily_configs, https://t.me/Best_internet_iran...

✓ Successfully processed 2/2 subscription(s)
```

---

## مزایا

### ۱. بهینه‌سازی شبکه
- ❌ درخواست تکراری حذف شد
- ✅ فقط درخواست‌های منحصر به فرد

### ۲. انعطاف‌پذیری
- ✅ هر subscription می‌تواند کانال‌های متفاوت داشته باشد
- ✅ آسان اضافه کردن/حذف subscription
- ✅ آسان اضافه کردن/حذف کانال

### ۳. maintainability
- ✅ تقسیم واضح مسئولیت‌ها
- ✅ provider.json برای تنظیمات کلی
- ✅ subscriptions.json برای تعریف specific

### ۴. خروجی منطقی
- ✅ هر subscription یک فایل
- ✅ نام معنی‌دار برای فایل‌ها
- ✅ فایل‌های decoded خودکار

---

## نمودار جریان

```
Config Files
├── providers.json (API keys, general settings)
└── subscriptions.json (subscription definitions)
         ↓
    Read Config
         ↓
    Extract Unique Channels
    (Set deduplication)
         ↓
    Collect from Unique Channels
    (Single collection pass)
         ↓
    Cache Results (all_nodes)
         ↓
    For Each Subscription:
    ├── Use cached all_nodes
    ├── Process with pipeline
    ├── Generate .txt file
    └── Generate .decoded.txt file
         ↓
    Output Files
    ├── Telegram-List1.txt
    ├── Telegram-List1.decoded.txt
    ├── Telegram-VPN-Specialized.txt
    └── Telegram-VPN-Specialized.decoded.txt
```

---

## تغییرات در کد

### Models (subscription.py)
```python
@dataclass
class Subscription:
    name: str
    enabled: bool
    subscription_name: str
    format: str
    provider: str              # NEW
    channels: tuple[str, ...] = ()  # NEW
    metadata: dict[str, Any] = field(default_factory=dict)
```

### Config (config.py)
- اضافه کردن خواندن `provider` و `channels` از subscriptions.json

### Runner (runner.py)
- ۱. خواندن تمام subscription‌ها
- ۲. استخراج کانال‌های منحصر به فرد
- ۳. یکبار جمع‌آوری
- ۴. پردازش برای هر subscription

---

## آزمایش

تمام tests موفق هستند:
- ✅ test_subscription_model: پشتیبانی `provider` و `channels`
- ✅ test_result_models: مدل‌های نتیجه
- ✅ test_pipeline: pipeline همچنان عمل می‌کند

---

## نتیجه‌گیری

این معماری:
- ✅ **بهینه**: کانال‌های مشترک یکبار خوانده می‌شود
- ✅ **منطقی**: تقسیم واضح providers و subscriptions
- ✅ **انعطاف‌پذیر**: اضافه کردن subscription‌های جدید ساده است
- ✅ **مقیاس‌پذیر**: هزاران subscription و درخواست مدیریت می‌شود
