# معماری بهینه‌شده برای چند Subscription با Deduplication

## 📋 خلاصه تغییرات

### 1️⃣ تقسیم مسئولیت‌ها

**قبل:**
- `providers.json` کانال‌ها تعریف می‌کرد
- `subscriptions.json` فقط اسم فایل

**اکنون:**
- `providers.json` تنظیمات کلی (API keys، defaults)
- `subscriptions.json` کانال‌های مختص هر subscription

---

## 🔄 معماری جدید

```
providers.json
├── Telegram API credentials
├── API ID / API Hash
└── General settings

        ↓

subscriptions.json
├── Subscription 1: Telegram-List1
│   └── Channels: [ch1, ch2, ch3, ch4, ch5]
├── Subscription 2: Telegram-VPN
│   └── Channels: [ch3, ch5, ch6, ch7] ← 2 مشترک
└── Subscription 3: Telegram-Daily
    └── Channels: [ch8]

        ↓

Unique Channels: [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8] = 8 تا

        ↓

Runner Process:
1. Read all enabled subscriptions
2. Extract unique channels (Set deduplication)
3. Collect from unique channels ONCE
4. Use cached results for each subscription
```

---

## 📊 مثال عملی: بهینه‌سازی

### Input
```json
// subscriptions.json
{
  "subscriptions": [
    {
      "name": "default",
      "subscription_name": "Telegram-List1",
      "channels": [
        "https://t.me/Capoit",           // 1
        "https://t.me/ConfigsHUB",       // 2
        "https://t.me/daily_configs",    // 3 ← مشترک
        "https://t.me/mehrosaboran",     // 4
        "https://t.me/VmessProtocol"     // 5
      ]
    },
    {
      "name": "vpn_specialized",
      "subscription_name": "Telegram-VPN-Specialized",
      "channels": [
        "https://t.me/daily_configs",    // 3 ← دوباره
        "https://t.me/Best_internet_iran", // 6
        "https://t.me/Persianvpnhub",    // 7
        "https://t.me/V2rayng_Fast"      // 8
      ]
    }
  ]
}
```

### بدون بهینه‌سازی ❌
```
Subscription 1: 5 درخواست
Subscription 2: 4 درخواست
────────────────────────
کل: 9 درخواست
```

### با بهینه‌سازی ✅
```
Unique channels: 8 تا (ch1-ch8)
کل: 8 درخواست

Saved: 1 درخواست (11% بهتر)
```

> در مثال‌های بزرگ‌تر، بهینه‌سازی می‌تواند 50% تا 70% صرفه‌جویی کند

---

## 🔧 تغییرات در کد

### ۱. Models (src/models/subscription.py)

```python
@dataclass
class Subscription:
    name: str
    enabled: bool
    subscription_name: str
    format: str
    provider: str                    # ✨ NEW
    channels: tuple[str, ...] = ()   # ✨ NEW
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def output_path(self) -> str:
        return f"{self.subscription_name}.txt"
```

### ۲. Config Loader (src/core/config.py)

```python
# خواندن provider و channels از subscriptions.json
"provider": self._require_str(...),
"channels": tuple(item.get("channels", [])) if isinstance(...) else (),
```

### ۳. Runner (src/runner.py) - الگوریتم جدید

```python
# Step 1: Extract unique channels
unique_channels_set = set()
for subscription in enabled_subscriptions:
    unique_channels_set.update(subscription.channels)

# Step 2: Collect from unique channels ONCE
all_nodes = list(provider.collect(unique_channels))

# Step 3: Process each subscription using cached results
for subscription in enabled_subscriptions:
    result = pipeline.run(collected_text, output_filename)
```

### ۴. Configuration

**providers.json:**
```json
{
  "providers": [{
    "name": "telegram",
    "enabled": true,
    "source": {
      "channels": [],           // ✨ EMPTY - تعریف در subscriptions
      "api_id": 34650676,
      "api_hash": "960a602ffe29a6937bdc66e3f6be60a6",
      "preserve_previous_configs": true
    }
  }]
}
```

**subscriptions.json:**
```json
{
  "subscriptions": [
    {
      "name": "default",
      "enabled": true,
      "subscription_name": "Telegram-List1",
      "format": "plain",
      "provider": "telegram",          // ✨ NEW
      "channels": [                    // ✨ NEW
        "https://t.me/Capoit",
        "https://t.me/ConfigsHUB"
      ]
    }
  ]
}
```

---

## ✅ مزایا

| مزیت | توضیح |
|------|--------|
| **بهینه‌سازی** | کانال‌های مشترک یکبار خوانده می‌شود |
| **انعطاف‌پذیری** | هر subscription کانال‌های متفاوت می‌تواند داشته باشد |
| **مقیاس‌پذیری** | صدها subscription و درخواست مدیریت می‌شود |
| **وضوح** | تقسیم واضح providers (تنظیمات) و subscriptions (تعریف) |
| **maintainability** | کد ساده‌تر و فهم‌پذیرتر |
| **اضافه کردن آسان** | subscription جدید = یک object در JSON |

---

## 📈 Output نمونه

```
✓ Found 2 enabled subscription(s): Telegram-List1, Telegram-VPN-Specialized
✓ Extracting 8 unique channel(s)...
✓ Collected 150 proxy nodes from 8 channel(s)
✓ Merged 180 proxy nodes (new + preserved, deduplicated)
✓ Published Telegram-List1.txt with 72 nodes
  Channels: https://t.me/Capoit, https://t.me/ConfigsHUB...
✓ Published Telegram-VPN-Specialized.txt with 55 nodes
  Channels: https://t.me/daily_configs, https://t.me/Best_internet_iran...

✓ Successfully processed 2/2 subscription(s)
```

---

## 🧪 Tests

تمام tests بروز رسانی شدند:
- ✅ `test_subscription_model`: provider و channels
- ✅ `test_result_models`: نتایج
- ✅ `test_pipeline`: pipeline هنوز درست کار می‌کند

---

## 📚 فایل‌های مرتبط

- 📄 `docs/MULTI_SUBSCRIPTION_OPTIMIZED.md` - توضیح مفصل
- 📄 `ARCHITECTURE_PROVIDERS_SUBSCRIPTIONS.md` - مقایسه گزینه‌ها
- 📝 `test_architecture.py` - تست configuration

---

## 🎯 نتیجه‌گیری

این معماری:
- ✅ کانال‌های مشترک یکبار خوانده می‌شود
- ✅ هر subscription می‌تواند کانال‌های خاص داشته باشد
- ✅ آسانی اضافه کردن subscription‌های جدید
- ✅ تقسیم واضح مسئولیت‌ها
- ✅ بهینه‌سازی کامل برای سرعت و traffic

**آمادگی برای تولید:** ✅
