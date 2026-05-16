# SOP — Clone Niche Mới (Playbook)

> **Phiên bản**: v1 (2026-05-16)
> **Mục đích**: playbook step-by-step để clone hệ thống miner cho 1 ngành/niche mới — từ 0 đến file handoff sẵn sàng cho client (CoWork hoặc khác)
> **Đối tượng**: anh Tuấn + bất kỳ ai onboard tool này cho project mới
> **Tinh thần**: làm theo từ trên xuống, không cần đọc lý thuyết. Lý thuyết ở [SOP_BUILD_INSIGHT_V1.md](SOP_BUILD_INSIGHT_V1.md).

---

## 0. Khi nào dùng SOP này

✅ **Dùng khi**:
- Muốn build kho insight cho 1 niche mới (vd skincare 30+, mẹ bỉm, đầu tư BĐS, sexual wellness...)
- Đã có niche reference (`kinh-doanh-27-45`) chạy ổn → clone pattern
- Muốn serve 1 client mới (brand khác chị Hiền)

❌ **KHÔNG dùng khi**:
- Chỉ chạy lại niche đã có → dùng [MVP_WORKFLOW.md](MVP_WORKFLOW.md) thay
- Muốn viết bài → việc CoWork, không phải miner

---

## 1. Pre-requisites

| Thứ | Có sẵn? | Ghi chú |
|---|---|---|
| Tool đã install (`pip install -e .`) | ✅ phải có | Nếu chưa, xem [README.md](../README.md) |
| `.env` có `APIFY_TOKEN` + `ANTHROPIC_API_KEY` | ✅ phải có | Apify để scrape, Claude để classify |
| Niche reference `kinh-doanh-27-45` chạy ổn | ✅ phải có | Dùng làm template clone |
| Hiểu pipeline 4 bước (Liệt kê → Sắp xếp → Lựa chọn → Handoff) | ✅ phải có | Xem [SOP_BUILD_INSIGHT_V1.md](SOP_BUILD_INSIGHT_V1.md) mục 2 |

---

## 2. Estimated time + cost

| Pha | Effort | Cost |
|---|---|---|
| Phase 0-1 (setup config) | 1-2 giờ (manual brainstorm) | $0 |
| Phase 2 (scrape + classify) | 5-15 phút wait | ~$0.05-0.30 (Apify + Claude) |
| Phase 3 (tune taxonomy nếu cần) | 30-60 phút | $0 (re-run bank không tốn API) |
| Phase 4 (tick + select + export) | 15-30 phút | $0 |
| **Tổng lần đầu** | **~3-4 giờ** | **<$0.50** |
| Lần thứ N (sau khi đã quen) | 30-60 phút | <$0.30 |

---

## Phase 0 — Quyết niche slug + persona (1 giờ, manual)

### 0.1 Đặt niche slug

Format **kebab-case**, mô tả audience cụ thể:

```
skincare-tuoi-25-40       ← niche skincare cho phụ nữ 25-40
me-be-0-3-tuoi            ← mẹ bỉm con 0-3 tuổi
bds-can-ho-tphcm          ← BĐS căn hộ TPHCM
dau-tu-chung-khoan-nam    ← nam đầu tư chứng khoán
```

Quy tắc:
- a-z, 0-9, dấu `-` (không space, không Tiếng Việt có dấu)
- Cụ thể: vừa **demographic** (tuổi, giới) vừa **vertical** (skincare, BĐS...)
- Tránh quá rộng (`phu-nu` ❌) hoặc quá hẹp (`me-bim-ha-noi-con-sinh-non` ❌)

### 0.2 Viết persona (1-2 đoạn)

Trả lời 5 câu hỏi:
1. **Demographic**: tuổi + giới + thu nhập + life stage
2. **Business/job stage**: làm gì, đã bao lâu
3. **Media behavior**: dùng platform nào, follow ai, xem mấy giờ/ngày
4. **Core tensions** (3-5 câu): mâu thuẫn nội tâm họ đang sống
5. **Goals**: họ muốn gì trong 6-12 tháng tới

