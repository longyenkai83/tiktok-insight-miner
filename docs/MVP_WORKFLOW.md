# MVP Workflow — TikTok Insight Miner

> Hướng dẫn sử dụng MVP hiện tại (v0.4 — 2026-05-08).
> Niche test: **phụ nữ 27–45 tuổi làm kinh doanh**.
> Dành cho: anh Tuấn + nhân viên trong team.

---

## 1. App này dùng để làm gì

Biến **comment TikTok thật** của audience thành **brief sản xuất nội dung sẵn sàng quay**.

```
TikTok URLs → Comment thật → Insight phân loại → Anh chọn vấn đề → Brief 60s/angle
```

Không đoán mò người xem cần gì. Không lấy ý tưởng từ "tham khảo" KOL khác. Lấy thẳng từ chính lời họ viết trong comment.

---

## 2. Khi nào dùng

- ✅ Khi muốn **research audience** trước khi mở kênh / sản phẩm / khóa học mới
- ✅ Khi muốn tìm **pain / desire / question THẬT** của thị trường, không phải brainstorm trên giấy
- ✅ Khi muốn **tạo content** ground vào demand thật (proof bằng quote + likes)
- ✅ Khi đang **bí ý tưởng**, không biết quay gì tuần này
- ✅ Khi muốn **đo trend** comment audience theo tuần / tháng / niche khác nhau

❌ KHÔNG phù hợp khi:
- Muốn scrape video / transcript (app này chỉ scrape comment)
- Muốn analytics dashboard view-time, retention (app này về **insight**, không phải metrics)
- Cần real-time monitoring (app chạy theo batch run, không stream)

---

## 3. Input cần chuẩn bị

| Thứ | Cụ thể | Ghi chú |
|---|---|---|
| **TikTok video URL** | 3–5 video cùng niche | URL dạng `https://www.tiktok.com/@user/video/123...`, KHÔNG phải profile URL hay short share `vm.tiktok.com` |
| **Niche slug** | `kinh-doanh-27-45` (đã có config) | Dùng kebab-case, tránh khoảng trắng |
| **Max comments / video** | 100–200 | Mặc định 100. Niche viral nhiều cmt → tăng lên 200. Test → 50 |
| **API keys** (`.env`) | `APIFY_TOKEN` + `ANTHROPIC_API_KEY` | Đã có sẵn trong `.env` |

**Niche config có sẵn**: [niche_configs/kinh-doanh-27-45.json](../niche_configs/kinh-doanh-27-45.json)
- 9 nhóm vấn đề chính (KINH_DOANH_KIET_SUC, GIA_TRI_BAN_THAN, TIEN_BAC_BINH_YEN, ...)
- Persona + positioning + tone + anti-pattern
- Scoring rules + thresholds

---

## 4. Full workflow 4 bước

### Bước 1: Run pipeline gốc để có `classified.json`

Lệnh đã có sẵn từ trước. Chọn 1 trong 3 cách:

**Cách A — All-in-one (khuyên dùng)**:
```powershell
python -m tiktok_insight_miner run `
  --urls-file "output/kinh-doanh-27-45/2026-05-08/urls.txt" `
  --max-comments 100 `
  -o "output/kinh-doanh-27-45/2026-05-08"
```

**Cách B — Web UI**:
- Anh: chạy `start-tunnel.bat` → đưa URL public + password cho nhân viên
- Nhân viên: mở URL → điền niche slug + URLs → bấm "🚀 Chạy pipeline" → đợi 2–5 phút

**Cách C — Init niche folder mới**:
```powershell
python -m tiktok_insight_miner init kinh-doanh-27-45
# → tạo output/kinh-doanh-27-45/<today>/{urls.txt, notes.md}
# → in lệnh `run` để copy-paste
```

**Output**: `output/kinh-doanh-27-45/<date>/classified.json`

→ **Cần file này** để chạy Bước 2.

---

### Bước 2: Bank — Liệt kê + Sắp xếp

```powershell
python -m tiktok_insight_miner bank `
  -i "output/kinh-doanh-27-45/<date>/classified.json" `
  --config "niche_configs/kinh-doanh-27-45.json"
```

**Output 3 file** trong cùng folder:

| File | Vai trò |
|---|---|
| `1-liệt-kê.csv` | **Mọi insight** đã loại praise/mention/other, Excel-friendly, có cột `status` để track |
| `2-sắp-xếp.md` | Group theo 9 nhóm + Top 10 cross-niche + UNCLASSIFIED section |
| `3-lựa-chọn.md` | Top 30 candidates (score ≥ 20), dạng checkbox `[ ]` |

**Console output sẽ in**:
```
📊 Niche: kinh-doanh-27-45
   Total insights đọc:   100
   Giữ lại (actionable): 58
   Loại do bucket:       42 (praise/mention/other)
