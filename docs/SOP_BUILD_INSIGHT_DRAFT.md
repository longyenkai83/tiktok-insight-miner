# SOP — Build Insight Bank (DRAFT v0.1)

> **Mục đích**: Quy trình biến `classified.json` (output của Claude classifier) thành **insight bank** có thể browse + lựa chọn được, theo phương pháp **Liệt kê → Sắp xếp → Lựa chọn → Thực thi**.
>
> **Trạng thái**: Draft — viết sau khi build module `insight_bank.py` (Bước 2 MVP). Sẽ refine khi đã chạy 5+ niche thực và rút kinh nghiệm.
>
> **Nguyên tắc**: SOP này phải chạy được cho **mọi ngành** (kinh doanh nữ, sức khỏe, làm cha mẹ, đầu tư...) — không hardcode niche.

---

## 1. Phương pháp 4 bước

| # | Bước | Mục tiêu | Output |
|---|---|---|---|
| 1 | **Liệt kê** | Lấy hết insight thô ra khỏi data, không bỏ sót | `1-liệt-kê.csv` |
| 2 | **Sắp xếp** | Group theo nhóm vấn đề + sort theo demand | `2-sắp-xếp.md` |
| 3 | **Lựa chọn** | User tick top N angle muốn thực thi | `3-lựa-chọn.md` |
| 4 | **Thực thi** | Mỗi angle đã pick → script đầy đủ | `4-thực-thi/angle-XX.md` *(làm ở module riêng)* |

Bước 1-3 = scope của module `insight_bank.py`.
Bước 4 = scope của module `production.py` (chưa có).

---

## 2. Input

### 2.1 `classified.json` (bắt buộc)

Output của stage `tim classify`. Cấu trúc:

```json
[
  {
    "comment": {"id": "...", "text": "...", "author": "...", "likes": 12, "reply_count": 3, "video_url": "..."},
    "bucket": "pain",
    "summary": "Mô tả insight 1 câu",
    "confidence": 0.85
  }
]
```

### 2.2 `niche_configs/<slug>.json` (bắt buộc)

Định nghĩa **taxonomy ngành**. Bắt buộc có:

| Key | Vai trò |
|---|---|
| `niche_slug`, `niche_name` | ID + tên hiển thị |
| `persona`, `positioning` | Để downstream (production.py) sinh script đúng tone |
| `main_problems[]` | **9-12 nhóm vấn đề** đặc trưng ngành. Mỗi nhóm có `code`, `keywords`, `description`, etc. |
| `intent_labels` | Layer phụ trên 7 bucket gốc — phân biệt VENT vs SEEK_HOWTO vs SHARE_EXPERIENCE... |
| `content_opportunity_labels` | Map insight → format video (HOOK_QUOTE, FAQ_ANSWER, MYTH_BUST...) |
| `scoring_rules` | Công thức demand_score |
| `output_files` | Path + columns + threshold cho 3 file output |

→ **Module insight_bank.py CHỈ ĐỌC config, KHÔNG hardcode.** Đổi niche = đổi config, không phải đổi code.

---

## 3. Output

### 3.1 `1-liệt-kê.csv` (Excel-friendly)

UTF-8 with BOM (Excel mở đúng tiếng Việt).

| Column | Ý nghĩa |
|---|---|
| `id` | `P001`, `D012`... — bucket initial + sequential |
| `problem_code` | 1 trong 9 nhóm config (hoặc `UNCLASSIFIED`) |
| `bucket` | pain / desire / question / objection (chỉ giữ 4 actionable) |
| `intent_label` | VENT / SEEK_HOWTO / DISAGREE / ... |
| `opportunity_label` | HOOK_QUOTE / PAIN_SOLUTION / FAQ_ANSWER / ... |
| `demand_score` | Theo công thức scoring (xem mục 4) |
| `likes`, `replies` | Raw signal |
| `author`, `quote`, `summary`, `video_url` | Để trace gốc |
| `status` | `todo` mặc định — anh có thể edit thành `doing/done/skip` để track tay |

Sort: theo `demand_score` desc.

### 3.2 `2-sắp-xếp.md`

Sections:
1. **Tổng quan 9 nhóm** — table: count + Σ demand_score + top likes
2. **Top 10 cross-niche** — quote ngắn, score, bucket, intent, opportunity
3. **Chi tiết từng nhóm** — sort theo demand_score desc trong group
4. **Unclassified section** (nếu có) — hint để bổ sung keyword vào config