Ví dụ (skincare 25-40):
> Phụ nữ 25-40, sống TP.HCM/HN, thu nhập 20-100tr/tháng. Đã có 1-2 con. Da dầu mụn từ tuổi dậy thì. Đã thử 5-10 brand skincare, đa phần chỉ giúp tạm thời. Tự research qua TikTok 1-2h/ngày, follow KOL beauty + bác sĩ da liễu. Sẵn sàng chi 1-3tr/tháng nếu thấy KOL chứng minh được sản phẩm work. Sợ retinoid (đỏ mặt), thích skincare thiên nhiên + minimal step.
>
> Core tensions: vừa muốn nhanh vừa sợ rủi ro / vừa muốn rẻ vừa muốn hiệu quả / vừa muốn đẹp tự nhiên vừa muốn rõ rệt.

### 0.3 Brainstorm 9-12 nhóm vấn đề

Hỏi: persona này thức dậy 6h sáng, **5-9 thứ đầu tiên họ lo** là gì?

Mỗi nỗi lo = 1 nhóm. Quy tắc:
- 9-12 nhóm là sweet spot. <7 quá rộng, >14 fragment
- Mỗi nhóm CODE format `UPPER_CASE_UNDERSCORE` (vd `MUN_DA_DAU`)
- Mỗi nhóm `name_vi` 2-4 từ rõ ràng

Ví dụ skincare:
```
MUN_DA_DAU           — Mụn & da dầu
LAO_HOA_30_PLUS      — Lão hóa sau 30
DA_NHAY_CAM          — Da nhạy cảm
SAU_SINH_HORMONE     — Sau sinh, hormone
MAKEUP_DAILY         — Trang điểm hằng ngày
BUDGET_VS_LUXURY     — Drugstore vs cao cấp
DIY_TU_NHIEN         — Thiên nhiên / DIY
THIET_BI_HOME        — Máy rửa mặt / LED
THAM_MY_VIEN         — Laser / filler / peel
```

→ Nếu không brainstorm được 9 nhóm trong 30 phút → niche chưa đủ hiểu, không nên chạy.

---

## Phase 1 — Copy + customize niche_config.json (30-60 phút)

### 1.1 Copy template

```powershell
# Từ folder D:\Projects\tiktok-insight-miner
copy niche_configs\kinh-doanh-27-45.json niche_configs\<niche-slug>.json
```

→ Ví dụ: `copy niche_configs\kinh-doanh-27-45.json niche_configs\skincare-tuoi-25-40.json`

### 1.2 Edit 6 chỗ trong file mới

| Chỗ cần edit | Edit gì |
|---|---|
| `niche_slug`, `niche_name` | Slug + tên đầy đủ Tiếng Việt |
| `persona` | Fill từ Phase 0.2 (summary, age_range, life_stage, business_stage, media_behavior, core_tensions) |
| `positioning` | for_whom, promise, tone, anti_pattern |
| `main_problems[]` | **REPLACE toàn bộ 9 nhóm cũ** bằng 9-12 nhóm mới từ Phase 0.3. Mỗi nhóm có 8 field: code, name_vi, freedom_layer, freedom_layer_secondary, suggested_mode, combo_visual_hint, description, keywords[], sub_problems[], common_emotions[], hidden_desires[], content_angles[] |
| `scoring_rules.problem_priority_bonus` | Map keys = code mới. Top 3 nhóm hot = +5, còn lại +2 đến +4 |
| `evolution_notes.version_log` | Reset, ghi `"v1.0 (<today>)": "Init từ template kinh-doanh-27-45"` |

### 1.3 Mapping `freedom_layer` (nếu client là CoWork chị Hiền)

Mỗi nhóm thêm 4 field:
- `freedom_layer`: 1 (Đời sống) / 2 (Công việc) / 3 (Tâm trí) / 4 (Dòng tiền)
- `freedom_layer_secondary`: lớp phụ hoặc `null`
- `suggested_mode`: `"A"` (Framework) / `"B"` (Storytelling)
- `combo_visual_hint`: 1 / 2 / 3

→ Chi tiết logic mapping: xem [MAPPING_FREEDOM_LAYER.md](MAPPING_FREEDOM_LAYER.md)