```

→ Nếu UNCLASSIFIED >40% → **Bước 2.5: tune config** (xem [SOP](SOP_BUILD_INSIGHT_DRAFT.md) section 6.5).

---

### Bước 3: Người dùng tick `[x]`

**Mở `3-lựa-chọn.md` trong VS Code** (hoặc text editor). Đọc top candidates, tick `[x]` vào 5–10 angle muốn quay tuần này.

```markdown
- [ ] `[SCORE 226]` `[Q001 TIEN_BAC_BINH_YEN]` `[FAQ_ANSWER]` "Phải chăng… ta lại không biết trân trọng?" — @anhsangtrithucc (209 likes)

→ đổi thành →

- [x] `[SCORE 226]` `[Q001 TIEN_BAC_BINH_YEN]` `[FAQ_ANSWER]` "Phải chăng… ta lại không biết trân trọng?" — @anhsangtrithucc (209 likes)
```

Cả `[x]` lẫn `[X]` đều OK. Khoảng trắng `[ x ]` cũng OK.

**Quy tắc tick**:
- ✅ Tick angle nào **trúng định vị thương hiệu** + **anh đủ hiểu để nói thật về chủ đề đó**
- ✅ Mix nhóm vấn đề (đừng tick 10 cái cùng `TIEN_BAC_BINH_YEN`)
- ❌ Đừng tick chỉ vì score cao nếu không phải topic anh muốn nói
- ❌ Đừng tick quá nhiều — 5–10 cái là đủ cho tuần đầu

---

### Bước 4: Select — chuyển insight đã chọn vào pipeline

```powershell
python -m tiktok_insight_miner select `
  -i "output/kinh-doanh-27-45/<date>/3-lựa-chọn.md"
```

**Output 2 file** trong `output/kinh-doanh-27-45/_master/`:

| File | Vai trò |
|---|---|
| `content-pipeline.md` | Markdown table cho anh **browse + track status** (`todo` / `doing` / `done` / `skip`) |
| `selected_angles.json` | Full data **cho stage Production** đọc — không phải parse markdown lần nữa |

**Ghi chú**:
- File này **idempotent** — chạy nhiều lần không sợ mất data
- Nếu anh đã đổi status `doing` tay trong `content-pipeline.md` → re-run KHÔNG ghi đè
- Tuần sau tick thêm 5 angle khác → chạy lại → pipeline tự cộng dồn

**Edge case**: nếu chưa tick gì → tool in message rõ + KHÔNG tạo file rỗng.

---

### Bước 5: Production — generate brief sản xuất

```powershell
# Default — dùng Claude (Opus 4.7 từ .env)
python -m tiktok_insight_miner production `
  -i "output/kinh-doanh-27-45/_master/selected_angles.json" `
  --config "niche_configs/kinh-doanh-27-45.json"
```

**Output**: folder `output/kinh-doanh-27-45/4-thực-thi/` với mỗi angle = 1 file:

```
4-thực-thi/
├── angle-01-tien-bac-binh-yen-khong-tran-trong-khi-du.md
├── angle-02-tien-bac-binh-yen-luong-cao-khong-hanh-phuc.md
├── ...
```

**Mỗi file có 10 sections**:
1. Metadata · 2. Insight gốc · 3. Big idea · 4. Hook (5 variants) · 5. Script 60s
6. B-roll & Visual · 7. Caption · 8. CTA · 9. Checklist quay · 10. Post-mortem

**Cost ước tính**:
- Opus 4.7: ~$0.05–0.15/angle × N angle
- Haiku 4.5: ~$0.005/angle × N (rẻ hơn 10×, chất lượng vẫn dùng được)

**Flag hữu ích**:
| Flag | Khi nào dùng |
|---|---|
| `--limit 1` | Test 1 angle trước, tiết kiệm cost |
| `--no-claude` | Fallback template (không tốn API, chất lượng thấp hơn) |
| `--overwrite` | Re-gen file đã có (vd anh đổi prompt trong code) |
| `--model claude-haiku-4-5` | Generate hết với Haiku để rẻ |

---

## 5. Cách đọc từng file output

### `1-liệt-kê.csv` — Excel filter

**Mở bằng Excel** (file đã encode `utf-8-sig`, mở thẳng không bị mojibake).

**Workflow**:
1. AutoFilter columns `bucket`, `problem_code`, `intent_label`, `opportunity_label`
2. Sort theo `demand_score` desc
3. Filter `bucket=pain` để chỉ xem nỗi đau
4. Edit cột `status` thành `doing/done/skip` để track tay (KHÔNG được pipeline đọc lại)

→ **Dùng khi**: muốn deep-dive 1 nhóm cụ thể, hoặc xuất sang Notion/Airtable.

### `2-sắp-xếp.md` — Browse có cấu trúc

**Mở bằng VS Code** (preview markdown bằng `Ctrl+K V`).

**Đọc theo thứ tự**:
1. Section "📊 Tổng quan 9 nhóm" → biết nhóm nào nóng tuần này
2. Section "🔥 Top 10 cross-niche" → 10 insight mạnh nhất xuyên 9 nhóm
3. Section "📁 Chi tiết từng nhóm" → deep-dive khi muốn quay series 1 chủ đề
4. Section "⚠️ Unclassified" → quote nào bị rớt → gợi ý keyword bổ sung config

