# Architecture: Providers ↔ Subscriptions Mapping

## مسئله فعلی

- **providers.json**: تعریف کانال‌های Telegram/GitHub/HTTP و نحوه جمع‌آوری
- **subscriptions.json**: تعریف فایل‌های خروجی و نام‌شان

**سؤال**: ارتباط میان آن‌ها چگونه باید تعریف شود؟

---

## راه‌حل پیشنهادی

### **Option 1: Provider-centric (ساده‌ترین)**

هر provider می‌تواند چندین subscription تولید کند.

```json
// providers.json
{
  "providers": [
    {
      "name": "telegram",
      "enabled": true,
      "type": "telegram",
      "subscriptions": ["Telegram-List1", "Telegram-List2"],
      "source": {
        "channels": [
          {"channel": "https://t.me/Capoit", "subscriptions": ["Telegram-List1"]},
          {"channel": "https://t.me/ConfigsHUB", "subscriptions": ["Telegram-List1", "Telegram-List2"]}
        ]
      }
    }
  ]
}

// subscriptions.json
{
  "subscriptions": [
    {
      "name": "default",
      "enabled": true,
      "subscription_name": "Telegram-List1",
      "format": "plain",
      "provider": "telegram"
    },
    {
      "name": "list2",
      "enabled": true,
      "subscription_name": "Telegram-List2",
      "format": "plain",
      "provider": "telegram"
    }
  ]
}
```

---

### **Option 2: Subscription-centric (انعطاف‌پذیرتر)**

هر subscription می‌تواند از کانال‌های مختلف جمع‌آوری کند.

```json
// subscriptions.json
{
  "subscriptions": [
    {
      "name": "default",
      "enabled": true,
      "subscription_name": "Telegram-List1",
      "format": "plain",
      "sources": [
        {
          "provider": "telegram",
          "channels": ["https://t.me/Capoit", "https://t.me/ConfigsHUB"]
        }
      ]
    },
    {
      "name": "list2",
      "enabled": true,
      "subscription_name": "Telegram-List2",
      "format": "plain",
      "sources": [
        {
          "provider": "telegram",
          "channels": ["https://t.me/daily_configs", "https://t.me/VmessProtocol"]
        }
      ]
    }
  ]
}
```

---

### **Option 3: Hybrid (توصیه‌شده)**

Default channel‌ها در `providers.json`، اما override در `subscriptions.json`.

```json
// providers.json
{
  "providers": [
    {
      "name": "telegram",
      "enabled": true,
      "type": "telegram",
      "source": {
        "channels": [
          {"channel": "https://t.me/Capoit", "limit": 5, "days": 1},
          {"channel": "https://t.me/ConfigsHUB", "limit": 5, "days": 1}
        ]
      }
    }
  ]
}

// subscriptions.json
{
  "subscriptions": [
    {
      "name": "default",
      "enabled": true,
      "subscription_name": "Telegram-List1",
      "format": "plain",
      "provider": "telegram"
      // استفاده از تمام کانال‌های telegram provider
    },
    {
      "name": "list2",
      "enabled": true,
      "subscription_name": "Telegram-List2",
      "format": "plain",
      "provider": "telegram",
      "channels": [
        "https://t.me/daily_configs",
        "https://t.me/VmessProtocol"
      ]
      // override: فقط این کانال‌ها
    }
  ]
}
```

---

## توصیه و مزایا

**من پیشنهاد می‌دهم Option 3 (Hybrid) زیرا:**

✅ **سادگی**: Default channel‌ها در `providers.json`  
✅ **انعطاف**: امکان customize کردن برای هر subscription  
✅ **maintainability**: کد runner کمتر پیچیده می‌شود  
✅ **reusability**: کانال‌های مشترک در چندین subscription  

---

## Implementation Plan

اگر میخواهیم Option 3 را پیاده‌سازی کنیم:

### 1. Update Models
- اضافه کردن `provider` فیلد به `Subscription` model
- اضافه کردن `channels` فیلد (optional) به `Subscription` model

### 2. Update Config Loader
- خواندن `provider` و `channels` از subscriptions.json

### 3. Update Runner
- برای هر subscription، provider مرتبط را پیدا کن
- اگر `channels` override تعریف شده، از آن استفاده کن
- ورنه، تمام کانال‌های provider را استفاده کن

### 4. Update Workflow
- ثابت می‌ماند، چون runner خود مدیریت می‌کند

---

## مثال عملی

```json
// config/subscriptions.json
{
  "subscriptions": [
    {
      "name": "default",
      "enabled": true,
      "subscription_name": "Telegram-List1",
      "format": "plain",
      "provider": "telegram"
      // تمام کانال‌های تعریف‌شده در config/providers.json
    },
    {
      "name": "vpn_only",
      "enabled": true,
      "subscription_name": "Telegram-VPN-Only",
      "format": "plain",
      "provider": "telegram",
      "channels": [
        "https://t.me/Best_internet_iran",
        "https://t.me/Persianvpnhub",
        "https://t.me/PrivateVPNs"
      ]
      // فقط VPN-related channels
    },
    {
      "name": "daily",
      "enabled": true,
      "subscription_name": "Telegram-Daily",
      "format": "plain",
      "provider": "telegram",
      "channels": [
        "https://t.me/daily_configs"
      ]
      // فقط daily configs
    }
  ]
}
```

**Generated Files:**
- `Telegram-List1.txt` - همه کانال‌ها
- `Telegram-VPN-Only.txt` - فقط VPN channels
- `Telegram-Daily.txt` - فقط daily channel

---

## آیا می‌خواهیم این تغییرات را پیاده‌سازی کنیم؟

اگر بله، لطفاً بگویید:
- ✅ Option 3 (Hybrid) را پیاده‌سازی کنیم
- 🔄 یا تغییر برای یک option دیگر
