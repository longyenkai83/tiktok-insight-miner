# SOP — Build Insight System từ comment audience

> **Phiên bản**: v2 (2026-05-16) — refactor sang scope "kho insight + handoff" (pull model)
> **Đối tượng**: anh Tuấn + bất kỳ ai muốn build insight system cho 1 niche/ngành mới
> **Tinh thần**: SOP để **làm theo**, không phải để **đọc lý thuyết**
> **Scope mới (v2)**: miner chỉ làm Bước 1-2-3-4 (kho insight + handoff). Việc viết bài thuộc CoWork. Xem [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) v2 Pull model.

---

## 1. Mục tiêu SOP

Biến **comment thật của audience** trên 1 nền tảng (TikTok hiện tại — sau có thể YouTube, FB) thành **kho insight có taxonomy + scoring**, sẵn sàng để **client riêng** (CoWork brand chị Hiền, brand khác, agency...) **pull về** dùng cho:

| Use case (do CoWork làm, không phải miner) | CoWork dùng insight để... |
|---|---|
| Content marketing | Đẻ concept → viết bài (hook, script, caption, CTA) |
| Offer / sản phẩm | Map pain → promise → mechanism → objection |
| Sản phẩm số | Feature priority + use case + ngôn ngữ user |
| Sales / nurture | Objection map + FAQ + proof angle |

→ Một kho insight = **source of truth duy nhất**, dùng cho nhiều client. **Miner KHÔNG viết bài**.

---

## 2. Nguyên lý cốt lõi: **Liệt kê → Sắp xếp → Lựa chọn → Handoff**

### 2.1 Liệt kê — không bỏ sót tín hiệu thị trường

Lấy hết comment có insight ra khỏi data thô. Không filter sớm theo cảm tính.

- Output: `1-liệt-kê.csv` — mọi insight actionable, sort theo demand
- Mục tiêu: **không bỏ lỡ insight quan trọng** chỉ vì AI không thấy "interesting"

### 2.2 Sắp xếp — gom tín hiệu thành nhóm vấn đề

Group insight theo **9-12 nhóm vấn đề** đặc trưng ngành. Mỗi nhóm = 1 cụm pain/desire/question rõ.

- Output: `2-sắp-xếp.md` — distribution theo nhóm + Top cross-niche
- Mục tiêu: **thấy bức tranh tổng quan** thay vì 200 insight rời rạc

### 2.3 Lựa chọn — CON NGƯỜI chọn insight chiến lược

AI rank theo demand score. **Người duyệt và tick** insight nào đáng làm tuần này.

- Output: `3-lựa-chọn.md` (checkbox) → `_master/content-pipeline.md` + `selected_angles.json`
- Mục tiêu: **giữ judgement chiến lược** ở người, không để AI quyết định bản sắc thương hiệu

### 2.4 Handoff — export insight cho client (CoWork) pull về

Mỗi insight đã chọn → export thành 1 file pack format chuẩn cho CoWork đọc.

- Output: `_master/insights-pack-for-cowork.md` (source of truth, miner KHÔNG đẩy — CoWork tự pull)
- Mục tiêu: **CoWork tự lấy khi cần** → viết bài bên CoWork với voice + writing rules riêng
- Module: `tim export-for-cowork`
- Chi tiết handoff: [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md), mapping: [MAPPING_FREEDOM_LAYER.md](MAPPING_FREEDOM_LAYER.md)

---

## 2.5. Nguyên lý data-source-agnostic

> **Quy tắc**: Core pipeline KHÔNG phụ thuộc 1 nền tảng cụ thể. Mọi nguồn comment đều phải được **chuẩn hoá về cùng 1 schema** trước khi vào phân tích.

### 2.5.1 Vì sao quan trọng

- TikTok đôi khi **video ít comment** (<30) → không đủ data để rank
- Audience 1 số niche **không dùng TikTok mạnh** (vd: "đầu tư BĐS 50+", "ba mẹ tuổi U60") → thông tin sống ở FB / YouTube / Zalo
- Tool **bind chặt vào 1 nền tảng** = vứt khi nền tảng đó đổi API hoặc audience chuyển kênh
- Nguồn càng đa dạng, **insight càng giàu**, ít bias

### 2.5.2 Cách áp dụng

Mọi nguồn data trước khi vào pipeline **phải qua adapter chuẩn hoá** thành format `Comment` (Pydantic) chung:

```python
class Comment:
    id: str             # unique identifier
    text: str           # nội dung comment
    author: str         # username
    likes: int
    reply_count: int
    created_at: str
    video_url: str      # source_url cho post FB / video YouTube
    raw: dict           # giữ nguyên data thô của platform để debug
```

| Nguồn | Adapter |
|---|---|
| TikTok | `scraper.py` (Apify) — đã có |
| **CSV/Excel manual** | `comment_importer.py` — đã có (Bước 6A) |
| Facebook API | (chưa làm) — `fb_scraper.py` future |
| YouTube API | (chưa làm) — `youtube_scraper.py` future |
| Reddit / Forum | (chưa làm) — adapter riêng future |

→ Khi add nguồn mới, **chỉ viết adapter**, KHÔNG đụng pipeline core (`classify` / `bank` / `select` / `production`).

### 2.5.3 Trường `platform` trong `raw`

Vì `Comment` schema không có field `platform` riêng (giữ minimal), nguồn data được ghi vào `raw["platform"]`:
```json
{
  "id": "manual-0001",
  "text": "...",
  "raw": {
    "platform": "facebook",
    "imported_from": "manual_csv"
  }
}
```

→ Sau này nếu cần filter theo nguồn (vd: "chỉ xem insight từ FB"), đọc `raw["platform"]` được.

### 2.5.4 Workflow lai (mix nhiều nguồn)

```
TikTok scrape  ──► raw_comments_tiktok.json   ┐
                                              ├─► merge → classify → bank → ...
FB CSV import  ──► raw_comments_fb.json       ┤
                                              │
YouTube CSV    ──► raw_comments_yt.json       ┘
```

Hiện chưa có `tim merge` command — nhưng có thể manual:
- Concatenate JSON files với Python script
- Hoặc append CSV trước khi import

→ **Future work**: `tim merge -i a.json b.json -o merged.json`

### 2.5.5 Bài học

- **TikTok-only là bias**: insight bias theo audience TikTok (Gen Z mạnh, ít người >40 tuổi)
- **Manual import giải nút thắt API**: không cần access token / app review FB / YouTube quota
- **Schema chuẩn hoá là contract**: thay đổi `Comment` schema = phải update mọi adapter

---

## 2.6. Nguyên lý voice tách riêng theo brand