→ **Dùng khi**: research theme, tìm angle quay series.

### `3-lựa-chọn.md` — Tick để chọn

**Mở bằng VS Code** trong cùng project.

**Cách tick**:
- Click chuột vào ô `[ ]` → gõ `x` (hoặc `X`)
- Hoặc Ctrl+F → "- [ ]" → replace từng cái

→ **Dùng khi**: chọn angle quay tuần này. Đây là **bước CHIẾN LƯỢC** — anh quyết, không phải AI.

### `_master/content-pipeline.md` — Track production status

**Mở bằng VS Code**. Có table:
```
| ID | Status | Score | Problem | Quote | Author | Source Run | Next Step |
```

**Edit cột `Status` tay** khi production:
- `todo` → `doing` (đã giao team quay)
- `doing` → `done` (đã đăng)
- `doing` → `skip` (quyết định không quay)

Re-run `tim select` KHÔNG reset status anh đã đổi.

→ **Dùng khi**: hỏi "tuần này có bao nhiêu angle pending?" → mở file này.

### `_master/selected_angles.json` — Cho module Production

**KHÔNG đọc tay** — đây là machine input cho stage Production.

→ **Dùng khi**: debug, hoặc backup trước khi chạy `tim production --overwrite`.

### `4-thực-thi/angle-XX.md` — Cho team content

**1 file = 1 video TikTok 60s**.

**Phân vai**:
| Vai trò | Đọc section nào |
|---|---|
| **Anh** (strategic) | Section 3 (Big idea) + 4 (Hook) → veto nếu off-brand |
| **Creator** (quay video) | Section 5 (Script) + 6 (B-roll) + 9 (Checklist) |
| **Copywriter** (đăng caption) | Section 7 (Caption) + 8 (CTA) |
| **Anh** (post-mortem) | Section 10 — fill sau 7 ngày đăng |

→ Đưa file `angle-XX.md` cho team cầm đi quay là đủ, không cần brief miệng thêm.

---

## 6. Quy tắc vận hành

### 6.1 Không cố phân loại 100%

UNCLASSIFIED **không phải bug** — đó là feedback rằng config taxonomy chưa cover hết pattern dataset hiện tại.

- UNCLASSIFIED **<30%** → config đã tốt
- UNCLASSIFIED **30–40%** → còn tune được
- UNCLASSIFIED **>40%** → cần Bước 2.5 tune ngay

Comment off-topic / spam / khen chung chung **đáng để UNCLASSIFIED** — đừng ép vào nhóm.

### 6.2 UNCLASSIFIED là mỏ vàng

Mỗi lần thấy UNCLASSIFIED >30%, mở section đó trong `2-sắp-xếp.md`, đọc top 10 quote, hỏi:
- Pattern này lặp lại ≥3 lần không?
- Có đáng map vào 1 trong 9 nhóm hiện có không?
- Hay cần add nhóm thứ 10?

→ Đa phần là **bổ sung keyword** cho nhóm có sẵn, KHÔNG phải add nhóm mới.

### 6.3 Người chọn insight, AI không tự quyết toàn bộ

`brief.md` (output của `tim suggest`) là AI tự pick 10 angle — **chỉ dùng để tham khảo**.

Workflow chính là `bank → tick → select → production`, **anh quyết** chứ không AI.

Lý do: định vị thương hiệu + judgement chiến lược không có công thức, AI không biết được.

### 6.4 Production brief là bản nháp, vẫn cần người duyệt

Output Claude rất tốt nhưng KHÔNG production-ready 100%. Trước khi giao team quay:
- Đọc Big idea — có hợp định vị brand không?
- Đọc Hook — có cliché không (vd "bạn xứng đáng...", "tin vào chính mình")?
- Đọc Script 15-35s (insight) — có sâu thật không hay chỉ rephrase quote gốc?
- Edit caption + CTA cho khớp tone cá nhân anh

→ Coi `angle-XX.md` như **draft 1**, edit thành `angle-XX-final.md` trước khi quay.

### 6.5 Fallback template chỉ dùng khi không có Claude

Nếu API down / chưa setup key → vẫn chạy được với `--no-claude`. Nhưng:
- Output có marker `⚠️ FALLBACK BRIEF` rõ ràng
- Các section creative ghi `[FALLBACK]` → cần edit tay
- KHÔNG đưa fallback file cho team quay mà chưa edit

---

## 7. Checklist chạy thật (1 lần/tuần)

### Trước khi chạy

- [ ] `.env` còn API key hợp lệ (Apify + Anthropic chưa hết quota)
- [ ] Đã chọn 3–5 video TikTok cùng niche kinh doanh nữ (KOL hoặc viral video)
- [ ] URLs là TikTok video URL đầy đủ (không phải profile, không phải `vm.tiktok.com`)
- [ ] Có folder mới `output/kinh-doanh-27-45/<today>/` (hoặc dùng `tim init`)

