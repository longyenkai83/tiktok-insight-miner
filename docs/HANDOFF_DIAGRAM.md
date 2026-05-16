# SƠ ĐỒ HANDOFF — TikTok Insight Miner → Nhi Hien CoWork

> **Phiên bản**: v2 (2026-05-16) — chuyển sang **Pull model**: CoWork tự lấy, miner không đẩy
> **Mục đích**: chốt ranh giới trách nhiệm giữa 2 hệ thống. Miner = mỏ vàng insight (source of truth). CoWork = xưởng chế tác nội dung.
> **Nguyên tắc gốc**: mỗi folder có 1 owner duy nhất. Miner KHÔNG biết CoWork tồn tại. CoWork tự lấy khi cần (xem mục 10).

---

## 1. Sơ đồ tổng

```
┌──────────────────────────────────────────────────────────────────────┐
│  ĐẦU VÀO — 2 cách                                                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   [Cách 1] Link TikTok               [Cách 2] Comment nhập tay       │
│   - Paste 3-5 URL video              - Paste plain text vào CSV      │
│   - Tool tự scrape comment           - Hoặc gõ tay vào webapp        │
│                       │                              │               │
│                       └──────────────┬───────────────┘               │
│                                      ▼                               │
│                              raw_comments.json                       │
└──────────────────────────────────────┬───────────────────────────────┘
                                       │
                                       ▼
╔══════════════════════════════════════════════════════════════════════╗
║  TIKTOK INSIGHT MINER (D:\Projects\tiktok-insight-miner)             ║
║  Trách nhiệm: làm mỏ vàng insight thô                                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   Bước 1 — LIỆT KÊ                                                   ║
║   ─────────────────                                                  ║
║   Claude phân loại từng comment:                                     ║
║   - Bucket (pain/desire/question/objection)                          ║
║   - Intent (VENT, SEEK_HOWTO, ...)                                   ║
║   - Vào nhóm vấn đề nào (9-12 nhóm taxonomy)                         ║
║                       │                                              ║
║                       ▼                                              ║
║              1-liệt-kê.csv  (mọi insight, sort theo demand)          ║
║                       │                                              ║
║                       ▼                                              ║
║   Bước 2 — SẮP XẾP                                                   ║
║   ─────────────────                                                  ║
║   Tool tự group + chấm điểm demand:                                  ║
║   - Top cross-niche                                                  ║
║   - Distribution 9-12 nhóm                                           ║
║   - Section UNCLASSIFIED (để tune taxonomy)                          ║
║                       │                                              ║
║                       ▼                                              ║
║              2-sắp-xếp.md  (bức tranh tổng quan)                     ║
║                       │                                              ║
║                       ▼                                              ║
║   Bước 3 — LỰA CHỌN                                                  ║
║   ─────────────────                                                  ║
║   Anh / nhân viên tick [x] insight đáng dùng                         ║
║                       │                                              ║
║                       ▼                                              ║
║              3-lựa-chọn.md  + _master/selected_angles.json           ║
║                                                                      ║
╚══════════════════════════════════════╤═══════════════════════════════╝
                                       │
                                       │  HANDOFF (module mới: tim export-for-cowork)
                                       ▼
                          _master/insights-pack-for-cowork.md
                          ─────────────────────────────────────
                          Mỗi insight có:
                          - Quote audience full
                          - Insight 1 câu
                          - Lớp tự do (1-4)
                          - Mode đề xuất (A/B)
                          - Combo visual gợi ý
                          - Cảm xúc + mong muốn ẩn
                                       │
                                       │  ◄── SOURCE OF TRUTH (ở miner)
                                       │  ◄── CoWork tự PULL khi cần
                                       │      (Miner KHÔNG đẩy — xem mục 10)
                                       ▼
╔══════════════════════════════════════════════════════════════════════╗
║  NHI HIEN COWORK (D:\Nhi Hien CoWork)                                ║
║  Trách nhiệm: xưởng chế tác — viết bài, ảnh, reel                    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   Skill (sẽ build bên CoWork): pull-insights-from-miner              ║
║   - Đọc file miner → save inputs/<project>/ (v1, v2, v3 versioning)  ║
║   - Hoặc transform: 1 pack → N wiki page (1 insight = 1 page)        ║
║                       │                                              ║
║                       ▼                                              ║
║   ┌─────────────────────────────────────────────────────────┐        ║
║   │  CONTENT PROPOSAL PROTOCOL (v1.2)                       │        ║
║   │  Mỗi insight → Claude đẻ 3-5 concept                    │        ║
║   │  Chấm điểm 5 trục: Chạm/Viral/Sâu/Mới/Brand → /50       │        ║
║   └─────────────────────────────────────────────────────────┘        ║
║                       │                                              ║
║                       ▼                                              ║
║   Hiền chọn 1 concept                                                ║
║                       │                                              ║
║                       ▼                                              ║
║   ┌─────────────────────────────────────────────────────────┐        ║
║   │  FLOW VIẾT 7 BƯỚC (theo ABOUT ME/00_README.md)          │        ║
║   │                                                         │        ║
║   │  1. Đọc 02_about     → Hiền là ai, audience, 4 lớp      │        ║
║   │  2. Đọc 03_voice     → voice, xưng hô, niềm tin         │        ║
║   │  3. Quyết: Mode A/B · Lớp 1-4 · Lạnh/Ấm/Nóng            │        ║
║   │  4. Tra kho_anecdote → bê chi tiết (nếu cần)            │        ║
║   │  5. Áp 04_writing_rules → kỹ thuật câu chữ              │        ║
║   │  6. Viết draft                                          │        ║
║   │  7. Self-check 4 test trước khi đăng                    │        ║
║   └─────────────────────────────────────────────────────────┘        ║
║                       │                                              ║
║                       ▼                                              ║
║   Visual coherence check                                             ║
║   - Pick signature combo (1/2/3)                                     ║
║   - Pick setting / wardrobe / mô hình podcast (nếu reel)             ║
║                       │                                              ║
║                       ▼                                              ║
║   Save vào outputs/ → memory.md log                                  ║
║                       │                                              ║
╚══════════════════════════════════════╤═══════════════════════════════╝
                                       │
                                       ▼
                                  [Đăng FB/IG]
                                       │
                                       ▼
                          Comment audience phản hồi
                                       │
                          (sau N bài) feed lại làm input
                          cho Insight Miner — vòng lặp
```