> ⚠️ **DEPRECATED v2 (2026-05-16)** — mục này KHÔNG CÒN trong scope miner. Voice của brand đã **moved sang CoWork** (`D:\Nhi Hien CoWork\ABOUT ME\voice-profile.md` + `writing-rules.md`). Folder `profiles/<brand>/` bên miner giữ làm history. Xem [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) cho scope mới.

> **Quy tắc**: Core insight system stay GENERIC. Voice + writing style của từng người/thương hiệu phải tách riêng vào `profiles/<brand>/`.

### 2.6.1 Vì sao quan trọng

- 1 tool có thể serve **nhiều brand khác nhau** (chị A, chị B, agency C...) — nếu voice nhồi vào core, đổi brand = sửa code
- Voice là **brand asset** — không leak được giữa các brand client
- SOP chung sống lâu (5+ năm), voice có thể đổi (rebrand 6-12 tháng)
- Người mới onboard cần đọc theo **layer**: kỹ thuật trước → voice sau

### 2.6.2 Cách tách

```
docs/                          ← LỚP CHUNG (mọi brand share)
├── SOP_BUILD_INSIGHT_V1.md   ← Quy trình kỹ thuật (file này)
├── WRITE_RULES_BASE.md        ← Luật viết phổ quát
└── VOICE_PROFILE_TEMPLATE.md  ← Template trống

profiles/                      ← LỚP RIÊNG (mỗi brand 1 folder)
├── chi-hien/
│   ├── about.md
│   ├── voice_profile.md       ← Theo schema TEMPLATE
│   └── write_rules.md         ← Extends WRITE_RULES_BASE
├── brand-x/                   ← Brand mới chỉ cần thêm folder
└── brand-y/
```

### 2.6.3 Quy tắc khi build / maintain

- **Core SOP (file này)** — KHÔNG được mention tên brand cụ thể, không quote câu signature của KOL
- **WRITE_RULES_BASE** — KHÔNG ghi từ vựng riêng 1 brand (vd KHÔNG nhồi banned word của chị Hiền vào base)
- **Profile riêng** — Tự do ghi giọng cụ thể, ví dụ thật, từ vựng riêng

### 2.6.4 Khi đổi/thêm brand

→ Chỉ làm 1 việc: tạo `profiles/<brand-moi>/` với 3 file (about, voice_profile, write_rules).

→ KHÔNG đụng `docs/`, KHÔNG đụng `src/`, KHÔNG đụng `niche_configs/`.

### 2.6.5 Trường hợp 1 brand serve nhiều niche

| Brand | Niche A | Niche B |
|---|---|---|
| `chi-hien` | `kinh-doanh-27-45` | `me-be-kinh-doanh` |
| `brand-x` | `skincare-tuoi-30` | — |

→ `profiles/<brand>/` × `niche_configs/<niche>/` = matrix.
→ `production.py` đọc CẢ 2: niche config (cho audience + persona) + brand profile (cho voice).

---

## 2.7. Nguyên lý "Writing Method là lớp biên tập"

> ⚠️ **DEPRECATED v2 (2026-05-16)** — Writing Method KHÔNG CÒN trong scope miner. Đã **moved sang CoWork** (`D:\Nhi Hien CoWork\RESOURCES\GUIDES\vietnamese-language-layer.md` + `reel-script-rules.md`). Folder `docs/writing_methods/` bên miner giữ làm history. Xem [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) cho scope mới.

> **Quy tắc**: Writing Method Library (`docs/writing_methods/`) là **lớp biên tập** — chỉ được dùng SAU KHI đã có **insight thật** + **voice profile phù hợp**.

### 2.7.1 Vì sao quan trọng

- Method **KHÔNG sinh insight**. Method chỉ giúp dệt insight đã có thành text chất lượng cao hơn.
- Method **KHÔNG thay voice**. Voice riêng của brand vẫn là nguồn cuối quyết định giọng.
- Method **KHÔNG thay judgement**. Anh / brand owner vẫn là người duyệt cuối cùng.

→ Nếu skip insight + voice và dùng method ngay → output thành **template content** không có hồn.

### 2.7.2 Order of operations (BẮT BUỘC)

```
[1] Insight thật       (từ pipeline classify → bank → select)
        ↓
[2] Voice profile      (đọc profiles/<brand>/{about, voice_profile, write_rules})
        ↓
[3] Big idea           (anh / brand owner duyệt)
        ↓
[4] Pick methods       (mở docs/writing_methods/method_picker.md → chọn 2-4 file)
        ↓
[5] Apply + Edit       (viết draft, áp method)
        ↓
[6] Editing checklist  (chạy docs/writing_methods/editing_checklist.md)
        ↓
[7] Brand owner duyệt  (anh / chị Hiền)
        ↓
[8] Xuất bản
```

→ Bước 4-6 là phạm vi của Library. Bước 1-3 + 7 vẫn là core SOP.

### 2.7.3 Writing Method Library KHÔNG được làm gì

- **KHÔNG nhồi voice 1 brand vào method file** — method file phải generic, dùng được cho mọi brand
- **KHÔNG copy nguyên block công thức có bản quyền** từ creator nào — chỉ trích nguyên tắc
- **KHÔNG cite tên creator cụ thể** trong method (anti-bias)
- **KHÔNG override voice profile** — nếu method conflict với brand voice, brand voice thắng

### 2.7.4 Cách add bài học mới vào Library

Library có quy trình ingestion riêng (xem `docs/writing_methods/README.md` mục 6):
- Đọc bài học gốc (vd từ Notion / sách / khoá)
- Tự hỏi 3 câu (nguyên tắc rõ? conflict không? duplicate không?)
- Trích nguyên tắc generic (KHÔNG cite creator)
- Map vào file đúng (hook / story / video / persuasion / rejected)
- Add với meta date + source category

→ Notion là **kho thô**. Library là **kho đã lọc**. KHÔNG paste thẳng.

---

## 2.8. Nguyên lý "Content Strategy Layer" — chiến lược tách khỏi giọng + taxonomy

> ⚠️ **DEPRECATED v2 (2026-05-16)** — Content Strategy + Calendar KHÔNG CÒN trong scope miner. Đã **moved sang CoWork** (thuộc project folder `WORK AREAS/Marketing/<project>/`). Folder `strategy_configs/` + module `content_calendar.py` bên miner giữ làm history. Xem [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) cho scope mới.

> **Quy tắc**: Chiến lược phân bổ nội dung theo thời gian (calendar 30/60/90 ngày) là **layer riêng biệt** — KHÔNG nhồi vào niche config, brand profile, hay code core.

### 2.8.1 Vì sao quan trọng

- Cùng 1 brand có thể có **nhiều strategy** (vd: 30 ngày chương 1, 60 ngày launch khoá học, 90 ngày Q4) → strategy cần version + reusable
- Cùng strategy có thể áp cho **brand khác** (vd template "30 ngày awareness build" dùng cho cả brand A và B nếu cùng archetype)
- Strategy thay đổi theo **giai đoạn business** (build awareness → consider → decide → retain), không cùng nhịp với brand voice (gần như stable) hay niche taxonomy (stable hơn)

