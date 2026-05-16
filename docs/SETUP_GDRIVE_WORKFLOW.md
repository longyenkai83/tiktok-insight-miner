# Setup Google Drive Workflow — Multi-Machine CoWork Pull

> **Phiên bản**: v1 (2026-05-16)
> **Mục đích**: setup Google Drive sync để CoWork máy nào cũng pull insight về được — không cần truy cập miner local
> **Audience**: anh Tuấn (setup 1 lần) + chị Hiền (cài Drive Desktop trên máy chị)

---

## 1. Vấn đề giải quyết

| Trước (chỉ local) | Sau (có Drive sync) |
|---|---|
| Miner output ở `D:\Projects\tiktok-insight-miner\output\...` | + snapshot tự lên Drive cloud |
| CoWork phải cùng máy mới đọc được | CoWork máy nào cũng pull được qua Drive sync |
| Đi máy khác = mất link insight | Đi máy khác = Drive sync tự kéo file mới về |

---

## 2. Architecture

```
┌───────────────────────────────────────────────────────────────┐
│ PC anh (Windows)                                              │
│                                                               │
│  Miner local                  Drive Desktop                   │
│  ────────────                 ──────────────                  │
│  D:\Projects\...\             G:\My Drive\                    │
│   _master\                      tiktok-miner-shared\          │
│    insights-pack-for-           insights-packs\               │
│    cowork.md                     kinh-doanh-27-45\            │
│        │                          insights-pack_v1.md         │
│        │ snapshot                 insights-pack_v2.md         │
│        └──────────────────────►   insights-pack_v3.md         │
│                                          │                    │
└──────────────────────────────────────────┼────────────────────┘
                                           │ Drive sync
                                           ▼
                                  ┌─────────────────────┐
                                  │ Google Drive Cloud  │
                                  │ tiktok-miner-shared │
                                  └──────────┬──────────┘
                                             │
            ┌────────────────────────────────┴──────────────┐
            │                                               │
            ▼                                               ▼
   ┌─────────────────────┐                       ┌─────────────────────┐
   │ Máy 2 (chị Hiền)    │                       │ Máy 3 (anh khi đi)  │
   │ Drive Desktop sync  │                       │ Drive Desktop sync  │
   │ G:\My Drive\...     │                       │ G:\My Drive\...     │
   │       │             │                       │       │             │
   │       ▼             │                       │       ▼             │
   │ CoWork pull skill   │                       │ CoWork pull skill   │
   │ → inputs/v1.md      │                       │ → inputs/v1.md      │
   └─────────────────────┘                       └─────────────────────┘
```

---

## 3. Setup (1 lần)

### 3.1 Anh — PC chính (15 phút)

**Bước 1**: Cài Google Drive Desktop
- Download: https://www.google.com/drive/download/
- Login với account `lenguyentuan1983@gmail.com`
- Sync mặc định map vào ổ `G:` (Windows) hoặc `/Volumes/GoogleDrive` (Mac)

**Bước 2**: Verify folder cấu trúc đã có
- Path local: `G:\My Drive\tiktok-miner-shared\insights-packs\`
- (Đã tạo từ trước, em đã verify accessible)

**Bước 3**: Add env var vào `.env` của miner
```env
INSIGHTS_PACK_DRIVE_DIR=G:\My Drive\tiktok-miner-shared\insights-packs
```
→ Mở file `D:\Projects\tiktok-insight-miner\.env` (notepad), copy dòng trên vào cuối file, save.

**Bước 4**: Test
```powershell
# Từ folder D:\Projects\tiktok-insight-miner
python -m tiktok_insight_miner export-for-cowork `
  -i output\kinh-doanh-27-45\_master\selected_angles.json `
  --config niche_configs\kinh-doanh-27-45.json