---

## 2. Bảng "Ai làm gì ở đâu"

| Stage | Tool | File chính | Người làm |
|---|---|---|---|
| Input | TikTok scraper hoặc CSV import | `urls.txt` / `raw_comments.json` | Nhân viên (10 phút) |
| Bước 1 — Liệt kê | Miner: `tim classify` | `classified.json` → `1-liệt-kê.csv` | Tool tự, Claude API (~5-10p) |
| Bước 2 — Sắp xếp | Miner: `tim bank` | `2-sắp-xếp.md` | Tool tự (~2 giây) |
| Bước 3 — Lựa chọn | Anh / nhân viên tick | `3-lựa-chọn.md` → `selected_angles.json` | **Người** (15-30 phút) |
| Handoff (Bước 4 cuối của miner) | Miner: `tim export-for-cowork` | `_master/insights-pack-for-cowork.md` (source of truth) | Tool tự (~5 giây) |
| Pull insight (CoWork tự lấy) | CoWork skill `pull-insights-from-miner` (sẽ build) | Save vào `WORK AREAS/Marketing/<project>/inputs/insights-pack_v<n>.md` | Claude CoWork |
| Đề xuất concept | CoWork: Content Proposal Protocol | Bảng chấm điểm 5 trục | Claude CoWork |
| Hiền chọn | Hiền tick concept | (1 dòng) | **Hiền** (5-10 phút) |
| Viết bài | CoWork: 7 bước viết | `outputs/<bài>.md` | Claude CoWork |
| Ảnh / Reel | CoWork: Visual workflow | `outputs/<ảnh>.png` | Claude CoWork |
| Đăng | FB/IG (Hiền) | — | **Hiền** |

---

## 3. Ba điểm chuyển giao quan trọng

### Gate 1 — Comment → Pipeline (Input gate)

```
TikTok URL  ─┐
             ├──► raw_comments.json (schema chuẩn)
CSV manual  ─┘
```

Bất kể nguồn nào, **chuẩn hoá về 1 format** trước khi vào classify.

### Gate 2 — Insight → CoWork (Handoff gate, **PULL-based**)

```
selected_angles.json (raw schema cho miner)
         │
         │ + niche_config.json (mapping freedom_layer, emotion, hidden_desire)
         ▼
insights-pack-for-cowork.md  ◄── SOURCE OF TRUTH (chỉ ở miner)
         ▲
         │ CoWork tự PULL khi cần (skill bên CoWork)
         │ → save vào CoWork inputs/ với version v1, v2, v3...
```

Đây là **điểm tách 2 hệ thống**. File handoff là **source of truth** — Miner KHÔNG đẩy, CoWork chủ động lấy. **Vì sao pull model**: xem mục 10.

### Gate 3 — CoWork → Đăng (Output gate)

```
Claude CoWork viết draft
         │
         ▼
Hiền duyệt
         │
         ▼
Hiền đăng (không tự động — luôn người ấn đăng)
```

---

## 4. Quyền sửa file ở mỗi bên

