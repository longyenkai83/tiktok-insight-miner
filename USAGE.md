# 📖 USAGE — Quick reference cho Tuấn

> Copy-paste guide để dùng tool khi đã quên cú pháp. File này KHÔNG phải README cho người ngoài — chỉ là note cá nhân.

---

## 🌐 Web UI nội bộ (v0.3+) — cho nhân viên dùng

**Khi nào dùng**: anh có 5+ nhân viên cần chạy mà họ không quen PowerShell.

### Setup 1 lần (anh làm)

1. Install deps webapp:
   ```powershell
   pip install -e ".[webapp]"
   ```

2. (Optional) set password trong `.env`:
   ```
   WEBAPP_PASSWORD=tu-dat-password-day
   MAX_RUNS_PER_USER_PER_DAY=20
   ```
   Nếu để trống `WEBAPP_PASSWORD` = open access (chỉ dùng cho LAN tin cậy).

3. Chạy:
   - **Double-click** `start-webapp.bat` (đã in sẵn LAN IP)
   - Hoặc lệnh: `python -m streamlit run webapp.py --server.address 0.0.0.0` (dùng `python -m` vì `streamlit.exe` không trong PATH)

4. **Lấy LAN IP của máy** (start-webapp.bat tự in ra), chia sẻ với nhân viên:
   ```
   http://192.168.1.10:8501
   ```

### Hàng ngày

- **Anh**: để máy bật + chạy `start-webapp.bat`. Anh có thể tắt bằng Ctrl+C trong console.
- **Nhân viên**: mở browser → URL anh đưa → nhập tên/mã NV ở sidebar → paste niche slug + URLs → bấm "Chạy pipeline" → đợi 2-5 phút → download report.md + brief.md.

### Audit (anh xem khi cần)

File `usage_log.csv` ở project root tự append mỗi run:

| Cột | Ý nghĩa |
|---|---|
| `timestamp` | Khi nào |
| `user` | Tên/mã NV họ tự nhập |
| `niche` | Niche slug |
| `num_urls`, `num_comments` | Quy mô run |
| `with_brief` | Có brief không |
| `duration_s` | Mất bao lâu |
| `status` | `success` / `error` |
| `cost_est_usd` | Cost ước tính |

Mở bằng Excel để xem ai chạy gì khi nào, tổng cost bao nhiêu.

### Quota per-user

Mỗi user (theo tên họ nhập) bị giới hạn `MAX_RUNS_PER_USER_PER_DAY` runs/24h (default 20). Hết quota → phải đợi 24h. Nếu nhân viên đổi tên thì reset → đặt password gate hoặc nhắc nhân viên dùng đúng tên.

### Troubleshooting webapp

| Lỗi | Fix |
|---|---|
| `ModuleNotFoundError: streamlit` | `pip install -e ".[webapp]"` |
| `'streamlit' is not recognized` | Dùng `python -m streamlit` thay vì `streamlit` (đã fix trong start-webapp.bat) |
| Nhân viên không access được LAN IP | Check Windows Firewall — allow port 8501. Hoặc cùng wifi với máy anh. |
| Web hang khi run | Đó là pipeline đang chạy 2-5 phút. Đừng refresh. Status block hiển thị stage hiện tại. |
| Pipeline lỗi `401 Authentication` | Token Apify hoặc Anthropic hết hạn — anh check `.env` |

---

## 🌍 Mở rộng cho nhân viên REMOTE — Cloudflare Tunnel (v0.3.1+)

**Khi nào dùng**: nhân viên ở xa, khác wifi, không truy cập được LAN IP `192.168.2.45`.

**Tradeoff**: máy anh vẫn phải bật + chạy webapp 24/7 (như LAN), nhưng tunnel xuất ra URL public dạng `https://random.trycloudflare.com` cho nhân viên remote vào được. Free, không cần domain, không cần Cloudflare account.

### Setup 1 lần (anh làm)

#### Bước 1: Download `cloudflared.exe`