```
→ Console sẽ in:
```
Snapshot to Drive: G:\My Drive\tiktok-miner-shared\insights-packs\kinh-doanh-27-45\insights-pack_v<N>.md
```

→ Verify file đã có ở local Drive folder + sync lên cloud (mở https://drive.google.com check folder).

### 3.2 Chị Hiền — Máy chị (10 phút)

**Bước 1**: Anh share folder Drive với chị Hiền
- Trên Drive web: mở folder `tiktok-miner-shared`
- Right-click → **Share** → add email chị Hiền
- Set role = **Viewer** (chỉ đọc — chị không nên ghi vào folder này)

**Bước 2**: Chị cài Drive Desktop
- Cùng link: https://www.google.com/drive/download/
- Login bằng email chị

**Bước 3**: Chị accept share folder
- Trên Drive web (chị Hiền login): folder `tiktok-miner-shared` xuất hiện ở **"Shared with me"**
- Right-click folder → **"Add shortcut to Drive"** → chọn vị trí trong My Drive của chị
- Drive Desktop sẽ sync folder đó về local (vài giây-vài phút tuỳ dung lượng)

**Bước 4**: Verify
- Chị mở File Explorer → đường dẫn (vd) `G:\Shared drives\tiktok-miner-shared\insights-packs\kinh-doanh-27-45\`
- Thấy file `insights-pack_v1.md` = OK

→ **Lưu ý**: path local của chị **khác path local của anh** vì Drive Desktop layout khác giữa "My Drive" vs "Shared". Chị note lại path chính xác để khi build CoWork pull skill biết đường.

---

## 4. Workflow vận hành hằng ngày

### 4.1 Anh / nhân viên — chạy miner

**Option A — CLI** (anh, nhanh):
```powershell
python -m tiktok_insight_miner run --urls-file ... -o output\<niche>\<date>
python -m tiktok_insight_miner bank -i .../classified.json --config niche_configs/<niche>.json
# (tick [x] trong 3-lựa-chọn.md)
python -m tiktok_insight_miner select -i .../3-lựa-chọn.md
python -m tiktok_insight_miner export-for-cowork `
  -i .../_master/selected_angles.json `
  --config niche_configs/<niche>.json
# → tự snapshot lên Drive vì có env var INSIGHTS_PACK_DRIVE_DIR trong .env
```

**Option B — Web UI** (nhân viên, qua tunnel):
- Vào URL `https://insight.lenguyenkhang.com`
- Login với password (anh set trong `.env` WEBAPP_PASSWORD)
- Paste niche + URLs → bấm "Chạy pipeline"
- (Hiện tại webapp chỉ chạy Bước 1-2: scrape + classify + report. Bước 3-4 vẫn manual qua CLI bên anh.)

→ Sau khi `tim export-for-cowork` chạy xong, file insight pack tự lên Drive cloud trong vài giây.

### 4.2 Chị Hiền — pull insight về CoWork

Mở session CoWork (bất kỳ máy nào có Drive Desktop sync):

1. Trigger skill `pull-insights-from-miner` (sẽ build session sau)
2. Skill đọc file từ `G:\Shared drives\tiktok-miner-shared\insights-packs\<niche>\insights-pack_v<latest>.md`
3. Skill save vào `WORK AREAS\Marketing\<project>\inputs\insights-pack_v<n>.md`
4. CoWork log vào `memory.md` project

→ Hoặc đơn giản hơn: chị Hiền **copy tay** file từ Drive folder sang CoWork inputs/ (zero code).

---

## 5. Versioning logic

Mỗi lần chạy `tim export-for-cowork --snapshot-to ...` (hoặc có env var):

| Lần | File mới tạo |
|---|---|
| 1 | `insights-pack_v1.md` |
| 2 | `insights-pack_v2.md` (giữ v1) |
| 3 | `insights-pack_v3.md` (giữ v1, v2) |
| N | `insights-pack_v<N>.md` |

→ **Không bao giờ ghi đè** file cũ. Tuân CoWork rule "Never delete files".