→ Nếu client KHÁC chị Hiền (brand khác / agency khác) → có thể skip 4 field này hoặc map theo schema riêng của client.

### 1.4 Validate JSON

```powershell
python -c "import json; json.load(open('niche_configs/<niche-slug>.json', encoding='utf-8')); print('JSON valid')"
```

→ Nếu lỗi → fix syntax (thiếu dấu phẩy, sai bracket...) rồi validate lại.

---

## Phase 2 — Scrape + classify (15 phút + 5 phút wait)

### 2.1 Init folder

```powershell
python -m tiktok_insight_miner init <niche-slug>
```

→ Tạo `output/<niche-slug>/<today>/{urls.txt, notes.md}`.

### 2.2 Paste URLs hoặc import CSV

**Cách A — TikTok URL** (nếu có viral video):
- Edit `output/<niche-slug>/<today>/urls.txt`
- Paste 3-5 TikTok video URL cùng niche (mix viral + medium + niche-specific)

**Cách B — Manual import** (nếu data ở FB/YouTube/Notion):
- Tạo file CSV với cột bắt buộc: `comment` hoặc `text`
- Cột optional: `platform`, `author`, `likes`, `replies`, `created_at`
- Chạy:
  ```powershell
  python -m tiktok_insight_miner import-comments `
    -i path\to\comments.csv `
    --niche <niche-slug> `
    --source facebook
  ```

→ Chi tiết format CSV: xem [MVP_WORKFLOW.md](MVP_WORKFLOW.md) mục 7B.

### 2.3 Run pipeline

```powershell
# Cách A (TikTok scrape)
python -m tiktok_insight_miner run `
  --urls-file output\<niche-slug>\<today>\urls.txt `
  --max-comments 100 `
  -o output\<niche-slug>\<today>

# Cách B (sau khi import CSV — chỉ chạy classify)
python -m tiktok_insight_miner classify `
  -i output\<niche-slug>\<today>__manual-import\raw_comments.json `
  -o output\<niche-slug>\<today>__manual-import\classified.json
```

→ Expected: file `classified.json` có ≥50 comment (lý tưởng 80-150).

→ Nếu <50 → scrape thêm video hoặc import thêm CSV.

---

## Phase 3 — Bank + tune taxonomy (15-60 phút)

### 3.1 Build bank lần 1

```powershell
python -m tiktok_insight_miner bank `
  -i output\<niche-slug>\<today>\classified.json `
  --config niche_configs\<niche-slug>.json
```

→ 3 file output:
- `1-liệt-kê.csv` — mọi insight, sort theo demand
- `2-sắp-xếp.md` — bức tranh tổng quan
- `3-lựa-chọn.md` — top candidates (auto-promote score ≥20)

### 3.2 Check UNCLASSIFIED %

Mở `2-sắp-xếp.md`, scroll xuống section "⚠️ Unclassified".

| % UNCLASSIFIED | Hành động |
|---|---|
| **<30%** | Config tốt → đi tiếp Phase 4 |
| **30-50%** | Tune taxonomy (mục 3.3) |
| **>50%** | Taxonomy có vấn đề lớn — review lại 9 nhóm ở Phase 0.3 |

### 3.3 Tune taxonomy (nếu cần)

1. Đọc top 20 quote unclassified (sort theo demand_score desc)
2. Gom thành 3-5 pattern lặp lại
3. Với mỗi pattern, quyết:
   - Map vào 1 trong 9 nhóm hiện có → bổ sung keyword vào `keywords[]` của nhóm đó
   - Hoặc giữ UNCLASSIFIED (off-topic, spam, quá generic)
4. Edit `niche_configs/<niche-slug>.json` — append keywords
5. Re-run `tim bank` trên cùng `classified.json` (free, không tốn API)
6. So sánh: UNCLASSIFIED có giảm <30% không?
7. Update `evolution_notes.version_log` ghi rõ keyword nào thêm

→ Quy tắc tune chi tiết: [SOP_BUILD_INSIGHT_V1.md](SOP_BUILD_INSIGHT_V1.md) mục 7.