### Bước 1 — Pipeline gốc

- [ ] Chạy `tim run --urls-file ... -o output/kinh-doanh-27-45/<today>` (hoặc dùng webapp)
- [ ] Verify `classified.json` đã tồn tại + có ≥50 comment
- [ ] Mở `report.md` xem distribution sơ bộ

### Bước 2 — Bank

- [ ] Chạy `tim bank -i .../classified.json --config niche_configs/kinh-doanh-27-45.json`
- [ ] Mở `2-sắp-xếp.md` — check UNCLASSIFIED bao nhiêu %
- [ ] Nếu >40% → tune config theo Bước 2.5 trong SOP, chạy lại

### Bước 3 — Tick

- [ ] Mở `3-lựa-chọn.md` trong VS Code
- [ ] Đọc top candidates, tick `[x]` vào 5–10 angle
- [ ] Mix nhóm vấn đề, đừng tick 10 cái cùng nhóm
- [ ] Save file

### Bước 4 — Select

- [ ] Chạy `tim select -i .../3-lựa-chọn.md`
- [ ] Verify `_master/content-pipeline.md` + `_master/selected_angles.json` đã tạo
- [ ] Verify số `Mới thêm` khớp số đã tick

### Bước 5 — Production

- [ ] Chạy `tim production -i .../selected_angles.json --config ...`
- [ ] (Tuỳ chọn) `--limit 1` test 1 angle trước nếu lần đầu chạy với prompt mới
- [ ] Verify `4-thực-thi/angle-XX-*.md` đã tạo đủ N file
- [ ] Mở 1 file, kiểm tra chất lượng Big idea + Script

### Sau khi quay đăng (1 tuần sau)

- [ ] Mở `4-thực-thi/angle-XX.md` của video đã quay
- [ ] Fill section 10 (Post-mortem): view, like, comment, save, bài học
- [ ] Update `_master/content-pipeline.md` đổi Status thành `done`
- [ ] Quan sát: angle nào viral → demand_score weights có cần tune không?

---

## 7B. Cách nạp comment thủ công từ Facebook / YouTube / nguồn khác

> **Khi nào dùng**: TikTok video ít comment, hoặc anh muốn research audience từ FB group / YouTube channel / fanpage / Zalo OA / Reddit / forum.
>
> **Nguyên tắc**: Core pipeline **không phụ thuộc TikTok**. Mọi nguồn data đều có thể chuẩn hoá về cùng 1 schema → chạy phân tích như bình thường.

### 7B.1 Quy trình tổng (3 bước)

```
File CSV/Excel comment   →   tim import-comments   →   raw_comments.json   →   pipeline cũ (classify → bank → ...)
                              ↑
                    KHÔNG phụ thuộc Apify / TikTok
```

### 7B.2 Chuẩn bị file CSV/Excel

**Cột bắt buộc** (1 trong 2):
- `comment` (ưu tiên nếu có cả 2)
- `text`

**Cột optional** (thiếu → default fill):
| Cột | Default | Ghi chú |
|---|---|---|
| `platform` | `manual` (hoặc giá trị từ flag `--source`) | Tên nguồn: `facebook`, `youtube`, `fb_group`, `zalo_oa`... |
| `source_url` | `""` | URL post / video gốc, để trace |
| `author` | `unknown` | Username người comment |
| `likes` | `0` | Số like |
| `replies` | `0` | Số reply |
| `created_at` | `""` | Ngày comment (free format, vd `2026-05-07`) |

**Format file**:
- ✅ `.csv` (UTF-8, kể cả UTF-8-BOM từ Excel Save-As)
- ✅ `.xlsx` (cần `pip install openpyxl` lần đầu)
- ❌ `.xls` (Excel cũ — convert sang `.xlsx` trước)

### 7B.3 Cách lấy comment từ Facebook / YouTube

**Phương pháp 1 — Copy-paste tay** (nhanh nhất, miễn phí):

1. Mở post FB / video YouTube có nhiều comment (≥30 cmt)
2. Scroll cho hiện hết comment (FB nhiều khi cần "Xem thêm bình luận")
3. Mở Excel / Google Sheets, tạo header: `comment,platform,source_url,author,likes,replies,created_at`
4. Copy-paste từng comment thủ công, hoặc:
   - **FB**: ctrl+A select hết comment area → paste vào Sheets → split column
   - **YouTube**: tương tự, hoặc dùng extension `Pocket Tube`
5. Save → File → Save As → `CSV UTF-8` (nếu lúc save có hỏi encoding chọn UTF-8)

**Phương pháp 2 — Browser extension** (semi-automated):
- FB: `Comment Picker for Facebook` (Chrome ext)
- YouTube: `YT Comment Sniper`, `vidIQ`
→ Export ra CSV → import vào tool

**Phương pháp 3 — API** (advanced, future work):
- FB Graph API (cần app review)
- YouTube Data API v3 (cần API key, free tier có quota)
→ Hiện tại MVP **chưa làm**, dùng manual import trước.