| Folder | Miner đọc | Miner ghi | CoWork đọc | CoWork ghi |
|---|---|---|---|---|
| `Projects/tiktok-insight-miner/src/` | yes | yes | no | no |
| `Projects/tiktok-insight-miner/output/` | yes | yes | yes (read-only) | no |
| `Projects/tiktok-insight-miner/niche_configs/` | yes | yes | no | no |
| `Nhi Hien CoWork/ABOUT ME/` | no | no | yes | yes (memory.md only) |
| `Nhi Hien CoWork/WORK AREAS/Marketing/<project>/inputs/` | no | no | yes | yes (pull → write) |
| `Nhi Hien CoWork/WORK AREAS/Marketing/<project>/outputs/` | no | no | yes | yes |

**Quy tắc vàng**: mỗi folder có 1 owner duy nhất. Hệ thống còn lại chỉ "khách thăm".

---

## 5. Quy ước đặt tên & vị trí file

| Item | Convention | Ví dụ |
|---|---|---|
| File handoff bên Miner | `_master/insights-pack-for-cowork.md` | `output/kinh-doanh-27-45/_master/insights-pack-for-cowork.md` |
| File handoff bên CoWork (sau khi PULL, có versioning) | `WORK AREAS/Marketing/<project>/inputs/insights-pack_v<n>.md` | `WORK AREAS/Marketing/kinh-doanh-content-from-insights-project/inputs/insights-pack_v1.md` |
| Bài viết output CoWork | `WORK AREAS/Marketing/<project>/outputs/<insight-id>_<content-type>_v1.md` | `outputs/P003_LongFBPost_v1.md` |

→ Naming bên CoWork theo `project_content-type_v1.ext` (xem CoWork CLAUDE.md section NAMING CONVENTION).

---

## 6. Schema "Insight Pack" (Gate 2 — file handoff)

Mỗi insight trong pack gồm:

| Field | Nguồn | Vai trò |
|---|---|---|
| `id` | `selected_angles.json` | Trace ngược về quote gốc |
| `quote` (full) | `selected_angles.json` | Bê chi tiết thật vào bài |
| `summary` | `selected_angles.json` | Insight 1 câu |
| `problem_code` | `selected_angles.json` | Nhóm vấn đề (taxonomy miner) |
| `bucket`, `intent`, `opportunity` | `selected_angles.json` | Hint loại content |
| `score` | `selected_angles.json` | Demand priority |
| `freedom_layer` (1-4) | mapping trong `niche_config.json` | CoWork chấm Trục 5 (Brand match) |
| `suggested_mode` (A/B) | infer từ `bucket` + `opportunity` | Hint Framework vs Storytelling |
| `audience_temperature` (Lạnh/Ấm/Nóng) | default = Lạnh | Hint CTA strength |
| `combo_visual_hint` (1/2/3) | infer từ `freedom_layer` | Hint signature combo |
| `emotion_hints[]` | `niche_config.main_problems[].common_emotions` | Bê vào empathy section |
| `hidden_desires[]` | `niche_config.main_problems[].hidden_desires` | Đòn bẩy hook |
| `engagement` (likes, replies, author, video_url) | `selected_angles.json` | Social proof (nếu có) |

---

## 7. Mapping `problem_code → freedom_layer` (niche `kinh-doanh-27-45`)

→ **Mapping chi tiết đã chốt ở [MAPPING_FREEDOM_LAYER.md](MAPPING_FREEDOM_LAYER.md) v1 (2026-05-16)**.

Tóm tắt 9 nhóm:

| problem_code | Lớp chính | Lớp phụ | Mode | Combo |
|---|:---:|:---:|:---:|:---:|
| `TIEN_BAC_BINH_YEN` | 4 | 3 | B | 2 |
| `THUONG_HIEU_CA_NHAN` | 2 | — | A | 2 |
| `DONG_GOI_CHUYEN_MON` | 2 | — | A | 2 |
| `KINH_DOANH_KIET_SUC` | 2 | 3 | B | 2 |
| `GIA_TRI_BAN_THAN` | 3 | 2 | B | 1 |
| `BINH_YEN_CHUA_LANH` | 3 | 1 | B | 1 |
| `KY_LUAT_THOI_QUEN` | 3 | 1 | A | 1 |
| `GIA_DINH_GONG_GANH` | 1 | 2 | B | 3 |
| `HINH_ANH_PHONG_CACH` | 1 | 3 | A | 3 |
| `UNCLASSIFIED` | — | — | — | — |

---

## 8. Tài liệu liên quan