→ Hardcode strategy vào niche config / brand profile / code = mỗi lần đổi chiến lược phải sửa nhiều layer.

### 2.8.2 Bốn layer tách biệt

```
LỚP 1 — niche_configs/<niche>.json       ← Taxonomy + scoring (audience pain)
LỚP 2 — profiles/<brand>/                 ← Voice riêng (cách nói)
LỚP 3 — docs/writing_methods/             ← Kỹ thuật viết (HOW)
LỚP 4 — strategy_configs/<strategy>.json  ← Chiến lược phân bổ nội dung (KHI NÀO + GÌ)
                                                     │
                                                     ▼
                              src/.../content_calendar.py (module generic)
                                                     │
                                                     ▼
                          Output: calendar.md + calendar.json
                                                     │
                                                     ▼
                          Input cho production.py (downstream)
```

### 2.8.3 Strategy config = contract giữa 4 yếu tố

```
strategy_config = (
    insight pool       ← từ classified/selected_angles
  + content_pillars    ← chiến lược chủ đề
  + awareness_stages   ← funnel position
  + format_ratio       ← phân bổ Reel/FB/Educational
  + measurement        ← KPI + feedback loop
  + constraints        ← banned groups, no FOMO, etc
)
```

→ Module `content_calendar.py` chỉ làm **mapping function** giữa các thành phần này → calendar entries. **KHÔNG sinh content** (production.py mới sinh).

### 2.8.4 Quy tắc khi viết / update strategy config

- ✅ Strategy = **kế hoạch**, không phải **content**. Chỉ chứa pillar/awareness/format ratio + constraints, KHÔNG chứa script bài.
- ✅ Update strategy = bump version (vd `v1` → `v2`), giữ history qua `evolution_notes`
- ✅ Constraint `banned_problem_groups` cho phép skip nhóm chưa muốn (vd HINH_ANH_PHONG_CACH cho 30 ngày đầu)
- ❌ KHÔNG nhồi voice signature của brand vào strategy (voice ở `profiles/<brand>/`)
- ❌ KHÔNG nhồi keyword taxonomy vào strategy (taxonomy ở `niche_configs/<niche>.json`)
- ❌ KHÔNG nhồi text generic templates vào strategy (templates ở module + docs/writing_methods/)

### 2.8.5 Module `content_calendar.py` constraints

- Module phải **GENERIC** — `grep "trịnh nhi hiền\|caregiver\|vipassana\|chi-hien"` trong file = **0 match**
- Module nhận paths qua strategy config, KHÔNG hardcode path
- Templates trong code dùng placeholder, fill từ data file
- Test reuse: cùng module + strategy khác → output calendar đúng brand mới

### 2.8.6 Khi nào KHÔNG dùng module — viết tay calendar?

- 1-time experiment cho campaign đặc biệt (vd Tết, Black Friday)
- Brand quá specific (vd phục vụ 1 client duy nhất, không scale)
- Calendar quá ngắn (≤7 ngày — overhead module > benefit)

→ Còn lại, **luôn ưu tiên module** vì re-runnable + audit-able.

### 2.8.7 Workflow chuẩn

```
classify → bank → tick → select → CALENDAR (chiến lược) → production (full text từng angle)
                                          ↑
                                          │
                                  strategy_configs/
```

→ `calendar` đứng giữa `select` và `production` — chiến lược trước, content sau.

---

## 3. Cấu trúc hệ thống tái sử dụng