### 7B.4 Lệnh import

```powershell
# Basic (CSV với platform=facebook là override khi cột empty)
python -m tiktok_insight_miner import-comments `
  -i data/comments-fb.csv `
  --niche kinh-doanh-27-45 `
  --source facebook

# Excel input
python -m tiktok_insight_miner import-comments -i data/comments.xlsx --niche kinh-doanh-27-45

# Custom date (nếu chạy import data của 1 tuần trước)
python -m tiktok_insight_miner import-comments -i ... --niche ... --date 2026-05-01

# Custom output root
python -m tiktok_insight_miner import-comments -i ... --niche ... --output-root /path/to/output
```

**Output**: `output/<niche>/<date>__manual-import/raw_comments.json`

→ Folder có suffix `__manual-import` để **dễ phân biệt** với data scraped từ TikTok.

### 7B.5 Sau khi import: chạy pipeline như bình thường

```powershell
# Classify
python -m tiktok_insight_miner classify `
  -i output/kinh-doanh-27-45/2026-05-08__manual-import/raw_comments.json `
  -o output/kinh-doanh-27-45/2026-05-08__manual-import/classified.json

# Bank
python -m tiktok_insight_miner bank `
  -i output/kinh-doanh-27-45/2026-05-08__manual-import/classified.json `
  --config niche_configs/kinh-doanh-27-45.json

# ... tick → select → production (giống Bước 4-5 ở mục 4)
```

→ Pipeline KHÔNG biết là manual import, ăn ngon như TikTok scraped data.

### 7B.6 Sample CSV template

File mẫu sẵn có: [data/sample-comments.csv](../data/sample-comments.csv) — copy + edit thẳng.

### 7B.7 Lưu ý quan trọng

| Vấn đề | Xử lý |
|---|---|
| **Comment trống** (chỉ space, hoặc <5 ký tự) | Tự động skip, có log |
| **Tiếng Việt mojibake** (Excel save UTF-8) | Save lại với "CSV UTF-8" thay vì "CSV (Comma delimited)" |
| **Duplicate comment** (paste nhầm 2 lần) | Hiện chưa auto-dedupe — anh tự xoá trong Excel trước khi import |
| **Mix nhiều nguồn vào 1 file** | OK, miễn cột `platform` ghi đúng nguồn từng dòng |
| **Số quá lớn ở cột likes/replies** | Tự convert int, fallback 0 nếu lỗi parse |

### 7B.8 Use case thực tế

**Use case 1**: Niche TikTok ít data → bổ sung từ FB group
- Scrape TikTok niche kinh doanh nữ → 50 comment (ít)
- Vào FB group "Mẹ bỉm khởi nghiệp" → copy 100 comment hot post → CSV
- Import → merge với TikTok run → bank → có 150 cmt phong phú hơn

**Use case 2**: Audience không xài TikTok mạnh
- Niche "đầu tư chứng khoán nam 30+" → audience xài YouTube nhiều hơn TikTok
- Không scrape TikTok → chỉ import từ comment YouTube → vẫn build insight được

**Use case 3**: Test config nhanh
- Trước khi tốn $0.20 scrape TikTok → tạo 20 comment giả định trong CSV
- Import → bank → check taxonomy đã hợp lý chưa
- Sau đó mới scrape thật

---

## 7B-bis. Pipeline mở rộng — `select` → `calendar` → `production`

> **Bối cảnh**: Sau khi tick `[x]` insight + chạy `tim select` → có `selected_angles.json`. Có 2 đường đi tiếp:

```
                 ┌─────────────────────────────────────────────┐
                 │           selected_angles.json              │
                 └────────────────┬────────────────────────────┘
                                  │
                ┌─────────────────┴─────────────────┐
                ▼                                   ▼
   tim production --limit N         tim calendar --strategy ...
   (1 angle → 1 brief đầy đủ)       (N angle → 30/60 ngày outline)
                │                                   │
                ▼                                   ▼
    4-thực-thi/angle-XX.md           content-calendar-XX-days.{md,json}
    (cho team quay video                (cho anh duyệt strategic
     1 angle cụ thể)                     30/60/90 ngày)
```

→ **2 đường này KHÔNG xung đột** — dùng song song:
- `production` cho **1 angle quay ngay**
- `calendar` cho **chiến lược nội dung dài hạn**

### 7B-bis.1 Khi nào chạy `tim calendar`?

| Tình huống | Recommend |
|---|---|
| Mới tick xong 5-10 insight, chưa quay gì | ✅ Chạy `calendar` trước → có roadmap 30 ngày → biết quay theo thứ tự nào |
| Đã quay 1-2 angle test, muốn scale | ✅ Chạy `calendar` để build calendar tháng |
| Brand mới onboard, chưa có dữ liệu | ❌ Chưa chạy được — collect insight + select trước |
| Đã có 30 angle posted, sang tháng 2 | ✅ Chạy lại với strategy mới (vd `chi-hien-30-day-v2.json`) |

### 7B-bis.2 Lệnh

```powershell
# Default — input là selected_angles.json
python -m tiktok_insight_miner calendar `
  -i output/<niche>/_master/selected_angles.json `
  --strategy strategy_configs/<brand>-30-day-v1.json `
  -o output/<niche>/_master/

# Fallback — pool nhỏ, dùng classified.json để có nhiều insight hơn
python -m tiktok_insight_miner calendar `
  -i output/<niche>/<date>/classified.json `
  --strategy strategy_configs/<brand>-30-day-v1.json `
  -o output/<niche>/_master/
