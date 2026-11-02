```markdown
# 📥 `downloads/` — vaqtinchalik video fayllar

Bu papka botning **ishchi maydoni**. `yt-dlp` yuklagan videolar shu yerga
vaqtincha saqlanadi, Telegram'ga yuborilgach o'chiriladi.

> ⚠️ **Bu papkadagi fayllarni qo'lda o'chirmang** — bot ularni
> avtomatik boshqaradi. Faqat bot to'xtatilgan holatda tozalash mumkin.

---

## 🔄 Fayllar hayot sikli

```
Foydalanuvchi havola yuboradi
        │
        ▼
┌───────────────────────────────┐
│ yt-dlp videoni yuklaydi       │
│ → downloads/abc123_video.mp4  │   ← fayl shu yerda paydo bo'ladi
└───────────────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│ Telegram'ga yuboriladi        │
└───────────────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│ Fayl o'chiriladi              │   ← download.py::finally
│ → downloads/ bo'sh            │
└───────────────────────────────┘
```

Agar biror sabab bilan fayl o'chirilmasa (masalan, bot kutilmaganda
to'xtasa), `cleanup.py` har 10 daqiqada ishga tushib, **30 daqiqadan
eski** fayllarni supurib tashlaydi.

---

## 📁 Fayl nomlash qoidasi

Har bir yuklash uchun unikal prefiks qo'shiladi — bu parallel yuklashlarda
to'qnashuvning oldini oladi:

```
{uuid8}_{title}.{ext}
```

Masalan:

```
a3f9c2d1_Instagram_reel_by_user.mp4
b8e4f1a2_TikTok_dance_challenge.mp4
```

`restrictfilenames=True` sozlamasi tufayli fayl nomida faqat `a-z`, `0-9`,
`_` va `-` qoladi — Telegram, Linux va Windows uchun xavfsiz.

---

## 🚫 Nega bu papka `.gitignore` da?

- **Hajm** — videolar yuzlab megabayt bo'lishi mumkin, git repo shishib ketadi
- **Maxfiylik** — foydalanuvchi yuklagan videolar repo'ga tushmasligi kerak
- **Vaqtinchalik** — bu fayllar doimiy saqlanish uchun emas

`.gitignore` da:

```gitignore
downloads/*
!downloads/README.md
```

`!downloads/README.md` qatori — "bu faylni **istisno** qil, git'ga qo'sh"
degan ma'noni bildiradi. Shu tufayli papka strukturasi saqlanadi, lekin
videolar kuzatilmaydi.

---

## 💾 Disk hajmi bo'yicha maslahatlar

| Holat | Tavsiya |
|---|---|
| Kichik bot (kuniga < 100 video) | Standart sozlamalar yetarli |
| O'rtacha bot (kuniga 100–1000 video) | `CLEANUP_MAX_AGE_MINUTES=10` qiling |
| Katta bot (kuniga > 1000 video) | Alohida disk yoki `tmpfs` ishlatish |
| Docker'da | Volume o'rniga **tmpfs** mount qiling — tezroq va avtomatik tozalanadi |

**tmpfs misoli** (`docker-compose.yml` da):

```yaml
services:
  bot:
    volumes:
      - type: tmpfs
        target: /app/downloads
        tmpfs:
          size: 1G
```

Bu holda `downloads/` operativ xotirada saqlanadi — diskka yozilmaydi va
konteyner qayta ishga tushganda avtomatik tozalanadi.

---

## 🔍 Muammolarni aniqlash

### Papka to'lib qolgan bo'lsa

```bash
du -sh downloads/
ls -lh downloads/ | wc -l
find downloads/ -type f -mmin +30 -delete
```

### `PermissionError` chiqsa

Bot foydalanuvchisi papkaga yozish huquqiga ega emas:

```bash
sudo chown -R botuser:botuser downloads/
chmod 755 downloads/
```

### Fayllar o'chirilmayotgan bo'lsa

Sabablari:

1. **`cleanup.py` ishlamayapti** — `main.py` da `_periodic_cleanup()` task
   ishga tushirilganini tekshiring
2. **Fayl boshqa jarayon tomonidan ushlab turilgan** — `lsof downloads/`
   bilan ko'ring
3. **`DOWNLOAD_DIR` noto'g'ri yo'lga ishora qiladi** — `python -m bot.config`
   buyrug'i bilan tekshiring

---

## 🧹 Qo'lda tozalash (bot to'xtatilgan holatda)

```bash
find downloads/ -type f ! -name "README.md" -delete
```

Yoki Python orqali:

```python
from bot.services import cleanup_old_files
removed = cleanup_old_files()
print(f"{removed} ta fayl o'chirildi")
```

---

## 📊 Monitoring (ixtiyoriy)

`bot/services/cleanup.py` ga quyidagi log qatorini qo'shsangiz, disk
holati `bot.log` da ko'rinadi:

```python
import shutil

total_size = sum(f.stat().st_size for f in DOWNLOAD_DIR.glob("*") if f.is_file())
free_space = shutil.disk_usage(DOWNLOAD_DIR).free
logger.info(
    "downloads/: %.1f MB ishlatilgan, %.1f GB bo'sh",
    total_size / (1024 * 1024),
    free_space / (1024 ** 3),
)
```

---

## 📌 Qisqa eslatma

| Savol | Javob |
|---|---|
| Bu papkani o'chirsam bo'ladimi? | Ha, bot qayta ishga tushganda avtomatik yaratiladi |
| Fayllarni git'ga qo'shsam bo'ladimi? | **Yo'q** — `.gitignore` da |
| Papka hajmi qancha bo'lishi normal? | Odatda 0–500 MB, undan ko'p bo'lsa cleanup ishlamayapti |
| Fayllar qachon o'chiriladi? | Telegram'ga yuborilgach darhol; xato bo'lsa 30 daqiqadan keyin |
| `README.md` ni o'chirsam bo'ladimi? | Yo'q — papka strukturasi uchun kerak |
```