### 3.3 `3-lựa-chọn.md`

Top N candidates (default 30, hoặc `auto_promote_to_top` threshold), dạng checkbox:

```markdown
- [ ] [SCORE 24] [P03 KINH_DOANH_KIET_SUC] [PAIN_SOLUTION] "quote ngắn" — @author (12 likes)
  - 💡 summary
  - 📂 nhóm: Kinh doanh kiệt sức · 🎯 intent: VENT
```

User tick `[x]` các angle muốn thực thi → input cho module `selection.py` (chưa làm).

---

## 4. Quy tắc thiết kế (lý do đằng sau)

### 4.1 Vì sao filter chỉ giữ 4 bucket actionable?

`praise/mention/other` không actionable cho content angle:
- `praise` → testimonial repurpose, không phải "vấn đề" cần giải
- `mention` → tag bạn, social signal sharing
- `other` → spam, off-topic

→ Loại sớm để CSV gọn, score không bị nhiễu.

### 4.2 Vì sao keyword matching thay vì gọi Claude lần nữa?

| Tiêu chí | Keyword match | Gọi Claude |
|---|---|---|
| Cost | $0 | ~$0.001/insight |
| Tốc độ | <1s/100 insight | 5-10s/batch |
| Deterministic | ✅ chạy lại = kết quả giống | ❌ có variance |
| Debug | ✅ thấy ngay keyword nào hit | ❌ black box |
| Tune | edit config JSON | edit prompt + test |

→ Cho stage **classify nhóm vấn đề + intent + opportunity**, keyword đủ tốt vì đây là rule-based decision.
Stage `production.py` (Bước 4) mới gọi Claude cho creative work (script, hook variations).

### 4.3 Tie-break khi insight match nhiều nhóm

Ưu tiên:
1. Số keyword hits cao hơn
2. Nếu hòa → nhóm có `problem_priority_bonus` cao hơn (theo config)

Lý do: 1 comment kiểu "kinh doanh mệt + chồng không hiểu" có thể match cả `KINH_DOANH_KIET_SUC` lẫn `GIA_DINH_GONG_GANH`. Cho phép config quyết định nhóm nào priority hơn cho niche đó.

### 4.4 Công thức demand_score

```
demand_score = (likes × w_likes) + (replies × w_replies)
             + bucket_bonus[bucket]
             + problem_priority_bonus[problem_code]
             + intent_bonus[intent_label]
```

Default weights:
- `w_likes = 1.0`
- `w_replies = 3.0` (1 reply = effort hơn 1 like ~3 lần)
- `bucket_bonus`: pain=5, desire=4, question=4, objection=3
- `problem_priority_bonus`: theo niche, top 3 nhóm hot = +5
- `intent_bonus`: SEEK_HOWTO/RECOMMENDATION = +3, VENT/SHARE = +2

→ Mọi weights đều ở config, **không hardcode**. Sau MVP test 5 niche, tune lại dựa trên angle nào thực sự viral.

### 4.5 Threshold `auto_promote_to_top`

Default `20`. Nghĩa là score ≥ 20 → tự động vào `3-lựa-chọn.md`. Dưới threshold nhưng top N → vẫn vào để fill cho đủ N candidates.

→ Avoid "anh phải duyệt 200 insight" — chỉ thấy top quality.

### 4.6 Vì sao output ở sibling folder của classified.json?

Convention: 1 niche / 1 ngày = 1 folder = mọi file của lần chạy đó cùng chỗ.

```
output/<niche>/<date>/
├── raw_comments.json       (scrape stage)
├── classified.json         (classify stage)
├── report.md               (report stage)
├── brief.md                (suggest stage — AI angles)
├── 1-liệt-kê.csv           ← bank stage (mới)
├── 2-sắp-xếp.md            ← bank stage (mới)
├── 3-lựa-chọn.md           ← bank stage (mới)
└── 4-thực-thi/             ← production stage (chưa làm)
```

Có thể override bằng `-o` nếu muốn ghi nơi khác.

---

## 5. CLI usage

```powershell
# Build bank cho 1 lần classify
tim bank `
  -i output/phu-nu-kinh-doanh/2026-05-06/classified.json `
  --config niche_configs/kinh-doanh-27-45.json

# Custom output dir
tim bank `
  -i output/X/classified.json `
  --config niche_configs/Y.json `
  -o output/X/bank-v2/