**Cách A — Manual download** (đơn giản nhất):
1. Vào https://github.com/cloudflare/cloudflared/releases/latest
2. Tải file `cloudflared-windows-amd64.exe`
3. Đổi tên thành `cloudflared.exe`
4. Đặt vào folder `d:\Projects\tiktok-insight-miner\` (cùng cấp với `webapp.py`)

**Cách B — winget** (PowerShell admin):
```powershell
winget install --id Cloudflare.cloudflared
```
(Sau khi cài xong, mở terminal mới để PATH update.)

#### Bước 2: BẮT BUỘC bật password

Edit `d:\Projects\tiktok-insight-miner\.env`, thêm/sửa:
```
WEBAPP_PASSWORD=mat-khau-anh-tu-dat-day
MAX_RUNS_PER_USER_PER_DAY=10
```

URL public ai có cũng vào được, **PHẢI có password** để tránh ai khám phá ra URL chạy abuse hết token của anh.

#### Bước 3: Chạy

Double-click `start-tunnel.bat`. Nó sẽ:
1. Check `cloudflared.exe` có không (nếu không, hướng dẫn anh tải)
2. Cảnh báo nếu chưa bật password
3. Mở **2 cửa sổ console**:
   - Cửa sổ 1: Streamlit local (port 8501)
   - Cửa sổ 2: Cloudflare Tunnel — sau ~10s sẽ in ra **URL public**

**Tìm URL ở cửa sổ 2**, dòng dạng:
```
https://something-something-xyz.trycloudflare.com
```

### Hàng ngày

- **Anh**: để 2 cửa sổ console luôn mở. Tắt = remote không vào được nữa.
- **Nhân viên remote**: paste URL `trycloudflare.com` → nhập password (anh gửi riêng) → dùng như LAN.

### ⚠️ Đặc điểm Quick Tunnel

- **URL đổi mỗi lần restart** tunnel. Anh phải gửi URL mới cho nhân viên mỗi sáng nếu restart máy.
- Muốn URL **không đổi** → cần Named Tunnel (có account Cloudflare + domain riêng) — phức tạp hơn, em scaffold riêng nếu anh cần.
- **Giới hạn miễn phí**: vài chục req/giây OK cho 5-10 nhân viên dùng. Vượt nhiều hơn cần upgrade.

### Template message cho nhân viên remote

> **Hi cả nhà, nhân viên ở xa dùng tool TikTok Insight Miner ở link sau:**
>
> **URL**: https://xxxxx.trycloudflare.com  *(URL hôm nay, có thể đổi → đợi anh gửi URL mới)*
> **Password**: tt2026  *(thay bằng password anh đặt)*
>
> **Hướng dẫn dùng**:
> 1. Mở Chrome/Edge → paste URL → nhập password
> 2. Sidebar: nhập tên/mã NV (vd `nv_minh`)
> 3. Niche: kebab-case (vd `skincare-acne`)
> 4. Paste TikTok URLs (mỗi dòng 1)
> 5. Bấm "🚀 Chạy pipeline" → đợi 2-5 phút (đừng đóng tab)
> 6. Tải `report.md` + `brief.md` về máy
>
> **Quota**: 10 lần/người/ngày. Lỗi → screenshot gửi anh.

### Troubleshooting tunnel

| Lỗi | Fix |
|---|---|
| `cloudflared` không nhận lệnh | Chưa download, theo Bước 1 phía trên |
| Tunnel start nhưng không có URL `trycloudflare.com` | Đợi thêm 30s. Hoặc Cloudflare đang sự cố — restart `start-tunnel.bat` |
| Nhân viên vào URL bị `502 Bad Gateway` | Cửa sổ Streamlit (cửa sổ 1) bị crash — restart `start-tunnel.bat` |
| URL hôm nay khác hôm qua | Bình thường — Quick Tunnel sinh URL mới mỗi lần restart. Cần URL persistent → upgrade Named Tunnel (hỏi em) |

---

## ⚡ Workflow chuẩn (5 phút)

### 1. Mở PowerShell tại project

**Cách nhanh**: Vào `D:\Projects\tiktok-insight-miner` trong File Explorer → Click phải → **"Open in Terminal"**.

Hoặc:
```powershell
cd d:\Projects\tiktok-insight-miner
```

### 2. Init niche folder (recommended) — `tim init`

Auto tạo folder `output/<niche>/<date>/` với template + update master index + in lệnh `run` sẵn để copy-paste:

```powershell
python -m tiktok_insight_miner init skincare-acne
# → output/skincare-acne/2026-05-03/{urls.txt, notes.md}
# → output/_index.md (cập nhật)
# → in lệnh `run` sẵn ra terminal
```

**Niche slug rules:** kebab-case, càng cụ thể càng tốt. Tốt: `skincare-acne`, `food-banh-mi-saigon`, `parenting-newborn-feeding`. Kém: `food`, `business`.

**Override date** (re-run niche cũ): `--date 2026-05-10`.

Sau init: edit `urls.txt` paste URLs → copy-paste lệnh `run` từ terminal output.

---

### 2b. (Cách cũ — bỏ qua nếu đã dùng `init`) Chuẩn bị URL thủ công

**1-2 video**: paste thẳng vào lệnh.

**Nhiều video**: tạo file `output\<niche>-urls.txt`:
```
# Niche XYZ - YYYY-MM-DD
https://www.tiktok.com/@user1/video/123
https://www.tiktok.com/@user2/video/456
```

### 3. Chạy (template chính)

**Đầy đủ — scrape + classify + report + brief:**

```powershell
python -m tiktok_insight_miner run `
  --urls-file "output\<NICHE>-urls.txt" `
  --max-comments 100 `
  --with-angles `
  -o "output\<NICHE>-2026-MM-DD"
```

**1 video nhanh:**

```powershell
python -m tiktok_insight_miner run `
  --urls "https://www.tiktok.com/@USER/video/ID" `
  --max-comments 100 `
  --with-angles `
  -o "output\<NICHE>-2026-MM-DD"