```

→ Module **auto-detect** input format (selected_angles vs classified). Tự fallback insight_bank logic nếu cần.

### 7B-bis.3 Output

| File | Vai trò |
|---|---|
| `content-calendar-30-days-<brand>-v1.md` | Human-readable — anh đọc + duyệt + edit tay nếu cần |
| `content-calendar-30-days-<brand>-v1.json` | Machine-readable — `production.py` downstream đọc trực tiếp (future) |
| `content-calendar-...-MANUAL-BACKUP.md` | Auto-backup file .md cũ (nếu có) trước khi overwrite |

### 7B-bis.4 Strategy config — tách riêng theo brand

| Layer | Path | Vai trò |
|---|---|---|
| Niche | `niche_configs/<niche>.json` | Phân loại vấn đề (audience pain) |
| Brand | `profiles/<brand>/` | Voice (cách nói) |
| Methods | `docs/writing_methods/` | Kỹ thuật viết (HOW) |
| **Strategy** ⭐ | `strategy_configs/<brand>-<period>-v<N>.json` | **Chiến lược phân bổ nội dung theo thời gian** (CHIẾN LƯỢC) |

→ Đổi brand = thêm `strategy_configs/<brand-y>-30-day-v1.json` + `profiles/<brand-y>/`. **0 lines code thay đổi**.

### 7B-bis.5 Pool nhỏ → diversity thấp (cảnh báo)

Nếu pool insight (selected_angles.json) chỉ có 6 angles → calendar 30 ngày sẽ **recycle 5x mỗi insight**. Module sẽ in cảnh báo:
```
⚠️ Pool nhỏ — avg reuse: 5.0x per insight
```

**2 cách fix**:
1. Tick thêm angles trong các `3-lựa-chọn.md` (round 1, 2, 3) → `tim select` lại → pool tăng
2. Pass `classified.json` thay vì `selected_angles.json` qua `-i` → pool full ~70-100 insights

---

## 7C. Voice profile và write rules dùng khi nào

> **Bối cảnh**: Tool có 3 LỚP tài liệu về cách viết. Mỗi lớp dùng cho mục đích khác nhau, KHÔNG trộn vào nhau.

### 7C.1 Kiến trúc 3 lớp

```
┌─────────────────────────────────────────────────────────────┐
│  LỚP 1 (CORE — kỹ thuật)                                    │
│  docs/SOP_BUILD_INSIGHT_V1.md                               │
│  → Quy trình build insight system, KHÔNG mang giọng riêng    │
│  → Dùng cho mọi ngành/mọi brand                             │
├─────────────────────────────────────────────────────────────┤
│  LỚP 2 (BASE — luật viết chung)                             │
│  docs/WRITE_RULES_BASE.md                                   │
│  docs/VOICE_PROFILE_TEMPLATE.md                             │
│  → Luật viết chung mọi output content                       │
│  → Template để mỗi brand điền voice riêng                   │
├─────────────────────────────────────────────────────────────┤
│  LỚP 3 (BRAND — voice cá nhân)                              │
│  profiles/<brand-slug>/                                      │
│    ├── about.md         (story + background)                │
│    ├── voice_profile.md (giọng cụ thể, từ vựng riêng)       │
│    └── write_rules.md   (extends LỚP 2)                     │
│  → Riêng từng người/thương hiệu                             │
└─────────────────────────────────────────────────────────────┘
```

→ **Quy tắc số 1**: KHÔNG nhồi giọng brand cụ thể vào LỚP 1 hoặc LỚP 2.

### 7C.2 Khi nào đọc cái gì?

| Tình huống | Đọc file nào |
|---|---|
| Onboard nhân viên content mới | `docs/MVP_WORKFLOW.md` (file này) → `docs/WRITE_RULES_BASE.md` → `profiles/<brand>/` |
| Build niche mới | `docs/SOP_BUILD_INSIGHT_V1.md` (LỚP 1) |
| Viết content cho brand cụ thể (vd chị Hiền) | `profiles/chi-hien/{about,voice_profile,write_rules}.md` (LỚP 3) — đọc cả 3 |
| Edit tay caption / brief trước khi đăng | LỚP 2 (`WRITE_RULES_BASE`) + LỚP 3 (brand-specific) |
| Onboard brand mới | Copy `docs/VOICE_PROFILE_TEMPLATE.md` → `profiles/<brand-slug>/voice_profile.md` → fill |

### 7C.3 Khi nào file nào được tự động dùng?

**`production.py` (tự động)**:
- Hiện tại: chỉ inject **niche_config persona** vào system prompt
- **Tương lai (chưa làm)**: nếu có flag `--profile chi-hien`, sẽ inject thêm:
  - `profiles/chi-hien/voice_profile.md`
  - `profiles/chi-hien/write_rules.md`
  - `profiles/chi-hien/about.md`
  → Brief sinh ra sẽ chuẩn giọng chị Hiền, không cần edit nhiều

**`production.py` (manual fallback hiện tại)**:
- Anh / nhân viên đọc các file profile TRƯỚC khi edit brief
- Edit Big idea / Hook / Caption cho khớp giọng

### 7C.4 Cách thêm brand mới (vd brand-Y)

```powershell
# Bước 1: Tạo folder
mkdir profiles\brand-y