```

Output console:
```
📊 Niche: kinh-doanh-27-45
   Total insights đọc:   287
   Giữ lại (actionable): 198
   Loại do bucket:       82 (praise/mention/other)
   Loại do quote ngắn:   7 (<5 ký tự)

✓ Output files:
   1️⃣  Liệt kê:   .../1-liệt-kê.csv
   2️⃣  Sắp xếp:   .../2-sắp-xếp.md
   3️⃣  Lựa chọn:  .../3-lựa-chọn.md

👉 Mở `3-lựa-chọn.md`, tick checkbox top 5-10 angle muốn quay tuần này.
```

---

## 6. Workflow anh dùng hàng ngày

1. Nhân viên chạy webapp → có `classified.json` ở `output/<niche>/<date>/`
2. Anh chạy `tim bank -i ... --config ...` (1 lệnh, ~2 giây)
3. Anh mở `2-sắp-xếp.md` → đọc tổng quan 9 nhóm → biết tuần này niche đang nóng nhóm nào
4. Anh mở `3-lựa-chọn.md` → tick top 5-10 angle muốn quay
5. (Bước 4 — chưa có) Chạy `tim production` → generate `4-thực-thi/angle-XX.md` cho team content quay

---

## 6.5. Bước 2.5 — Tune taxonomy từ UNCLASSIFIED

> **Khi nào làm**: ngay sau lần đầu chạy `tim bank` cho 1 niche mới, NẾU UNCLASSIFIED chiếm ≥30% số insight giữ lại.
>
> **Mục tiêu**: bổ sung keyword vào `niche_config.json` để phủ hết những pattern insight rõ ràng nhưng bị rớt vì câu chữ TikTok dùng biến thể (viết tắt, slang, dùng từ khác mà cùng nghĩa).
>
> **Nguyên tắc số 1**: KHÔNG ép mọi comment vào nhóm. Comment off-topic / quá generic / spam → đúng để UNCLASSIFIED. Tune chỉ để bắt thêm những cái có insight thực.

### 6.5.1 Quy trình tune (5 bước, ~15 phút)

1. **Mở `2-sắp-xếp.md`**, scroll xuống section "⚠️ Unclassified". Đọc top 20 quote (đã sort theo `demand_score` desc — cái có likes/replies cao = đáng cứu nhất).

2. **Phân pattern**: gom các quote unclassified thành 3-5 pattern lặp lại. Ví dụ run thực:
   - Pattern "đạt rồi không vui" — 11 quote
   - Pattern "lòng tham / muốn nhiều hơn" — 4 quote
   - Pattern "lo toan hôn nhân/con cái" — 2 quote
   - Pattern "sợ ánh nhìn người khác" — 4 quote

3. **Map pattern → main_problem**: với mỗi pattern, quyết định nó nên thuộc nhóm nào trong 9 nhóm config. Nếu KHÔNG nhóm nào fit tự nhiên → có 2 lựa chọn:
   - **Để UNCLASSIFIED** (chấp nhận limitation của taxonomy v1)
   - **Add nhóm thứ 10** (chỉ làm khi pattern xuất hiện ≥2 niche khác nhau)

4. **Trích keyword đặc trưng** từ pattern. Quy tắc:
   - ✅ Lấy 2-4 từ liền nhau làm phrase (vd: "không thấy vui", "lạc trôi giữa đời")
   - ✅ Cover cả viết tắt TikTok ("k", "ko", "ms", "vk", "ck")
   - ❌ TRÁNH keyword 1 từ quá generic ("vui", "buồn", "tiền") — false positive cao
   - ❌ TRÁNH keyword chỉ xuất hiện 1 lần trong 1 quote — over-fit

5. **Edit `niche_configs/<slug>.json`**: append vào `keywords[]` của nhóm tương ứng. Validate JSON, re-run `tim bank` trên cùng `classified.json` cũ → so sánh trước/sau.

### 6.5.2 Metric đo hiệu quả

So sánh trước/sau theo 3 metric:

| Metric | Mục tiêu sau tune |
|---|---|
| **% UNCLASSIFIED** | Giảm xuống <40% (lý tưởng <30%) |
| **Distribution có balance hơn** | Nhiều nhóm có insight (không chỉ 1-2 nhóm chiếm hết) |
| **Side effect** | Không nhóm nào MẤT insight quá nhiều (nếu mất → keyword mới quá broad) |

**Ví dụ run thực — niche "kinh-doanh-27-45" v1.1 (2026-05-08)**:

| Niche test | Metric | Before | After | Δ |
|---|---|---|---|---|
| phu-nu-kinh-doanh | UNCLASSIFIED | 38 (66%) | 23 (40%) | **−39%** |
| gia-tri-ban-than | UNCLASSIFIED | 8 (62%) | 4 (31%) | **−50%** |

### 6.5.3 Side effect cần kiểm tra

Khi add keyword vào nhóm có `problem_priority_bonus` cao, có thể **đánh cắp** insight vốn match nhóm khác (do tie-break theo bonus).

**Ví dụ thực** (run 2026-05-08): sau khi add "vật chất có" vào TIEN_BAC, 1 quote vốn match HINH_ANH_PHONG_CACH bị shift sang TIEN_BAC → HINH_ANH giảm từ 1 → 0.

→ **Workflow phòng ngừa**: trước khi commit config mới, check distribution của TẤT CẢ nhóm, không chỉ nhóm đang tune. Nếu 1 nhóm mất ≥30% insight → keyword mới quá broad, bỏ hoặc gắn ngữ cảnh hẹp hơn.

### 6.5.4 Khi nào DỪNG tune

| Tình huống | Action |
|---|---|
| UNCLASSIFIED đã <30% và residual chủ yếu là off-topic/spam | ✅ DỪNG, ghi `evolution_notes` trong config |
| Còn nhiều insight unclassified nhưng pattern xuất hiện <2 lần | ✅ DỪNG, đợi run thêm 2-3 niche nữa rồi mới tune |
| Sau 3 vòng tune vẫn không cải thiện | ⚠️ Có thể taxonomy 9 nhóm thiếu — cân nhắc add nhóm thứ 10 |
| Quote đặc thù chỉ 1 lần xuất hiện | ❌ Đừng thêm keyword cho 1 quote — over-fit |

### 6.5.5 Document keyword evolution

Mỗi lần tune, update `evolution_notes` trong config:

```json
"evolution_notes": {
  "v1.0 (2026-05-08)": "Init 9 nhóm + ~25 keyword/nhóm",
  "v1.1 (2026-05-08)": "Tune từ phu-nu-kinh-doanh + gia-tri-ban-than → +30 keyword TIEN_BAC, +14 GIA_TRI, +14 GIA_DINH, +10 BINH_YEN. Side effect: HINH_ANH bị shift -1 quote.",
  "v1.2 (TBD)": "..."
}
```

→ Tránh "magic config" — sau 3 tháng vẫn nhớ vì sao có keyword đó.

---

## 6.6. Bước 3 — Lựa chọn insight để thực thi

> **Trạng thái**: Đã build (`selection.py` + CLI `tim select`), 2026-05-08.
>
> **Mục đích**: chuyển insight từ trạng thái "đã được rank" (`3-lựa-chọn.md`) sang trạng thái "đã được con người chọn để làm" (`_master/content-pipeline.md`).

### 6.6.1 Triết lý — vì sao cần BƯỚC LỰA CHỌN THỦ CÔNG?

| Nếu để AI tự quyết toàn bộ | Nếu giữ bước thủ công của con người |
|---|---|
| Pipeline hết generic, mất bản sắc người sáng tạo | Bản sắc + judgement chiến lược nằm ở khâu chọn |
| Không có cơ hội anh "veto" angle không hợp định vị | Anh kiểm soát chiến lược dài hạn |
| Khó học từ post-mortem (AI generate → AI quên) | Có log explicit angle nào anh chọn → đối chiếu với view sau khi đăng |
| Tạo ảo giác "tool thay được người" | Tool **augment** chứ không **replace** judgement |

→ **Quy tắc số 1**: AI làm bước **Liệt kê + Sắp xếp** (rank theo demand, suggest opportunity), nhưng **bước Lựa chọn cuối cùng phải là người**. Đó là phần định vị thương hiệu, không có công thức.

### 6.6.2 Input

`3-lựa-chọn.md` (output của Bước 2 — `tim bank`) — đã được anh / nhân viên mở trong VS Code và **tick `[x]`** vào các angle muốn quay tuần này.

Format expected (do `insight_bank.py` sinh):
```markdown
- [x] `[SCORE 226]` `[Q001 TIEN_BAC_BINH_YEN]` `[FAQ_ANSWER]` "quote..." — @author (209 likes)
  - 💡 summary
  - 📂 nhóm: **Tiền bạc & bình yên** · 🎯 intent: `VENT`