### 3.4 Khi nào DỪNG tune

- UNCLASSIFIED <30% và residual chủ yếu off-topic → STOP
- Pattern xuất hiện <2 lần → STOP (đợi run thêm 2-3 batch)
- 3 vòng tune vẫn không cải thiện → có thể thiếu nhóm, cân nhắc add nhóm thứ 10-12

---

## Phase 4 — Tick + select + export (15-30 phút)

### 4.1 Tick `[x]` trong `3-lựa-chọn.md`

Mở file trong VS Code, đọc top 30 candidates, tick `[x]` vào 5-10 angle muốn dùng tuần này.

Quy tắc tick:
- ✅ Mix nhóm vấn đề (đừng tick 10 cái cùng 1 nhóm)
- ✅ Ưu tiên quote có cảm xúc mạnh + gần offer
- ❌ KHÔNG tick chỉ vì score cao nếu off-brand

### 4.2 Select

```powershell
python -m tiktok_insight_miner select `
  -i output\<niche-slug>\<today>\3-lựa-chọn.md
```

→ Tạo 2 file trong `output/<niche-slug>/_master/`:
- `content-pipeline.md` — markdown table track status
- `selected_angles.json` — JSON cho stage handoff

### 4.3 Export handoff + snapshot lên Drive

```powershell
python -m tiktok_insight_miner export-for-cowork `
  -i output\<niche-slug>\_master\selected_angles.json `
  --config niche_configs\<niche-slug>.json
```

→ Tạo 2 file:
1. `output/<niche-slug>/_master/insights-pack-for-cowork.md` — **source of truth ở miner**
2. `G:\My Drive\tiktok-miner-shared\insights-packs\<niche-slug>\insights-pack_v<N>.md` — **snapshot lên Drive** (tự version v1, v2, v3...)

→ Drive Desktop sync sẽ tự đẩy lên cloud trong vài giây.

→ CoWork máy nào cũng pull được sau khi Drive sync xong (xem [SETUP_GDRIVE_WORKFLOW.md](SETUP_GDRIVE_WORKFLOW.md)).

**Yêu cầu**: env var `INSIGHTS_PACK_DRIVE_DIR` trong `.env` (setup 1 lần).

**Override path mỗi lần** (nếu muốn snapshot vào folder khác):
```powershell
python -m tiktok_insight_miner export-for-cowork `
  -i ... --config ... `
  --snapshot-to "G:\Path\Khac"