```

### 4. Đọc kết quả

Mở folder output, có 4 file:

| File | Để làm gì |
|---|---|
| `report.md` | **Insight chính** — pain/desire/question theo bucket, top quotes |
| `brief.md` | **Content brief** — 10 angle hoàn chỉnh (hook + script + CTA) |
| `classified.json` | Raw data classified (dùng để re-generate brief với prompt khác) |
| `raw_comments.json` | Backup raw từ Apify |

---

## 🎛 Tham số hay dùng

| Flag | Mặc định | Khi nào đổi |
|---|---|---|
| `--max-comments N` | 100 | Niche viral nhiều comment → 200; test → 50 |
| `--with-angles` | off | **Luôn bật** nếu cần content brief |
| `--num-angles N` | 10 | Cần ít hơn → 5; muốn library lớn → 20 |
| `--model X` | từ `.env` (Haiku) | Quality cao hơn → `claude-opus-4-7` (cost 5-10x) |
| `--suggester-model X` | giống `--model` | Chỉ để override riêng cho stage suggest |
| `--batch-size N` | 20 | Tăng lên 30 nếu API ổn (ít request hơn, rẻ hơn chút) |

---

## 🔁 Re-generate brief từ data cũ (không tốn Apify)

Có `classified.json` rồi, muốn thử prompt/model khác:

```powershell
python -m tiktok_insight_miner suggest `
  -i "output\<OLDFOLDER>\classified.json" `
  -o "output\<OLDFOLDER>\brief-v2.md" `
  --num 15 `
  --model claude-opus-4-7
```

## 🔁 Chạy từng stage riêng

```powershell
# Chỉ scrape (giữ raw để dùng sau)
python -m tiktok_insight_miner scrape --urls-file "..." --max-comments 100 -o "output\X\raw.json"

# Chỉ classify (từ raw có sẵn)
python -m tiktok_insight_miner classify -i "output\X\raw.json" -o "output\X\classified.json"

# Chỉ report
python -m tiktok_insight_miner report -i "output\X\classified.json" -o "output\X\report.md"

# Chỉ suggest (yêu cầu đã có classified)
python -m tiktok_insight_miner suggest -i "output\X\classified.json" -o "output\X\brief.md"
```

---

## 💰 Cost (template phổ biến)

| Workflow | Apify | Claude | Tổng |
|---|---|---|---|
| 1 video, 100 cmt, không brief | $0.05 | $0.02 | **~$0.07** |
| 3 videos, 100 cmt, có brief (Haiku) | $0.20 | $0.10 | **~$0.30** |
| 5 videos, 200 cmt, có brief (Haiku) | $0.50 | $0.20 | **~$0.70** |
| 5 videos, 200 cmt, có brief (**Opus 4.7**) | $0.50 | $1.00+ | **~$1.50+** |

---

## ⚠️ Trước khi chạy — checklist

- [ ] `.env` còn token hợp lệ (Apify + Anthropic chưa hết hạn / hết quota)
- [ ] Folder output đặt tên không có khoảng trắng (dùng `-` hoặc `_`)
- [ ] Nếu re-run cùng folder → file cũ sẽ bị **ghi đè** (backup nếu cần giữ)
- [ ] URLs là TikTok video URL (không phải profile, không phải share short URL `vm.tiktok.com`)

---

## 🐛 Troubleshooting nhanh

| Lỗi | Nguyên nhân | Fix |
|---|---|---|
| `401 Authentication` | Token sai/hết hạn | Renew ở console.anthropic.com hoặc console.apify.com |
| `apify run trả về None` | Hết quota Apify | Check Apify dashboard, có thể cần upgrade plan |
| `UnicodeEncodeError cp1252` | Terminal không UTF-8 | Đã fix trong `cli.py` v0.1.1+, chạy `pip install -e .` lại nếu cần |
| Apify scrape rất chậm | Video viral 100K+ comment | Giảm `--max-comments` xuống 50-100 |
| `tim` không nhận lệnh | `tim.exe` không trong PATH | Dùng `python -m tiktok_insight_miner` thay |
| Brief có vài angle "lệch" | Haiku đôi khi suy diễn | Re-run suggest với `--model claude-opus-4-7` |

---

## 🆙 Update dependencies (tháng/quý 1 lần)

```powershell
cd d:\Projects\tiktok-insight-miner
pip install -e . --upgrade
```

---

## 🔄 Backup output trước khi xóa

Folder `output/` chứa data anh đã trả tiền scrape — đừng xóa nhanh. Trước khi cleanup:

```powershell
# Zip backup ra ngoài
Compress-Archive -Path "output\*" -DestinationPath "..\insight-backup-2026-MM-DD.zip"
```

---

## 📝 Bucket ý nghĩa (v0.1.1+)

| Bucket | Để làm gì với nó |
|---|---|
| `pain` | **Content angle priority #1** — pain solution video |
| `desire` | Aspiration video, before/after, dream-state content |
| `question` | **FAQ video opportunity** — mỗi câu hỏi 1 short |
| `objection` | Myth-busting video, counter-narrative |
| `praise` | Testimonial repurpose, quote graphic, social proof |
| `mention` | (Ignore cho content) — chỉ là engagement signal |
| `other` | (Ignore) — sticker, off-topic, spam |

---

**Updated**: 2026-05-03 (v0.2.0)