```

Cả `[x]` lẫn `[X]` đều được parse. Khoảng trắng trong checkbox cũng OK (`[ x ]`).

### 6.6.3 Output

Tạo (hoặc append vào) 2 file ở `output/<niche>/_master/`:

| File | Mục đích |
|---|---|
| `content-pipeline.md` | Markdown table cho anh **browse + track status thủ công** (`todo` → `doing` → `done`/`skip`) |
| `selected_angles.json` | Full data **cho stage Bước 4** (production.py) đọc dễ — không phải parse markdown lần nữa |

`content-pipeline.md` schema:
```
| ID | Status | Score | Problem | Quote | Author | Source Run | Next Step |
```

- **Default status**: `todo`
- **Default next_step**: `generate_production_brief`
- **Source Run**: tên folder cha của `3-lựa-chọn.md` (vd `2026-05-06`)

### 6.6.4 Quy tắc append (idempotent)

- **Dedup theo full quote** (không phải ID, vì ID có thể trùng giữa 2 run khác niche/date)
- **Quote đã tồn tại** → giữ row cũ nguyên vẹn (status, next_step, mọi cell)
- **Quote mới** → thêm row với default status

→ Anh có thể **chạy `tim select` nhiều lần** mà không sợ mất dữ liệu đã edit tay.

→ Workflow: tuần này tick 5 cái → chạy → tuần sau tick thêm 5 cái khác → chạy lại → pipeline tự cộng dồn 10 cái, status các row cũ giữ nguyên.

### 6.6.5 Cross-reference với `1-liệt-kê.csv`

Markdown chỉ chứa quote **truncated 140 ký tự**. Để Bước 4 (production.py) sinh script chuẩn xác, cần **full quote + summary + video_url**.

→ `selection.py` tự động đọc `1-liệt-kê.csv` ở **sibling folder** của `3-lựa-chọn.md`:
- Match theo ID (Q001, P002, ...)
- Lấy: `quote` (full), `summary`, `video_url`, `bucket`, `replies`, `intent_label`

Nếu CSV không có (vd anh xóa rồi chỉ giữ md) → fallback dùng truncated quote, log warning.

### 6.6.6 Edge case: không tick gì

Nếu file 3-lựa-chọn.md không có `[x]` nào:
- ✅ KHÔNG crash
- ✅ KHÔNG tạo `_master/content-pipeline.md` rỗng
- ✅ In message rõ ràng:
  ```
  ℹ️ Chưa có insight nào được chọn.
  Hãy mở file ..., tick [x] các angle muốn quay, rồi chạy lại.
  ```

→ Tránh tạo file giả, gây nhiễu khi browse `_master/`.

### 6.6.7 CLI usage

```powershell
# Lệnh chính
tim select -i output/<niche>/<date>/3-lựa-chọn.md