**Bên Miner**:
- [SOP_CLONE_NICHE.md](SOP_CLONE_NICHE.md) — **Playbook clone niche mới** (use khi onboard ngành/brand mới)
- [SOP_BUILD_INSIGHT_V1.md](SOP_BUILD_INSIGHT_V1.md) — Quy trình build insight (lý thuyết + 12 nguyên lý)
- [MAPPING_FREEDOM_LAYER.md](MAPPING_FREEDOM_LAYER.md) — Mapping cho client CoWork chị Hiền
- [SOP_BUILD_INSIGHT_DRAFT.md](SOP_BUILD_INSIGHT_DRAFT.md) — Chi tiết kỹ thuật từng module
- [../niche_configs/kinh-doanh-27-45.json](../niche_configs/kinh-doanh-27-45.json) — Niche config có taxonomy (template để clone)
- [../output/kinh-doanh-27-45/_master/selected_angles.json](../output/kinh-doanh-27-45/_master/selected_angles.json) — Input của handoff

**Bên CoWork** (đọc trước khi viết bài):
- `D:\Nhi Hien CoWork\ABOUT ME\00_README.md` — Flow viết 7 bước
- `D:\Nhi Hien CoWork\ABOUT ME\content-proposal-protocol.md` — Protocol chấm điểm 5 trục
- `D:\Nhi Hien CoWork\ABOUT ME\about-me.md` — Identity + 4 lớp tự do
- `D:\Nhi Hien CoWork\ABOUT ME\voice-profile.md` — Voice + xưng hô + niềm tin
- `D:\Nhi Hien CoWork\ABOUT ME\writing-rules.md` — Kỹ thuật viết câu chữ
- `D:\Nhi Hien CoWork\ABOUT ME\visual-identity.md` — DNA visual + 3 combo signature

---

## 9. Đường vòng feedback (sau khi đăng)

Sau N bài đăng, comment audience phản hồi → có thể feed lại vào Miner làm input mới:

```
Bài chị Hiền đăng → comment thật → scrape comment của chính bài chị Hiền
                                          │
                                          ▼
                            raw_comments.json (nguồn mới)
                                          │
                                          ▼
                          tim classify → tim bank → tim select
                                          │
                                          ▼
                          insight v2 (đã có context audience của chính chị)
```

→ Khác với run lần đầu (scrape comment KOL khác), lần này là **mining own audience** — insight chính xác hơn nhiều cho voice riêng.

---

## 10. Vì sao Pull thay vì Push

CoWork **tự lấy** insight từ miner, **không phải** miner đẩy sang CoWork. Đây là quyết định design chính.

### So sánh

| Tiêu chí | Push (miner đẩy) | **Pull (CoWork lấy)** ✓ |
|---|---|---|
| Source of truth | File ở 2 nơi, dễ out-of-sync | File 1 chỗ (miner), CoWork chỉ là "view" |
| Coupling | Miner phải biết path CoWork | Miner KHÔNG biết CoWork tồn tại |
| Versioning | Miner phải tự logic v1, v2... | CoWork tự quản version theo flow nó |
| CoWork rule "Never delete" | Có risk vi phạm | Không risk (miner không touch CoWork) |
| Scale brand thứ 2 | Mỗi brand = 1 path hardcode trong miner | Brand mới tự build pull skill, miner không đụng |
| Spam files | Mỗi miner run = 1 file mới ở CoWork | CoWork chỉ pull khi cần |
| Wiki transformation | Push raw dump phá structure wiki | Pull cho phép CoWork transform (1 pack → N wiki page + cross-link) |

### Implication

- **Miner**: chỉ làm tốt việc generate file `_master/insights-pack-for-cowork.md`. **Không biết CoWork tồn tại**.
- **CoWork**: build skill `pull-insights-from-miner` (bên CoWork session) — đọc file miner → save vào `inputs/` với version riêng → có thể tách thành wiki page.

### Trigger pull

- Hiền (hoặc anh) nói bên CoWork: *"lấy insight mới về"* → Claude CoWork chạy pull skill
- Không cần lịch tự động (cron) — pull theo nhu cầu
- CoWork có thể track "đã pull batch nào rồi" trong `memory.md` của project

### Risk nhỏ

| Risk | Mức | Fix |
|---|---|---|
| Path miner đổi (rename folder) → CoWork break | thấp | Document path trong `ABOUT ME/specialist-routing.md` CoWork |
| 2 lần pull cùng 1 file → duplicate trong CoWork | thấp | Pull skill dedup theo insight `id` |
| Miner chưa generate file mới mà CoWork pull | thấp | Pull skill check `timestamp` trong file header trước khi save |

---

**Updated**: 2026-05-16 · v2 (Pull model)
**Tinh thần**: 2 hệ thống, 2 trách nhiệm, 1 source of truth. Miner không biết CoWork tồn tại. CoWork tự lấy khi cần.