# Bước 2: Copy template
copy docs\VOICE_PROFILE_TEMPLATE.md profiles\brand-y\voice_profile.md

# Bước 3: Tạo write_rules.md (extends WRITE_RULES_BASE)
# Bắt đầu file với:
#   <!-- EXTENDS: docs/WRITE_RULES_BASE.md -->
#   # WRITE RULES — Brand Y
#   [chỉ ghi delta của brand Y, không lặp base]

# Bước 4: Viết about.md
# Story + background do brand cung cấp

# DONE — KHÔNG sửa gì ở LỚP 1 hoặc LỚP 2
```

→ **Đổi brand = thêm folder, không sửa core**.

### 7C.5 Lưu ý quan trọng

- **3 file profile của 1 brand được đọc CÙNG NHAU** trước mỗi tác vụ viết (như chị Hiền yêu cầu trong write_rules)
- **Voice profile KHÔNG share giữa 2 brand** — mỗi người có voice riêng
- **WRITE_RULES_BASE stay generic** — chỉ update khi có insight về luật viết phổ quát, KHÔNG nhồi từ ngữ riêng 1 brand
- File `profiles/<brand>/` có thể anh muốn cho vào `.gitignore` nếu chứa info confidential — anh quyết

---

## 7D. Khi nào dùng Writing Method Library

> **Library**: `docs/writing_methods/` — kho **kỹ thuật viết** (hook / story / video format / persuasion / editing).
>
> **Quan hệ với 3 lớp đã có**: Library là **lớp biên tập** — đứng SAU 3 lớp Generic / Base / Brand-specific.

### 7D.1 Order of operations (BẮT BUỘC)

```
[1] Insight thật từ pipeline (classify → bank → select)
[2] 🧭 SB7 Message Check — fill 10 ô trước khi viết (docs/writing_methods/SB7_message_check.md)
[3] Đọc 3 file brand: profiles/<brand>/{about, voice_profile, write_rules}
[4] Đọc base rules: docs/WRITE_RULES_BASE.md
        ↓
[5] Mở Library: docs/writing_methods/method_picker.md
[6] Pick 2-4 method file phù hợp output type
[7] 🇻🇳 Vietnamese Language Layer — pick 1-2 biện pháp tu từ + tone
[8] Viết draft, áp method
[9] Chạy editing_checklist.md trước khi xuất bản
        ↓
[10] Brand owner duyệt → đăng
```

→ KHÔNG skip 1-4 và đi thẳng tới 5. Library mà thiếu insight + SB7 + voice = template generic.

→ **SB7 ở Bước 2** là kim chỉ nam thông điệp. KHÔNG phải style viết. KHÔNG thay thế voice / language layer. Mỗi bài fill 10 ô trước khi draft. Skip được khi: caption <30 chữ / reply DM / nháp test format.

→ **Mỗi bài chọn 1 message framework chính + 1-2 phụ** (hiện chỉ có SB7, tương lai sẽ thêm). KHÔNG trộn 4-5 framework vào 1 bài.

### 7D.2 Bảng tra nhanh — Khi viết loại nào, mở file nào?

| Output | Methods PICK | Note |
|---|---|---|
| **Reel 60s** | `short_video_methods.md` + `hook_methods.md` + `storytelling_methods.md` + `persuasion_methods.md` | 4 file — đủ cho format chặt |
| **FB post 300-600 chữ** | `hook_methods.md` + `storytelling_methods.md` + `persuasion_methods.md` | 3 file |
| **Caption ngắn (<100 chữ)** | `hook_methods.md` + 1 CTA từ `persuasion_methods.md` | 2 file |
| **Bài kể chuyện dài** | `storytelling_methods.md` (đủ 7 thành phần) + `hook_methods.md` | 2 file |
| **Bài giáo dục** | `hook_methods.md` (counter-belief) + `persuasion_methods.md` (belief shift) | 2 file |
| **Lead magnet CTA** | `persuasion_methods.md` (comment keyword + desire amplification) | 1 file |

→ Chi tiết xem `docs/writing_methods/method_picker.md`.

### 7D.3 Khi viết cho chị Hiền — quy trình đặc biệt

Chị Hiền đã có **3 file profile riêng**. Khi pick method từ Library cho chị:

```
[1] Đọc profiles/chi-hien/voice_profile.md
        → đặc biệt mục Q11 (pattern mở bài), Q12 (structure), Q13 (CTA style)