# Override niche slug (nếu folder name khác slug muốn dùng)
tim select -i .../3-lựa-chọn.md --niche my-custom-slug

# Override output root (đặt _master ở chỗ khác)
tim select -i .../3-lựa-chọn.md --output-root /custom/path
```

### 6.6.8 Position trong pipeline

```
[Stage 1] scrape    → raw_comments.json
[Stage 2] classify  → classified.json
[Stage 3] report    → report.md       (generic insight summary)
[Stage 4] suggest   → brief.md        (AI suggest 10 angle — alternative path, dùng song song)
[Stage 5] bank      → 1-liệt-kê.csv + 2-sắp-xếp.md + 3-lựa-chọn.md
                      ─────────  Bước 1-3 của phương pháp 4-bước ─────────
[Stage 6] select    → _master/content-pipeline.md + _master/selected_angles.json  ← BƯỚC 3 (file này)
[Stage 7] production → _master/4-thực-thi/angle-XX.md (chưa làm)                  ← Bước 4
```

→ Mỗi stage tạo 1 file rõ ràng, có thể re-run độc lập, không lose data.

---

## 6.7. Bước 4 — Thực thi insight thành nội dung

> **Trạng thái**: Đã build (`production.py` + CLI `tim production`), 2026-05-08.
>
> **Mục đích**: chuyển insight đã chọn (output Bước 3) thành **file thực thi sản xuất 1-1** mà team content có thể cầm đi quay/viết ngay, không phải improvise.

### 6.7.1 Triết lý — vì sao tách production brief khỏi insight report?

| Insight report (`report.md`, `2-sắp-xếp.md`) | Production brief (`4-thực-thi/angle-XX.md`) |
|---|---|
| **Audience**: anh — strategic decision maker | **Audience**: creator/team content — tactical executor |
| **Optimize for**: scan nhanh, browse cross-niche | **Optimize for**: cầm 1 file, quay 1 video |
| **Granularity**: 1 file / nhiều insight | **Granularity**: 1 file / 1 insight / 1 video |
| **Lifecycle**: đọc 1 lần khi research | **Lifecycle**: dùng nhiều lần, post-mortem sau khi đăng |
| **Format**: tổng hợp tabular | **Format**: chi tiết step-by-step như recipe |

→ Tách 2 layer này tránh **"file insight 200 dòng nhưng không quay được"**. Production brief là **bản dịch** từ insight strategic sang script tactical.

### 6.7.2 Input / Output

**Input**:
- `output/<niche>/_master/selected_angles.json` (output Bước 3)
- `niche_configs/<slug>.json` (output Bước 1, để lấy persona + positioning + tone)

**Output**:
- Folder `output/<niche>/4-thực-thi/`
- Mỗi insight đã chọn → 1 file: `angle-{idx:02d}-{problem-lower-kebab}-{summary-slug}.md`
  - Vd: `angle-01-tien-bac-binh-yen-khong-tran-trong-khi-du.md`

### 6.7.3 Cấu trúc 1 file angle (10 sections)

```
1. Metadata           — Status, Score, Problem, Bucket, Intent, Author, Source quote, Video URL
2. Insight gốc        — Quote thật + Summary + Vấn đề chính + Cảm xúc + Mong muốn ẩn (từ niche_config)
3. Big idea           — 1 ý tưởng trung tâm
4. Hook options       — 5 variants: 2 cảm xúc · 1 myth-bust · 1 câu hỏi · 1 caption-style
5. Script 60s         — 5 đoạn: 0-3s hook / 3-15s pain / 15-35s insight / 35-50s action / 50-60s CTA
6. B-roll & Visual    — Cảnh quay chính, text overlay, bối cảnh, props, nhịp dựng
7. Caption            — 200-400 ký tự, có chiều sâu
8. CTA                — 3 lựa chọn: mềm / comment keyword / lưu-share
9. Checklist quay     — 5-8 việc cần check (ánh sáng, mic, biểu cảm)
10. Post-mortem       — Placeholder fill SAU khi đăng (view, like, comment, bài học)
```

### 6.7.4 Hai path generate

**Path A — Claude (default, recommended)**:
- Dùng Opus 4.7 với adaptive thinking + structured output (Pydantic schema)
- Inject `persona`, `positioning.tone`, `anti_pattern` từ niche config vào system prompt
- Inject `common_emotions`, `hidden_desires` của từng `main_problem` vào context
- Cost: ~$0.05-0.15/angle với Opus, ~$0.005/angle với Haiku

**Path B — Fallback rule-based (no API)**:
- Auto kích hoạt khi không có `ANTHROPIC_API_KEY` hoặc Claude lỗi
- Force enable bằng flag `--no-claude`
- Output đánh dấu rõ `⚠️ FALLBACK BRIEF` + `[FALLBACK]` ở các phần creative
- Quality thấp hơn, dùng để: (1) test pipeline, (2) emergency khi API down, (3) anh muốn tự viết tay

→ **Quy tắc**: production luôn chạy được, không bao giờ crash vì API.

### 6.7.5 Idempotency & re-generate

- **Default**: skip nếu file `angle-XX-*.md` đã tồn tại → re-run không tốn API
- **`--overwrite`**: force re-gen tất cả (vd: anh đổi prompt trong code, muốn refresh)
- **`--limit N`**: chỉ generate N angle đầu (cho test, tiết kiệm cost)

→ Workflow: lần đầu chạy hết, sau đó chỉ cần chạy lại với new angle vừa tick (Bước 3 append) → file cũ không bị ghi đè (post-mortem placeholder anh đã fill được giữ).

### 6.7.6 CLI usage

```powershell
# Default — dùng Claude (model từ .env)
tim production `
  -i output/<niche>/_master/selected_angles.json `
  --config niche_configs/<slug>.json