```

→ **Trách nhiệm miner DỪNG ở đây**.

---

## Phase 5 — Client pull (việc của client, không phải miner)

### 5.1 Nếu client là CoWork chị Hiền

- Mở session bên `D:\Nhi Hien CoWork`
- Trigger skill `pull-insights-from-miner` (hoặc nói Claude CoWork: *"lấy insight mới về"*)
- CoWork tự đọc file ở miner → save vào `WORK AREAS/Marketing/<project>/inputs/` với version `_v1`, `_v2`...
- CoWork tự viết bài theo flow 7 bước của CoWork

→ Chi tiết flow: [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) mục 10.

### 5.2 Nếu client là brand khác / agency

Cách 1 — Copy file thủ công:
- Copy `output/<niche-slug>/_master/insights-pack-for-cowork.md` sang folder client
- Client tự đọc + transform

Cách 2 — Share path:
- Cho client đường dẫn `D:\Projects\tiktok-insight-miner\output\<niche-slug>\_master\insights-pack-for-cowork.md`
- Client tự pull (cần access D: hoặc setup OneDrive sync)

Cách 3 — Build pull tool riêng cho client:
- Tùy stack của client

---

## Phase 6 — (Optional) Feedback loop

Sau khi client đăng bài ≥7 ngày, có thể feed comment audience phản hồi lại miner:

1. Lấy URL bài đã đăng (FB/IG/TikTok)
2. Scrape comment dưới bài đó
3. Chạy lại pipeline: `classify → bank → select → export-for-cowork`
4. Insight v2 chính xác hơn vì là **mining own audience**

→ Đây là vòng feedback giúp config v1 → v2 → v3 thông minh hơn theo thời gian.

---

## Common pitfalls + Fix

| Pitfall | Triệu chứng | Fix |
|---|---|---|
| Niche quá rộng | UNCLASSIFIED >60%, distribution lệch | Hẹp lại persona, chia 2 niche con (vd "skincare" → "skincare-acne-25-30" + "skincare-aging-35-45") |
| Niche quá hẹp | Scrape <30 comment, hết video viral | Mở rộng adjacent niche, hoặc dùng manual import từ FB group |
| Keyword quá broad | 1 nhóm chiếm 60%+, các nhóm khác trống | Bỏ keyword broad, giữ keyword 2-4 từ specific |
| Forgot `freedom_layer` field | Module export thiếu hint | Add 4 field vào niche_config (xem mục 1.3) hoặc skip mapping nếu không cần |
| JSON syntax error | `tim bank` fail với JSONDecodeError | Validate bằng `python -c "import json; json.load(open('...'))"` |
| Mojibake (Tiếng Việt lỗi) | Quote hiển thị `mu?n` thay vì `muốn` | Re-encode CSV: Excel → Save As → "CSV UTF-8" (không phải "CSV (Comma delimited)") |
| `tim production` deprecated | Script vẫn còn nhưng không dùng | Bỏ qua — scope v2 cuối là `tim export-for-cowork`, không phải production |

---

## 7 niche tiềm năng (đã list trong SOP V1 mục 10.2)

| Niche | Slug đề xuất | Đặc thù |
|---|---|---|
| Skincare 25-40 | `skincare-tuoi-25-40` | Nhiều thuật ngữ khoa học, keywords cần cover viết chuẩn + slang |
| Spa & thẩm mỹ viện | `spa-tham-my-vien` | Audience chia 2: practitioner vs customer |
| Mẹ & bé 0-3 tuổi | `me-be-0-3-tuoi` | Emotion strong (lo lắng + guilt) |
| Giáo dục online | `khoa-hoc-online` | Nhiều objection ("đắt", "không kịp học") |
| BĐS căn hộ | `bds-can-ho-tphcm` | Decision cycle dài, demand_score weights cần khác |
| Tài chính cá nhân | `tai-chinh-ca-nhan` | Trùng partial với kinh-doanh-27-45 ở nhóm TIEN_BAC |
| Đầu tư chứng khoán | `dau-tu-chung-khoan` | Audience 80% nam 25-45 — persona ngược niche nữ |

---

## Quick reference — CLI commands

```powershell
# Phase 0-1: setup (manual)
copy niche_configs\kinh-doanh-27-45.json niche_configs\<niche-slug>.json
# → edit file mới

# Phase 2: init + run
python -m tiktok_insight_miner init <niche-slug>
# → edit urls.txt
python -m tiktok_insight_miner run `
  --urls-file output\<niche-slug>\<today>\urls.txt `
  --max-comments 100 `
  -o output\<niche-slug>\<today>

# Phase 3: bank
python -m tiktok_insight_miner bank `
  -i output\<niche-slug>\<today>\classified.json `
  --config niche_configs\<niche-slug>.json

# Phase 4: tick → select → export
# (tick `[x]` trong 3-lựa-chọn.md tay)
python -m tiktok_insight_miner select -i output\<niche-slug>\<today>\3-lựa-chọn.md
python -m tiktok_insight_miner export-for-cowork `
  -i output\<niche-slug>\_master\selected_angles.json `
  --config niche_configs\<niche-slug>.json

# Phase 5: client pull (việc của client)
```

---

## Checklist clone niche mới (copy-paste mỗi lần)