→ Chị Hiền pull về CoWork có thể dedup theo insight `id` (không phải file version).

---

## 6. Permission Drive — security cảnh báo

⚠️ **Hiện tại folder `insights-packs/` có permission `anyone = writer`** — ai có link đều ghi/xoá được.

**Em recommend đổi sang 1 trong 2 phương án**:

### Option 1 — Restricted + share email chị Hiền (tightest)
1. Drive web → folder `tiktok-miner-shared` → Share
2. "General access" → đổi từ "Anyone with the link" sang **"Restricted"**
3. Add email chị Hiền với role **"Viewer"**
4. Bất kỳ ai khác có link đều không vào được

### Option 2 — Anyone = reader (looser)
1. Đổi role `anyone` từ **writer** → **reader**
2. Ai có link đọc được, nhưng không ghi/xoá được
3. OK nếu anh không lo leak link

→ Option 1 an toàn hơn — nhất là khi anh có nhiều brand sau này.

---

## 7. Troubleshooting

| Triệu chứng | Fix |
|---|---|
| Console in `Snapshot dir không tồn tại` | Anh chưa cài Drive Desktop, hoặc path env var sai. Check `echo $env:INSIGHTS_PACK_DRIVE_DIR` (PowerShell) |
| File ở local Drive folder nhưng chưa thấy trên Drive web | Drive sync chưa kịp đẩy lên — đợi 30s-2 phút. Hoặc check Drive Desktop icon (system tray) xem có lỗi sync không |
| Chị Hiền không thấy folder shared | Anh chưa share, hoặc chị chưa add shortcut vào Drive. Check share permission ở Drive web |
| Path local chị Hiền khác PC anh | Bình thường — "My Drive" vs "Shared drives" có path khác. Mỗi máy note path local riêng |
| File `desktop.ini` xuất hiện trong folder | Windows tự tạo, ignore (không ảnh hưởng) |
| Snapshot tạo file `_v999.md` (số quá to) | Có file naming sai trong folder. Manual clean tay hoặc rename theo pattern `insights-pack_v<N>.md` |

---

## 8. Cost & limit

| Item | Cost | Limit |
|---|---|---|
| Google Drive free tier | $0 | 15GB (đủ cho hàng nghìn niche) |
| Drive Desktop | $0 | — |
| Sync speed | $0 | Phụ thuộc internet (vài giây - vài phút) |
| Số version per niche | $0 | Unlimited (mỗi run = 1 file mới) |

→ Nếu sau này dung lượng vượt 15GB → upgrade Drive ($1.99/tháng cho 100GB).

---

## 9. Future improvements (chưa làm)

- **Auto cleanup version cũ**: keep N version mới nhất per niche, archive cái cũ vào subfolder `_archive/`
- **Webhook**: sau khi snapshot xong, ping vào Slack/Telegram báo CoWork có batch mới
- **Webapp auto-export**: webapp chạy hết Bước 1-4 (gồm tick UI) + auto snapshot — tránh anh phải mở CLI
- **Pull skill CoWork**: bên CoWork build skill `pull-insights-from-miner` để auto pull khi Hiền nói "lấy insight mới về"

---

## 10. Tài liệu liên quan

- [SOP_CLONE_NICHE.md](SOP_CLONE_NICHE.md) — Playbook clone niche mới (Phase 4 có bước snapshot)
- [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) — Sơ đồ flow tổng
- [MAPPING_FREEDOM_LAYER.md](MAPPING_FREEDOM_LAYER.md) — Mapping cho CoWork
- [../README.md](../README.md) — Quick start tool
- [../.env.example](../.env.example) — Template config (có `INSIGHTS_PACK_DRIVE_DIR`)

---

**Updated**: 2026-05-16 · v1
**Tinh thần**: Google Drive làm "OneDrive cho insight" — miner ghi, CoWork đọc, máy nào cũng access được. Zero infra phức tạp.