# Test rẻ — Haiku
tim production -i ... --config ... --model claude-haiku-4-5 --limit 2

# No API call — fallback template
tim production -i ... --config ... --no-claude

# Force re-gen
tim production -i ... --config ... --overwrite
```

### 6.7.7 Cách dùng file angle-XX.md

| Vai trò | Action |
|---|---|
| **Anh** (strategic) | Đọc Big idea + Hook → veto nếu off-brand → tick `Status: doing` trong `_master/content-pipeline.md` |
| **Creator** (tactical) | Đọc Script + B-roll + Checklist → quay video. Hook chọn 1 trong 5 (cảm thấy hợp tone hôm đó) |
| **Team copywriter** | Đọc Caption + CTA → đăng lên FB/IG cùng video TikTok |
| **Anh** (post-mortem) | Sau 7 ngày đăng → fill section 10 (view, comment, bài học) → input cho Bước 5 (tune) |

→ 1 file = 1 đơn vị sản xuất hoàn chỉnh. Không cần mở thêm file khác để hiểu phải làm gì.

### 6.7.8 Position trong pipeline (full)

```
[1] scrape    → raw_comments.json
[2] classify  → classified.json
[3] report    → report.md
[4] suggest   → brief.md (alternative path — AI tự pick 10 angle, không có user-vote)
[5] bank      → 1-liệt-kê.csv + 2-sắp-xếp.md + 3-lựa-chọn.md
                ─── Bước 1 + 2 của phương pháp 4-bước ───