```markdown
## Clone niche: <niche-slug>

### Phase 0 — Plan (1 giờ)
- [ ] Đặt niche_slug (kebab-case, unique trong niche_configs/)
- [ ] Viết persona (1-2 đoạn, có core_tensions)
- [ ] Brainstorm 9-12 main_problems (3 câu hỏi: 6h sáng họ lo gì?)

### Phase 1 — Config (30-60 phút)
- [ ] Copy template từ kinh-doanh-27-45.json
- [ ] Edit niche_slug + niche_name
- [ ] Edit persona + positioning
- [ ] REPLACE main_problems[] với 9-12 nhóm mới
- [ ] Cho mỗi nhóm: code, name_vi, freedom_layer (nếu CoWork), suggested_mode, combo_visual_hint, description, keywords (25-40), sub_problems (6-8), common_emotions (4-6), hidden_desires (4), content_angles (5)
- [ ] Set scoring_rules.problem_priority_bonus theo priority
- [ ] Reset evolution_notes.version_log = v1.0 (today)
- [ ] Validate JSON

### Phase 2 — Collect data (~15 phút + 5 phút API)
- [ ] tim init <slug>
- [ ] Paste 3-5 URLs vào urls.txt HOẶC import CSV
- [ ] tim run (hoặc tim classify nếu manual import)
- [ ] Verify classified.json có ≥50 comment

### Phase 3 — Bank + tune (~15-60 phút)
- [ ] tim bank
- [ ] Check UNCLASSIFIED % trong 2-sắp-xếp.md
- [ ] Nếu >30%: tune taxonomy, append keywords, re-run bank
- [ ] Update evolution_notes.version_log
- [ ] UNCLASSIFIED <30% và residual chủ yếu off-topic → STOP tune

### Phase 4 — Tick + handoff (~15-30 phút)
- [ ] Mở 3-lựa-chọn.md, tick [x] 5-10 angle (mix nhóm, gần offer)
- [ ] tim select
- [ ] Verify _master/selected_angles.json có đủ row
- [ ] tim export-for-cowork (auto snapshot lên Drive nếu có env var INSIGHTS_PACK_DRIVE_DIR)
- [ ] Verify _master/insights-pack-for-cowork.md đã tạo
- [ ] Verify snapshot Drive: G:\My Drive\tiktok-miner-shared\insights-packs\<slug>\insights-pack_v<N>.md
- [ ] Đợi 30s-2 phút cho Drive sync lên cloud

### Phase 5 — Client pull (việc của client)
- [ ] Báo client có batch mới (qua chat / email / Slack)
- [ ] Client tự pull file (skill bên CoWork hoặc copy thủ công)
- [ ] Trách nhiệm miner KẾT THÚC

### Phase 6 — (Optional) Feedback loop
- [ ] Sau client đăng ≥7 ngày: scrape comment bài đã đăng
- [ ] Chạy lại pipeline → insight v2 (mining own audience)
- [ ] Tune niche_config dựa trên patterns thực tế
```

---

## Tài liệu liên quan

- [SETUP_GDRIVE_WORKFLOW.md](SETUP_GDRIVE_WORKFLOW.md) — Setup Drive sync cho multi-machine
- [SOP_BUILD_INSIGHT_V1.md](SOP_BUILD_INSIGHT_V1.md) — Lý thuyết + 12 nguyên lý cốt lõi (V2 Pull model)
- [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) — Sơ đồ flow miner ↔ client
- [MAPPING_FREEDOM_LAYER.md](MAPPING_FREEDOM_LAYER.md) — Mapping cụ thể cho client CoWork chị Hiền (template)
- [MVP_WORKFLOW.md](MVP_WORKFLOW.md) — Hands-on guide cho niche đã có sẵn
- [SOP_BUILD_INSIGHT_DRAFT.md](SOP_BUILD_INSIGHT_DRAFT.md) — Chi tiết kỹ thuật từng module
- [../niche_configs/kinh-doanh-27-45.json](../niche_configs/kinh-doanh-27-45.json) — Template config (v1.4)
- [../README.md](../README.md) — Quick start
- [../USAGE.md](../USAGE.md) — Reference command lines
- [../.env.example](../.env.example) — Template config (có `INSIGHTS_PACK_DRIVE_DIR`)

---

**Updated**: 2026-05-16 · v1
**Tinh thần**: 1 niche mới = 1 lần follow SOP này từ Phase 0 → Phase 4. ~3-4 giờ first time, ~30-60 phút sau khi quen. Scale nhiều niche mà KHÔNG đụng code core.