Hệ thống có **6 layer**, tách rõ trách nhiệm để khi đổi niche **không phải sửa code**:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Core pipeline (CODE — không đổi giữa các niche)   │
│  scrape → classify → bank → select → production              │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Niche config (JSON — đổi mỗi niche)               │
│  niche_configs/<slug>.json                                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Taxonomy (trong niche config)                     │
│  9–12 main_problems với keywords + sub_problems              │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Scoring rules (trong niche config)                │
│  weights, bucket_bonus, problem_priority_bonus, thresholds   │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: Output contract (trong niche config)              │
│  paths + columns + template cho 4 file output                │
├─────────────────────────────────────────────────────────────┤
│  Layer 6: SOP vận hành (file này + MVP_WORKFLOW.md)         │
│  Quy trình + checklist + quy tắc                             │
└─────────────────────────────────────────────────────────────┘
```

→ Quy tắc số 1: **Đổi niche = đổi Layer 2-5 (JSON), KHÔNG đổi Layer 1 (code)**.

→ Code (Layer 1) chỉ refactor khi có insight mới về **kiến trúc**, KHÔNG vì có niche mới.

---

## 4. Quy trình build insight cho một niche mới (12 bước)

### Bước 1: Chọn niche

**Tiêu chí 1 niche tốt**:
- Có audience cụ thể (giới tính, tuổi, life stage, business stage)
- Có đủ video TikTok viral với comment dày (≥50 cmt/video)
- Có mục tiêu thương mại rõ (anh muốn bán gì cho nhóm này?)

**Tránh**:
- Niche quá rộng ("phụ nữ Việt Nam") — insight loãng, không actionable
- Niche quá hẹp ("mẹ bỉm sữa Hà Nội nuôi con sinh non") — không đủ data

**Format**: kebab-case slug. Ví dụ:
- `kinh-doanh-27-45` ✅
- `skincare-acne-tuoi-30` ✅
- `me-bim-sau-sinh-12-thang` ✅
- `phụ nữ` ❌ (có dấu)
- `business-women` ❌ (English chung chung)

### Bước 2: Định nghĩa persona

Viết **1-2 đoạn cụ thể** về persona, KHÔNG bullet point khô khan:

```
Phụ nữ 30-40, sống TP.HCM/HN, thu nhập 30-100tr/tháng, đã có 1-2 con,
da dầu mụn từ tuổi dậy thì. Đã thử 5-10 brand skincare, đa phần chỉ giúp tạm thời.
Tự research qua TikTok 1-2h/ngày, follow KOL beauty + bác sĩ da liễu.
Sẵn sàng chi 1-3tr/tháng nếu thấy KOL chứng minh được sản phẩm work với da họ.
Sợ retinoid (đỏ mặt), thích skincare thiên nhiên + minimal step.
```

**Phải có**:
- Tuổi + giới tính
- Life stage (đã/chưa có con, đã/chưa lấy chồng)
- Business / job stage
- Media behavior (xem gì, follow ai)
- **Core tensions** — 3-5 mâu thuẫn nội tâm (vd: "vừa muốn nhanh vừa sợ rủi ro")

### Bước 3: Tạo taxonomy vấn đề chính (9-12 nhóm)

**Quy tắc**:
- 9-12 nhóm là sweet spot. <7 → quá rộng, mất insight. >14 → fragment, khó group.
- Mỗi nhóm CODE format `UPPER_CASE_UNDERSCORE` (vd `KINH_DOANH_KIET_SUC`)
- Mỗi nhóm `name_vi` 2-4 từ tiếng Việt clear (vd "Kinh doanh kiệt sức")

**Cách brainstorm 9 nhóm**:
1. Tự hỏi: persona thức dậy 6h sáng, **5 thứ đầu tiên họ lo** là gì?
2. Mỗi nỗi lo = 1 nhóm tiềm năng
3. Nỗi lo nào cùng "rễ tâm lý" → merge thành 1 nhóm
4. Nỗi lo nào quá đặc thù 1 case → loại

**Ví dụ skincare**:
1. `MUN_DA_DAU` — mụn, da dầu, lỗ chân lông
2. `LAO_HOA_30_PLUS` — nếp nhăn, chảy xệ, đốm nâu
3. `DA_NHAY_CAM` — kích ứng, đỏ rát, eczema
4. `SAU_SINH_HORMONE` — nám, rụng tóc, da xám sau sinh
5. `MAKEUP_DAILY` — base trang điểm, no-makeup look
6. `BUDGET_VS_LUXURY` — drugstore vs cao cấp, value
7. `DIY_TU_NHIEN` — thiên nhiên, organic, DIY mask
8. `THIET_BI_HOME` — máy rửa mặt, LED, microcurrent
9. `THAM_MY_VIEN` — laser, filler, peel hóa học

### Bước 4: Mỗi nhóm cần 6 thành phần

Cho mỗi `main_problem`, viết:

| Field | Ví dụ |
|---|---|
| `code` | `MUN_DA_DAU` |
| `name_vi` | "Mụn & da dầu" |
| `description` | "Da dầu, mụn ẩn, mụn viêm tái đi tái lại sau 25. Đã thử 5-10 brand vẫn không trị dứt." |
| `keywords[]` | 25-40 từ khóa: viết tắt TikTok, slang, từ đồng nghĩa |
| `sub_problems[]` | 6-8 nỗi đau con trong nhóm |
| `common_emotions[]` | 4-6 cảm xúc khi gặp vấn đề ("xấu hổ", "tự ti", "tuyệt vọng") |
| `hidden_desires[]` | 4 mong muốn ẩn (vd "muốn soi gương buổi sáng và mỉm cười") |
| `content_angles[]` | 5 ý tưởng video gợi ý (sẽ sàng lọc lại sau khi run thật) |

**Quy tắc keyword**:
- ✅ 2-4 từ liền nhau làm phrase ("đêm nào cũng thức dậy")
- ✅ Cover viết tắt ("k", "ko", "ms", "mn")
- ❌ Tránh keyword 1 từ quá generic ("đẹp", "buồn")
- ❌ Tránh keyword chỉ xuất hiện 1 lần trong 1 quote

### Bước 5: Chạy dữ liệu thật (không trên giấy!)

```powershell
# 1. Init folder
tim init <niche-slug>
# Edit urls.txt với 3-5 URL TikTok cùng niche

# 2. Run pipeline gốc
tim run --urls-file output/<niche>/<date>/urls.txt --max-comments 100

# 3. Build bank
tim bank -i output/<niche>/<date>/classified.json --config niche_configs/<niche>.json
```

**Yêu cầu data**:
- Tối thiểu **3 video / 100 comment / video** cho lần test đầu
- Mix loại video: 1 viral (>1M view), 1 medium (>100K), 1 niche specific
- Tránh video toàn praise comment (KOL fanbase) → bias

### Bước 6: Xem UNCLASSIFIED

Mở `2-sắp-xếp.md`, scroll xuống section "⚠️ Unclassified".

| % UNCLASSIFIED | Hành động |
|---|---|
| **<30%** | Config tốt, đi tiếp Bước 8 |
| **30-50%** | Bước 7 — tune taxonomy |
| **>50%** | Taxonomy có vấn đề lớn — review lại 9 nhóm |

**Đọc top 20 quote unclassified**:
1. Có pattern lặp lại không? (vd 8 quote đều nói "ngủ không yên")
2. Pattern này nên thuộc nhóm nào trong 9 nhóm hiện có?
3. Hay cần add nhóm thứ 10?

### Bước 7: Tune taxonomy

Quy trình **Bước 2.5** đã document chi tiết trong [SOP_BUILD_INSIGHT_DRAFT.md](SOP_BUILD_INSIGHT_DRAFT.md) section 6.5.

**Tóm tắt**:
1. Map pattern unclassified → main_problem phù hợp
2. Trích keyword đặc trưng (2-4 từ)
3. Append vào `keywords[]` của nhóm đó trong config JSON
4. Re-run `tim bank` trên cùng `classified.json` (free, không tốn API)
5. So sánh before/after: UNCLASSIFIED %, distribution, side effect (nhóm nào bị shift)
6. Update `evolution_notes.version_log` trong config

**Mục tiêu sau tune**: UNCLASSIFIED <30%, distribution có balance hơn.

**Khi nào DỪNG tune**:
- UNCLASSIFIED <30% và residual chủ yếu là off-topic/spam → STOP
- Pattern xuất hiện <2 lần → STOP (đợi run thêm 2-3 niche)
- 3 vòng tune vẫn không cải thiện → có thể taxonomy thiếu nhóm, cân nhắc add

### Bước 8: Chấm demand score

Score được tính tự động bởi `insight_bank.py` theo `scoring_rules` trong config:

```
demand_score = (likes × w_likes)
             + (replies × w_replies)
             + bucket_bonus[bucket]
             + problem_priority_bonus[problem_code]
             + intent_bonus[intent_label]