[6] select    → _master/content-pipeline.md + _master/selected_angles.json
                ─── Bước 3 ───
[7] production → 4-thực-thi/angle-XX-*.md                                     ← BƯỚC 4 (file này)
                ─── Bước 4 (cuối) ───
```

→ MVP "Liệt kê → Sắp xếp → Lựa chọn → Thực thi" **đã hoàn thành đủ 4 bước**.

---

## 6.8. Bước 6 — Run end-to-end thật và chọn angle đầu tiên để test thị trường

> **Trạng thái**: Hoàn thành lần đầu 2026-05-09 với manual import 35 comment niche `kinh-doanh-27-45`.
>
> **Mục đích**: chạy đủ pipeline với data thật → có 5+ production brief → chọn 1 angle quay/post thật → đo thị trường.

### 6.8.1 Vì sao cần "run thật" thay vì chỉ test smoke

| Smoke test (Bước 2-4) | Run thật (Bước 6) |
|---|---|
| Chạy với data có sẵn (đã tune để đẹp) | Chạy với data fresh (chưa biết distribution) |
| Verify pipeline KỸ THUẬT | Verify pipeline VẬN HÀNH (lỗi env, encoding, rate limit) |
| Output dùng để debug | Output dùng để **quay video thật** |
| Đo: code có chạy không | Đo: brief có **production-ready** không |

→ Smoke test pass không nghĩa là run thật pass. Run thật mới lộ ra issue thật.

### 6.8.2 Checklist 7 bước (lần đầu chạy thật cho 1 niche)

```
[ ] 0. Chuẩn bị data 50-150 comment thật (TikTok scrape HOẶC manual import)
[ ] 1. Verify encoding UTF-8 đúng (không mojibake)
[ ] 2. Run import-comments / scrape → raw_comments.json
[ ] 3. Run classify (CHẮC CHẮN có ANTHROPIC_API_KEY + SSL OK)
[ ] 4. Run bank → đọc 2-sắp-xếp.md report distribution
[ ] 5. Tick [x] 5-10 angle trong 3-lựa-chọn.md (mix nhóm, gần offer)
[ ] 6. Run select → verify _master/content-pipeline.md có đủ row
[ ] 7. Run production → đọc 1 brief verify chất lượng → đề xuất 1 angle quay đầu
```

### 6.8.3 Bài học từ run lần đầu (2026-05-09 — kinh-doanh-27-45)

**Issue 1: Mojibake từ source data**
- Data anh paste lần đầu bị UTF-8 → latin-1 → bytes mất ký tự 3-byte VN ("muốn" → "mu�n")
- Recovery `latin-1 → utf-8 errors='replace'` chỉ cứu được ~80%
- **Fix**: anh paste trực tiếp clean text vào chat (không qua file trung gian) → encoding sạch
- **Lesson**: VERIFY ENCODING là bước đầu tiên TRƯỚC khi tốn API classify

**Issue 2: SSL Certificate Verify Failed (môi trường máy)**
- Classify FAIL với `[SSL: CERTIFICATE_VERIFY_FAILED]` dù TCP 443 reachable
- Root cause: cert store của Python / antivirus MITM / VPN — không phải bug code
- **Fix**: anh tự xử lý ở máy (update certifi / tắt antivirus / etc.) → retry pass
- **Lesson**: ENV issue ngoài tầm tool — code chỉ surface lỗi rõ, KHÔNG tự bypass SSL

**Issue 3: Sample size dưới ngưỡng**
- Spec recommend 50-150, actual 35 → distribution lệch hẳn 1 nhóm (45% `THUONG_HIEU_CA_NHAN`)
- 4/9 nhóm có 0 insight (không nhỡ data, đúng với dataset hẹp)
- **Lesson**: ≥50 cmt là min để distribution có signal đáng tin

**Issue 4: Engagement metadata thiếu**
- Manual import paste plain text → likes/replies/author = default (0/0/unknown)
- Demand score chỉ tính bucket_bonus + problem_priority_bonus, **mất engagement signal**
- Top 10 score chênh nhau ít (9-12 score)
- **Lesson**: nếu collect manual, **gắng giữ likes/replies trong CSV** (cột optional)

**Issue 5: Tick checkbox đa dạng format**
- Anh dùng cả `[x ]` (space sau) và `[ x]` (space trước) — regex của select đủ flexible đã handle
- 6/6 ticked parsed đúng

### 6.8.4 Cách chọn 1 angle quay đầu tiên

Khi có 5-10 production brief, đừng quay hết. **Chọn 1 cái duy nhất** dựa trên:

| Tiêu chí | Weight |
|---|---|
| **Big idea độc đáo nhất** (counter-narrative > generic) | 30% |
| **Hook punch nhất** (cụ thể > chung chung) | 20% |
| **Phù hợp tone brand** (peer-level, không guru) | 20% |
| **Diversity nhóm** (nếu 5/6 cùng nhóm → quay 1 cái khác nhóm để test tone bên ngoài comfort zone) | 15% |
| **Setup quay đơn giản** (props/setting tối thiểu) | 15% |

→ Quay 1 → đăng → đợi 7 ngày → fill section 10 (Post-mortem) → **học từ data thật** trước khi quay tiếp 4 cái còn lại.

### 6.8.5 Output run lần đầu

**Folder**: `output/kinh-doanh-27-45/`
- `2026-05-09__manual-import/` — raw, classified, 1-liệt-kê, 2-sắp-xếp, 3-lựa-chọn
- `_master/content-pipeline.md` — 6 angles tracked, status `todo`
- `_master/selected_angles.json` — full data cho production
- `4-thực-thi/angle-01..06-*.md` — 6 production brief (Claude Opus 4.7, ~$0.40-0.60 cost)

**Cost tổng** (lần đầu run thật):
- Apify: $0 (manual import không scrape)
- Claude classify (Haiku, 35 cmt): ~$0.01
- Claude production (Opus, 6 angle): ~$0.40-0.60
- **Tổng**: <$1 cho 1 lần run đủ pipeline

---

## 7. Roadmap mở rộng (sau MVP)

| Phase | Cải tiến |
|---|---|
| ~~v0.2~~ | ~~Module `selection.py` — parse `[x]` đã tick, output `_master/content-pipeline.md`~~ ✅ **Done 2026-05-08** |
| ~~v0.3~~ | ~~Module `production.py` — generate `4-thực-thi/angle-XX.md` cho mỗi angle pick~~ ✅ **Done 2026-05-08** |
| v0.4 | Aggregate cross-run: `tim bank --aggregate-niche <slug>` → cộng dồn nhiều ngày |
| v0.5 | Tune weights dựa trên post-mortem: angle nào viral → bonus lên |
| v0.6 | Generic SOP cho mọi ngành — viết lại file này thành `SOP_BUILD_INSIGHT.md` final |

---

## 8. Tài liệu liên quan

- [niche_configs/kinh-doanh-27-45.json](../niche_configs/kinh-doanh-27-45.json) — config v1 cho MVP
- [src/tiktok_insight_miner/insight_bank.py](../src/tiktok_insight_miner/insight_bank.py) — implementation
- [src/tiktok_insight_miner/cli.py](../src/tiktok_insight_miner/cli.py) — CLI subcommand `bank`
- `output/gia-tri-ban-than/_master/build_bank.py` — script ad-hoc gốc (đã thay bởi module mới, sẽ archive sau)

---

**Updated**: 2026-05-08 · v0.1 draft (Bước 2 của MVP)