[2] Đọc profiles/chi-hien/write_rules.md
        → đặc biệt section "Pattern mở bài" (4 lựa chọn theo Archetype)
[3] Cross-check Library:
        → Method nào trong Library MATCH với pattern brand → pick
        → Method nào CONFLICT với brand → SKIP (brand voice thắng)
[4] Apply method theo brand convention (KHÔNG generic)
[5] Chạy "The test" 6 điểm trong profiles/chi-hien/write_rules.md
[6] Chạy editing_checklist.md trong Library
[7] Chị Hiền / anh duyệt → quay
```

→ Brand profile là **nguồn cuối**. Library là **fallback** khi brand không cover.

### 7D.4 Khi NÀO KHÔNG dùng Library?

- ❌ Khi brand profile đã có method tương đương → dùng brand version
- ❌ Khi viết cho client KHÔNG có voice profile → tạo voice profile trước (qua `VOICE_PROFILE_TEMPLATE.md`)
- ❌ Khi muốn "quick draft" mà skip insight thật → re-do pipeline trước

### 7D.5 Khi NÊN dùng Library?

- ✅ Khi brand mới chưa có nhiều convention → Library cho framework cơ bản
- ✅ Khi nhân viên content mới onboard → đọc Library + WRITE_RULES_BASE để học kỹ thuật chung
- ✅ Khi brand profile yêu cầu (vd "dùng pattern Hard Truth") → Library giải thích chi tiết hơn brand profile
- ✅ Khi cần quick refresher trước khi viết bài

### 7D.5b 🇻🇳 Vietnamese Language Layer — khi viết draft

> Sau khi pick hook + storytelling + persuasion method, **trước khi viết draft**, mở `docs/writing_methods/language_bank/` để chọn câu chữ.

**Quy trình ngắn**:

```
[1] Method Picker đã chọn hook/story/persuasion
        ↓
[2] Mở language_bank/ — pick 1-2 cái phù hợp insight đang viết:
        • 1-2 biện pháp tu từ (vietnamese_rhetoric.md)
        • Từ loại nổi bật cần (đặc biệt tình thái/trợ/phó từ — vietnamese_word_classes.md)
        • 1 nhóm từ biểu đạt (láy / thành ngữ / trái nghĩa — expressive_word_groups.md)
        • Tone/register (tone_and_register.md) — phải khớp voice profile brand
        ↓
[3] Viết draft áp dụng các pick trên
        ↓
[4] editing_checklist.md — đặc biệt Nhóm 7 (6 check VN mới)
```

**Khi NÀO dùng Language Bank**:
- ✅ Bài có đoạn story / cảm xúc → cần biện pháp tu từ + giác quan
- ✅ CTA / kết bài → cần tình thái từ làm mềm
- ✅ Hook → cần đảo ngữ / tương phản / câu hỏi tu từ

**Khi NÀO không cần**:
- ❌ Caption ngắn <30 chữ → bỏ qua, tone đã đủ
- ❌ Bài data/báo cáo → tone báo chí thuần, không nhồi tu từ
- ❌ Tin nhắn nội bộ / DM → không audit câu chữ

→ Language Bank là **menu**, không phải **luật**. Pick 1-2 cái fit, không nhồi.

---

### 7D.6 Lifecycle — khi nào update Library

Library **stable**, KHÔNG update thường xuyên. Update chỉ khi:
- Học được method mới chưa cover (thêm vào file phù hợp qua quy trình ingestion ở `README.md` mục 6)
- Phát hiện anti-pattern mới → add vào `rejected_methods.md`
- Editing checklist phát hiện gap pattern → update `editing_checklist.md`

→ KHÔNG nhồi mọi bài học từ Notion vào Library — chỉ những gì đã LỌC qua 3 câu hỏi (xem README mục 6.1).

---

## 8. Tài liệu liên quan

- [SOP_BUILD_INSIGHT_DRAFT.md](SOP_BUILD_INSIGHT_DRAFT.md) — SOP draft chi tiết quy trình kỹ thuật từng bước
- [SOP_BUILD_INSIGHT_V1.md](SOP_BUILD_INSIGHT_V1.md) — SOP tổng quát để build cho ngành khác
- [../niche_configs/kinh-doanh-27-45.json](../niche_configs/kinh-doanh-27-45.json) — Config v1.1 cho niche test
- [../README.md](../README.md) — Quick start cho người mới
- [../USAGE.md](../USAGE.md) — Reference command lines

---

**Updated**: 2026-05-10 · MVP v0.4 (đủ 4 bước Liệt kê → Sắp xếp → Lựa chọn → Thực thi) + 🧭 SB7 Message Check + 🇻🇳 Vietnamese Language Layer