```

**Tune weights** sau MVP test:
- Nếu thấy angle viral từ insight có **likes thấp + replies cao** → tăng `w_replies`
- Nếu nhóm A luôn ra angle hay hơn nhóm B → tăng `problem_priority_bonus[A]`

→ Tune dựa trên **post-mortem thực tế**, không phải guess.

### Bước 9: Tạo `3-lựa-chọn.md`

`tim bank` đã tự sinh — không phải làm gì thêm.

Top 30 candidates auto-promote (score ≥ `auto_promote_to_top` threshold trong config, default 20).

### Bước 10: NGƯỜI chọn insight

Anh / nhân viên content lead mở `3-lựa-chọn.md`, tick `[x]` 5-10 angle muốn quay tuần này.

→ Bước này **KHÔNG được delegate cho AI**. Đây là chiến lược thương hiệu.

→ Sau đó chạy `tim select -i .../3-lựa-chọn.md` để chuyển vào pipeline.

### Bước 11: Export handoff cho CoWork

```powershell
tim export-for-cowork -i output/<niche>/_master/selected_angles.json --config niche_configs/<niche>.json
```

Module sẽ generate file `_master/insights-pack-for-cowork.md` — đây là **source of truth**, miner KHÔNG đẩy sang CoWork.

→ CoWork (`D:\Nhi Hien CoWork`) tự **PULL** khi cần. Xem [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) mục 10 (Pull model).

→ **Trách nhiệm miner DỪNG ở đây**. Việc viết bài, calendar, voice, visual, post-mortem — thuộc CoWork.

### Bước 12: (Optional) Feedback loop — mining own audience

Sau khi CoWork đăng bài ≥7 ngày, comment audience phản hồi — có thể feed lại vào miner làm input mới:

1. Scrape comment dưới chính bài chị Hiền (link FB/IG)
2. Chạy lại `tim run` với URL bài đó → comment thật của audience riêng
3. `tim classify → tim bank → tim select → tim export-for-cowork` → insight v2 chính xác hơn cho voice riêng

→ Khác lần đầu (scrape KOL khác) → đây là **mining own audience**, insight phù hợp 100% với brand.

**Quan sát patterns sau 5-10 bài đăng** (CoWork track ở `memory.md` project):
- Nhóm vấn đề nào engagement cao? → CoWork báo về để miner tăng `problem_priority_bonus` trong niche_config
- Comment audience có insight mới không? → feed lại pipeline (mining own audience như trên)

→ Đây là **vòng feedback liên hệ 2 hệ thống**, không phải trong code miner. Trigger: CoWork báo về.

---

## 5. Template `niche_config` cho ngành mới

```json
{
  "$schema_version": "1.0",
  "_doc": "Niche config cho <niche-name>. Đổi niche = đổi file này, không đổi code.",

  "niche_slug": "<kebab-case-slug>",
  "niche_name": "<Tên đầy đủ tiếng Việt>",

  "persona": {
    "summary": "1-2 đoạn mô tả persona cụ thể",
    "age_range": [<min>, <max>],
    "life_stage": ["...", "..."],
    "business_stage": ["...", "..."],
    "media_behavior": ["...", "..."],
    "core_tensions": [
      "vừa muốn X vừa sợ Y",
      "vừa khao khát A vừa không dám B"
    ]
  },

  "positioning": {
    "for_whom": "<persona ngắn gọn>",
    "promise": "<lời hứa cốt lõi>",
    "tone": "peer-level, ấm, thực tế, không lên lớp",
    "anti_pattern": [
      "tránh ngôn ngữ guru / motivation cliché",
      "tránh hứa quá",
      "..."
    ]
  },

  "method": {
    "name": "Liệt kê → Sắp xếp → Lựa chọn → Thực thi",
    "steps": [
      {"code": "LIET_KE", "label": "Liệt kê", "output": "1-liệt-kê.csv"},
      {"code": "SAP_XEP", "label": "Sắp xếp", "output": "2-sắp-xếp.md"},
      {"code": "LUA_CHON", "label": "Lựa chọn", "output": "3-lựa-chọn.md"},
      {"code": "THUC_THI", "label": "Thực thi", "output": "4-thực-thi/angle-XX.md"}
    ]
  },

  "main_problems": [
    {
      "code": "PROBLEM_CODE_1",
      "name_vi": "Tên 2-4 từ",
      "description": "1-2 câu mô tả",
      "keywords": ["keyword 1", "keyword 2", "..."],
      "sub_problems": ["...", "..."],
      "common_emotions": ["...", "..."],
      "hidden_desires": ["...", "..."],
      "content_angles": ["...", "..."]
    }
    // ... 9-12 nhóm tổng cộng
  ],

  "intent_labels": {
    "labels": [
      {"code": "VENT", "label": "Trút bầu tâm sự"},
      {"code": "SEEK_HOWTO", "label": "Hỏi cách làm"},
      {"code": "SEEK_VALIDATION", "label": "Tìm sự đồng cảm"},
      {"code": "SEEK_RECOMMENDATION", "label": "Xin gợi ý"},
      {"code": "SHARE_EXPERIENCE", "label": "Chia sẻ trải nghiệm"},
      {"code": "DISAGREE", "label": "Phản đối"},
      {"code": "TAG_FRIEND", "label": "Tag bạn"},
      {"code": "PRAISE_KOL", "label": "Khen KOL"}
    ]
  },

  "content_opportunity_labels": {
    "labels": [
      {"code": "HOOK_QUOTE", "format": "Reel 15s đọc quote + reaction"},
      {"code": "PAIN_SOLUTION", "format": "Reel 60s validate → root cause → action"},
      {"code": "FAQ_ANSWER", "format": "Reel 30-60s Q&A"},
      {"code": "MYTH_BUST", "format": "Reel 60s 'người ta nghĩ X, thực ra Y'"},
      {"code": "SOCIAL_PROOF", "format": "Reel 60-90s case study"},
      {"code": "FRAMEWORK", "format": "Carousel hoặc Reel 90s 'X bước để...'"}
    ]
  },

  "scoring_rules": {
    "formula": "demand_score = (likes × w_likes) + (replies × w_replies) + bucket_bonus + problem_priority_bonus + intent_bonus",
    "weights": {"w_likes": 1.0, "w_replies": 3.0},
    "bucket_bonus": {"pain": 5, "desire": 4, "question": 4, "objection": 3, "praise": 0, "mention": 0, "other": 0},
    "problem_priority_bonus": {
      "PROBLEM_CODE_1": 5,
      "PROBLEM_CODE_2": 5,
      "_unmatched": 0
    },
    "intent_bonus": {"SEEK_HOWTO": 3, "SEEK_RECOMMENDATION": 3, "VENT": 2, "...": 0},
    "thresholds": {
      "must_review": 10,
      "auto_promote_to_top": 20
    }
  },

  "output_files": {
    "step_1_liet_ke": {
      "path": "1-liệt-kê.csv",
      "columns": ["id", "problem_code", "bucket", "intent_label", "opportunity_label", "demand_score", "likes", "replies", "author", "quote", "summary", "video_url", "status"]
    },
    "step_2_sap_xep": {"path": "2-sắp-xếp.md"},
    "step_3_lua_chon": {"path": "3-lựa-chọn.md", "max_candidates": 30},
    "step_4_thuc_thi": {"path": "4-thực-thi/", "is_folder": true}
  },

  "evolution_notes": {
    "v1.0 (<date>)": "Init: 9 nhóm + ~25-35 keyword/nhóm",
    "v1.1 (<date>)": "Tune từ data thật: ..."
  }
}
```

→ Copy file này, fill placeholder, save vào `niche_configs/<niche-slug>.json`.

---

## 6. Quy tắc tạo taxonomy tốt

### 6.1 Không bắt đầu bằng keyword, bắt đầu bằng vấn đề thật

❌ **Sai**: Brainstorm 100 keyword "skincare" rồi cố group thành nhóm
✅ **Đúng**: Tự hỏi "persona này 6h sáng lo gì?" → 5-10 nỗi lo → 9 nhóm

→ Keyword là **biểu hiện ngôn ngữ** của nhóm, không phải định nghĩa nhóm.

### 6.2 Mỗi nhóm phải đại diện 1 cụm pain/desire rõ

Test: cho người ngoài đọc `name_vi` + `description`, họ có hình dung **cụ thể 1 cảm giác / cảnh** không?

- "Mụn ẩn quanh cằm sau 30" — ✅ rõ
- "Vấn đề về da" — ❌ quá rộng

### 6.3 Có sub-problem (chi tiết hóa)

Mỗi nhóm 6-8 sub_problems. Đây là **map các góc** trong nhóm — sau dùng để gợi ý angle cụ thể.

Ví dụ nhóm `MUN_DA_DAU`:
- "mụn ẩn quanh cằm chu kỳ kinh"
- "lỗ chân lông to vùng mũi"
- "da dầu cuối ngày bóng nhờn"
- "thử retinoid bị đỏ rát bỏ"
- ...

### 6.4 Có emotion (cảm xúc thật)

Liệt kê 4-6 cảm xúc khi gặp vấn đề. Đây là **input cho prompt production** để Claude viết script empathy đúng tone.

❌ Tránh: "buồn", "lo lắng" (quá generic)
✅ Đúng: "xấu hổ khi đi sự kiện", "tự ti với bạn cùng tuổi không bị mụn", "tuyệt vọng vì đã thử 10 brand"

### 6.5 Có hidden desire (mong muốn ẩn)

4 mong muốn **ẩn dưới bề mặt** — không phải user nói thẳng nhưng là điều thực sự khao khát.

Ví dụ persona kinh doanh:
- Surface desire: "muốn doanh thu cao hơn"
- Hidden desire: "muốn 1 ngày KHÔNG phải nghĩ về business"

→ Hidden desire chính là **đòn bẩy** cho hook viral.

### 6.6 Có content angle gợi ý

Cho mỗi nhóm, list 5 angle gợi ý. Đây là **starter kit** trước khi run dữ liệu thật.

Sau khi run, sẽ có angle thật từ comment — angle gợi ý này chỉ để brainstorm, không bắt buộc dùng.

### 6.7 Không ép tất cả comment vào nhóm

UNCLASSIFIED 10-40% là **bình thường** ở giai đoạn đầu. Có 3 lý do hợp lý để comment ở UNCLASSIFIED:
1. Off-topic (hỏi nhạc nền, tag bạn)
2. Quá generic ("hay quá", "+1")
3. Insight thật nhưng config v1 chưa cover → input cho Bước 7 tune

→ KHÔNG cố add keyword cho mọi quote — over-fit + false positive cao.

---

## 7. Quy tắc tune taxonomy (đúc kết từ Bước 2.5 MVP)

### 7.1 Tune từ dữ liệu thật, không tune trên giấy

❌ Tune dựa trên giả định "có lẽ chị em sẽ nói X"
✅ Tune dựa trên 20 quote thật trong UNCLASSIFIED của run thực

### 7.2 Chỉ thêm keyword nếu quote có insight rõ

3 câu hỏi check:
1. Quote này có pattern lặp lại ≥2 lần trong dataset không?
2. Pattern này có map vào 1 trong 9 nhóm hiện có không?
3. Keyword này có đủ specific để KHÔNG false positive ở comment khác không?

→ Nếu không 3/3 ✅ → KHÔNG add.

### 7.3 Theo dõi side effect shift nhóm

Khi add keyword vào nhóm có `problem_priority_bonus` cao, có thể **đánh cắp** insight vốn match nhóm khác.

**Ví dụ thực tế MVP**: add "vật chất có" vào TIEN_BAC → 1 quote vốn match HINH_ANH_PHONG_CACH bị shift sang TIEN_BAC.

→ **Workflow**: trước khi commit, check distribution của TẤT CẢ nhóm, không chỉ nhóm tune.

### 7.4 So sánh before/after metric

Sau mỗi vòng tune, đo 3 metric:
- % UNCLASSIFIED (giảm bao nhiêu?)
- Distribution balance (nhóm nào tăng, nhóm nào giảm)
- Top 10 cross-niche có thay đổi không?

### 7.5 Ghi `evolution_notes.version_log` mỗi lần tune

```json
"version_log": {
  "v1.0 (2026-05-08)": "Init",
  "v1.1 (2026-05-08)": "+30 kw TIEN_BAC, +14 GIA_TRI, ..."
}
```

→ 6 tháng sau vẫn nhớ vì sao có keyword đó.

### 7.6 Dừng tune khi marginal return thấp

Khi UNCLASSIFIED <30% mà residual chủ yếu là off-topic → **STOP**.

→ Đừng cố tune đến 0% UNCLASSIFIED — over-fit data hiện tại, hại data tương lai.

---

## 8. Quy tắc chọn insight (Bước 10 — strategic)

### 8.1 AI đề xuất, người quyết định

`3-lựa-chọn.md` là **AI rank theo demand**. Người quyết định **angle nào trúng định vị thương hiệu**.

→ KHÔNG tick `[x]` toàn bộ top 10 score — cần judgement.

### 8.2 Ưu tiên demand thật

Insight có:
- ≥10 likes hoặc ≥3 replies → demand đã verified
- 0 like 0 reply → có thể là 1 case lẻ, kém ưu tiên hơn

### 8.3 Ưu tiên insight gần offer

Nếu anh đang bán **khóa coaching tài chính** cho phụ nữ kinh doanh:
- ✅ Tick: insight về `TIEN_BAC_BINH_YEN`, `KINH_DOANH_KIET_SUC`
- ❌ Không tick: insight về `HINH_ANH_PHONG_CACH` (không gần offer)

→ Mỗi tuần làm 5-10 video, ưu tiên video **dẫn đến sản phẩm**.

### 8.4 Ưu tiên insight có cảm xúc mạnh

Quote dạng "hôm qua mình khóc khi..." > quote dạng "có ai biết làm sao để...".

Cảm xúc mạnh = video viral cao + dễ chạm audience.

### 8.5 Ưu tiên insight dễ biến thành content / action

Quote rõ pain + có hint giải pháp dễ → angle dễ viết.
Quote ambiguous, abstract → angle khó viết, dễ guru.

### 8.6 KHÔNG chọn chỉ vì score cao

Score là **tín hiệu**, không phải **mệnh lệnh**. Insight score 226 nhưng off-brand → SKIP.

---

## 9. Quy tắc thực thi insight (Bước 11)

### 9.1 Mỗi insight chọn → 1 action cụ thể

KHÔNG để insight chỉ nằm trong file `_master/`. Phải biến thành **output có format**:

| Loại output | Cấu trúc |
|---|---|
| **Content video** | Hook + Script + B-roll + Caption + CTA + Checklist + Post-mortem |
| **Offer / sản phẩm** | Pain → Promise → Mechanism → Objection → Proof |
| **Sản phẩm số / app** | Feature priority + Use case + User language + Edge case |
| **Sales / nurture** | Objection map + FAQ + Proof angle + Pricing rationale |

→ MVP hiện tại làm cho **content video** (`production.py`). Các loại khác cần module riêng (chưa làm).

### 9.2 Production brief = bản nháp, không phải final

Output Claude rất tốt nhưng vẫn cần edit:
- Veto Big idea nếu off-brand
- Edit Hook để hợp giọng cá nhân
- Edit Caption khớp tone tài khoản

→ Coi `angle-XX.md` là **draft 1**, `angle-XX-final.md` là phiên bản đi quay.

### 9.3 Post-mortem là vòng feedback bắt buộc

Sau 7 ngày đăng:
- Fill section 10 trong `angle-XX.md` (view, like, comment, save)
- **Bài học rút ra**: 1 câu

→ Sau 5-10 video, mở loạt post-mortem → patterns:
- Nhóm vấn đề nào viral nhiều nhất?
- Hook style nào engagement cao?

→ Tune `problem_priority_bonus` + prompt suggester dựa trên patterns này.

---

## 10. Cách mở rộng sang ngành khác

### 10.1 Quy tắc số 1: Đổi config trước, đổi code sau (nếu cần)

99% trường hợp đổi niche **chỉ cần đổi `niche_configs/<slug>.json`**.

Code core (`scraper.py`, `classifier.py`, `insight_bank.py`, `selection.py`, `production.py`) **dùng lại nguyên**.

### 10.2 Ví dụ niche tiềm năng

| Niche | Slug đề xuất | Đặc thù cần lưu ý |
|---|---|---|
| **Skincare 25-40** | `skincare-tuoi-25-40` | Nhiều thuật ngữ khoa học (retinoid, niacinamide) — keywords cần cover viết chuẩn + viết tắt |
| **Spa & thẩm mỹ viện** | `spa-tham-my-vien` | Audience chia 2: practitioner vs customer — có thể cần 2 niche riêng |
| **Mẹ & bé 0-3 tuổi** | `me-be-0-3-tuoi` | Emotion strong: lo lắng + guilt → bonus emotion-related insight |
| **Giáo dục online** | `khoa-hoc-online` | Nhiều objection ("đắt", "không kịp học") → bonus `objection` bucket |
| **Bất động sản** | `bds-can-ho-tphcm` | Decision cycle dài + cao value → demand_score weights khác (less likes, more depth) |
| **Tài chính cá nhân** | `tai-chinh-ca-nhan` | Trùng partial với `kinh-doanh-27-45` ở nhóm `TIEN_BAC` — có thể merge nhóm |
| **Đầu tư chứng khoán** | `dau-tu-chung-khoan` | Audience 80% nam 25-45 — persona ngược niche kinh doanh nữ |

### 10.3 Quy trình copy-and-modify

```powershell
# Copy config gần niche mới nhất
cp niche_configs/kinh-doanh-27-45.json niche_configs/skincare-tuoi-25-40.json

# Edit:
# 1. niche_slug + niche_name
# 2. persona (tuổi, life stage, media behavior)
# 3. positioning (tone, anti_pattern)
# 4. main_problems[] — REPLACE 9 nhóm cũ
# 5. scoring_rules.problem_priority_bonus — match tên nhóm mới
# 6. evolution_notes — reset version_log
```

### 10.4 Khi nào CẦN đổi code?

Hiếm khi. Chỉ trong các case:
- Add nền tảng mới (YouTube, FB) → cần `youtube_scraper.py`, `fb_scraper.py`
- Output type khác (vd offer brief thay vì video brief) → cần module mới (vd `offer_production.py`)
- Scoring formula phức tạp hơn (vd time-decay) → sửa `scoring_rules` parser trong `insight_bank.py`

→ Còn lại, **luôn ưu tiên giải quyết qua config**.

---

## 11. Checklist SOP dùng cho ngành mới

Copy-paste checklist này mỗi lần build niche mới:

```markdown
## Build niche: <NICHE-SLUG>

### Phase 1: Setup config (~30-60 phút)
- [ ] Đặt niche_slug (kebab-case, đã check unique trong niche_configs/)
- [ ] Viết persona (1-2 đoạn cụ thể, có core_tensions)
- [ ] Viết positioning (tone, anti_pattern)
- [ ] Brainstorm 9-12 main_problems (3 câu hỏi: 6h sáng họ lo gì?)
- [ ] Mỗi nhóm: code, name_vi, description, keywords (25-40), sub_problems (6-8), emotions (4-6), hidden_desires (4), content_angles (5)
- [ ] Set scoring_rules.problem_priority_bonus theo strategic priority
- [ ] Validate JSON: `python -c "import json; json.load(open('niche_configs/<slug>.json'))"`

### Phase 2: Run dữ liệu thật lần 1 (~15 phút + 5 phút API)
- [ ] Chọn 3-5 video TikTok cùng niche, mix viral + medium + niche-specific
- [ ] `tim init <slug>` → tạo folder
- [ ] Edit `urls.txt`
- [ ] `tim run --urls-file ... --max-comments 100 -o output/<slug>/<date>`
- [ ] Verify `classified.json` có ≥50 comment
- [ ] `tim bank -i .../classified.json --config niche_configs/<slug>.json`

### Phase 3: Tune taxonomy (Bước 2.5) (~15-30 phút)
- [ ] Đọc section UNCLASSIFIED trong `2-sắp-xếp.md`
- [ ] Phân top 20 quote unclassified thành 3-5 pattern
- [ ] Map mỗi pattern → main_problem nào (hoặc giữ UNCLASSIFIED nếu off-topic)
- [ ] Append keywords vào config
- [ ] Re-run `tim bank` → so sánh before/after
- [ ] Update `evolution_notes.version_log`
- [ ] Verify UNCLASSIFIED <30%

### Phase 4: Lựa chọn (~15 phút)
- [ ] Mở `3-lựa-chọn.md`, đọc top 30
- [ ] Tick `[x]` 5-10 angle (mix nhóm, gần offer, demand thật)
- [ ] `tim select -i .../3-lựa-chọn.md`
- [ ] Verify `_master/content-pipeline.md` có đủ N row

### Phase 5: Handoff cho CoWork (~5 giây)
- [ ] `tim export-for-cowork -i .../selected_angles.json --config niche_configs/<slug>.json`
- [ ] Verify file `_master/insights-pack-for-cowork.md` đã tạo + có đủ insight + distribution đúng
- [ ] **Trách nhiệm miner DỪNG ở đây**

### Phase 6-7: KHÔNG TRONG SCOPE MINER (CoWork lo)

Việc viết bài, calendar, voice, visual, post-mortem — thuộc CoWork:
- CoWork pull file insight về (skill `pull-insights-from-miner`)
- CoWork chấm điểm 5 trục (Content Proposal Protocol) → Hiền chọn concept
- CoWork viết bài theo 7 bước (xem `ABOUT ME/00_README.md`)
- CoWork track post-mortem ở `memory.md` project

→ Xem [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) cho flow đầy đủ.
```

---

## 12. Bài học từ MVP "phụ nữ kinh doanh 27–45"

### 12.1 Config v1 luôn là **guess**

Em viết config v1 dựa trên kinh nghiệm + folder `gia-tri-ban-than/_master/` cũ — toàn là **hypothesis**.

→ KHÔNG cố làm config "perfect" trước khi run thực. Run sớm, tune sau.

### 12.2 Dữ liệu thật mới giúp tune đúng

Run thật trên niche `phu-nu-kinh-doanh` lộ ra:
- Pattern "đạt được rồi không vui" lặp lại 11 lần — không có keyword cover trong v1.0
- Pattern "lo toan hôn nhân" — 2 lần — đáng add
- Pattern "tay trắng / mảng tiêu cực" — 2 lần — đáng add

→ Sau Bước 2.5 tune: UNCLASSIFIED giảm 39-50%, distribution có balance hơn.

### 12.3 UNCLASSIFIED là mỏ vàng

KHÔNG xem UNCLASSIFIED là "fail" của taxonomy. Xem nó là **TODO list** để improve config.

### 12.4 Broad keyword có thể gây side effect shift nhóm

Ví dụ: thêm "vật chất có" (broad) vào TIEN_BAC → 1 quote vốn match HINH_ANH bị shift sang TIEN_BAC do tie-break theo `problem_priority_bonus`.

→ **Workflow phòng ngừa**: trước commit config mới, check distribution TẤT CẢ nhóm.

### 12.5 Người chọn insight vẫn là trung tâm

`tim suggest` (AI tự pick 10 angle) là **alternative path**, không phải workflow chính.

Workflow chính: `bank → tick → select → production` — anh quyết.

→ Định vị thương hiệu + judgement chiến lược không có công thức, AI không biết được.

### 12.6 Fallback giúp hệ thống không phụ thuộc hoàn toàn vào AI

`production.py` có 2 path: Claude (creative quality) + Fallback rule-based.

→ Tool LUÔN chạy được:
- API down → fallback
- Hết quota Anthropic → fallback
- Test pipeline không tốn API → `--no-claude`
- Anh muốn tự viết tay → `--no-claude` rồi edit thẳng

### 12.7 Bảng tổng kết timeline MVP

| Stage | Effort | Output cumulative |
|---|---|---|
| Bước 1 (config v1.0) | 30 phút | `niche_configs/kinh-doanh-27-45.json` |
| Bước 2 (insight_bank.py) | 1 giờ | 3 file output / classified |
| Bước 2.5 (tune config v1.1) | 30 phút | UNCLASSIFIED giảm 39-50% |
| Bước 3 (selection.py) | 1 giờ | `_master/content-pipeline.md` + `selected_angles.json` |
| Bước 4 (production.py) | 2 giờ | `4-thực-thi/angle-XX.md` x N |
| Bước 5 (docs) | 30 phút | `MVP_WORKFLOW.md` + `SOP_BUILD_INSIGHT_V1.md` |
| **Tổng** | **~5.5 giờ code** | MVP đủ 4 bước ready để chạy thật |

→ MVP nhỏ, build nhanh, không over-engineer.

---

## Tài liệu liên quan

**Bên miner (scope hiện tại)**:
- [SOP_CLONE_NICHE.md](SOP_CLONE_NICHE.md) — **Playbook clone niche mới** (use khi onboard ngành/brand mới)
- [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) — Sơ đồ flow miner → CoWork (v2 Pull model)
- [MAPPING_FREEDOM_LAYER.md](MAPPING_FREEDOM_LAYER.md) — Mapping problem_code → 4 lớp tự do
- [SOP_BUILD_INSIGHT_DRAFT.md](SOP_BUILD_INSIGHT_DRAFT.md) — Chi tiết kỹ thuật từng module
- [MVP_WORKFLOW.md](MVP_WORKFLOW.md) — Hands-on guide cho anh + nhân viên
- [../niche_configs/kinh-doanh-27-45.json](../niche_configs/kinh-doanh-27-45.json) — Niche config v1.4 (đã có freedom_layer)
- [../README.md](../README.md) — Quick start
- [../USAGE.md](../USAGE.md) — Reference command lines

**Deprecated (giữ làm history, không dùng cho scope mới)**:
- [SOP_UPDATE_WRITING_METHODS.md](SOP_UPDATE_WRITING_METHODS.md) — Moved sang CoWork
- `profiles/chi-hien/` — Voice moved sang `D:\Nhi Hien CoWork\ABOUT ME\`
- `docs/writing_methods/` — Moved sang `D:\Nhi Hien CoWork\RESOURCES\GUIDES\`
- `strategy_configs/` — Moved sang CoWork project folder

**Bên CoWork (client của miner)**:
- `D:\Nhi Hien CoWork\ABOUT ME\00_README.md` — Flow viết bài 7 bước
- `D:\Nhi Hien CoWork\ABOUT ME\content-proposal-protocol.md` — Chấm điểm 5 trục
- `D:\Nhi Hien CoWork\ABOUT ME\voice-profile.md` — Voice + xưng hô
- `D:\Nhi Hien CoWork\ABOUT ME\writing-rules.md` — Kỹ thuật câu chữ
- `D:\Nhi Hien CoWork\ABOUT ME\visual-identity.md` — DNA visual + 3 combo

---

**Updated**: 2026-05-16 · **v2** (refactor scope: chỉ kho insight + handoff, bỏ voice/strategy/calendar/writing methods, move sang CoWork)
**Tinh thần**: Miner là **mỏ vàng insight** (source of truth). CoWork là **xưởng chế tác**. 2 hệ thống, 2 trách nhiệm, 1 file handoff. Miner không biết CoWork tồn tại. CoWork tự lấy khi cần.

**Version log**:
- v1 (2026-05-08): MVP đúc kết sau niche "phụ nữ kinh doanh 27–45"
- v2 (2026-05-16): Refactor — split scope rõ ràng giữa miner (insight) và CoWork (writing). Pull model.
