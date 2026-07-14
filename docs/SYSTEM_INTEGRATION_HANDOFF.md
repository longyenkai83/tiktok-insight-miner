# TikTok Insight Miner — System Integration Handoff

> **Phiên bản tài liệu**: v1.0 (2026-06-14)
> **Mục đích**: cung cấp cho kỹ sư app content (CoWork hoặc app khác) toàn bộ context kỹ thuật để **tích hợp** với Insight Miner.
> **Đối tượng**: dev backend / fullstack, đã quen Python, REST API, Google Drive API.
> **Thời gian đọc**: 30-45 phút (đọc đủ section 1-7 là tích hợp được).

---

## Mục lục

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Kiến trúc tổng thể](#2-kiến-trúc-tổng-thể)
3. [Pipeline 6 stages](#3-pipeline-6-stages-chi-tiết)
4. [Data schemas](#4-data-schemas)
5. [Output files cho integration](#5-output-files-cho-integration)
6. [Google Drive F1 structure](#6-google-drive-f1-structure)
7. [5 integration patterns](#7-5-integration-patterns---chọn-1)
8. [Deployment & infrastructure](#8-deployment--infrastructure)
9. [Cost model](#9-cost-model)
10. [Limitations + roadmap](#10-limitations--roadmap)
11. [Contact + repo access](#11-contact--repo-access)

---

## 1. Tổng quan dự án

**Insight Miner** là CLI/webapp Python biến **comment audience** (TikTok, Facebook paste, YouTube paste, v.v.) thành **content brief có chiều sâu psychology** sẵn sàng cho người viết bài.

### Use case chính

Marketer (anh Tuấn) + coach (chị Hiền) + 3-5 nhân viên cần:
1. Hiểu audience nghĩ gì (pain, desire, question, objection từ comment thật)
2. Có **content angle** (hook + script outline + CTA) cho TikTok/Fanpage
3. Hand-off sang **app viết bài** (CoWork) — đây là chỗ **kỹ sư bên anh cần tích hợp**

### Vai trò trong pipeline content

```
[Insight Miner] ──insights pack──► [App content (CoWork)] ──bài viết──► [Đăng Fanpage/TikTok]
       ↑                                    ↑
   project này                        kỹ sư bạn build
```

Insight Miner làm **upstream** (research + planning). App content làm **downstream** (writing + publishing).

### Tech stack

- **Python 3.11+** (match/case, type hints mới)
- **Anthropic SDK** (Claude Opus 4.7 / Haiku 4.5 — classify + brief + strategy)
- **Apify Python client** (TikTok comment scraping)
- **Streamlit** (web UI nội bộ)
- **Pydantic v2** (data models + validation)
- **Google Drive API** (auto-upload output)
- **Railway** (hosting, $5-15/tháng Pro tier)
- **CSV log** (`usage_log.csv` — không database)

### URL production

- Webapp: `https://insight.lenguyenkhang.com` (Cloudflare DNS → Railway)
- Repo: `https://github.com/longyenkai83/tiktok-insight-miner` (private, anh Tuấn invite kỹ sư)
- Drive shared folder: `https://drive.google.com/drive/folders/1S27BXGisZTNZ63EgrINDxhMTVvmrue8W`

---

## 2. Kiến trúc tổng thể

```
┌──────────────────────────────────────────────────────────────────┐
│                     USER (anh + Hiền + nhân viên)                │
│                              ▼                                    │
│             Streamlit webapp (insight.lenguyenkhang.com)         │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    PIPELINE 6 STAGES                              │
│                                                                    │
│  [1] Scrape ────► Apify TikTok actor                             │
│  [2] Classify ──► Claude Haiku (7 buckets: pain/desire/...)      │
│  [3] Report ────► Markdown distribution + top quotes              │
│  [4] Brief ─────► Claude Opus (10 angles + psychology layer)     │
│  [5] Strategy ──► Claude Opus (Canvas + Synthesis B+C+D)         │
│  [6] Upload ────► Google Drive F1 structure (auto)               │
│                                                                    │
│  Optional: Stage C — CoWork Brief Pack (cherry-pick 3-5 angles)  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    OUTPUT — 3 layer storage                      │
│                                                                    │
│  Layer 1 — Railway Volume (/app/output/<niche>/<date>/<user>/)   │
│  Layer 2 — Google Drive (insights-packs/runs/<niche>/<date>/...) │
│  Layer 3 — Webapp history (CSV log, restore download)            │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│          ⭐ APP CONTENT (CoWork) — kỹ sư bạn build               │
│                                                                    │
│  Pull từ Drive → Process → Generate bài viết → Đăng              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Pipeline 6 stages chi tiết

### Stage 1 — Scrape

| Field | Value |
|---|---|
| **Input** | TikTok URLs (list) hoặc raw comment paste (FB/YT manual) |
| **Tool** | Apify actor `clockworks/tiktok-comments-scraper` |
| **Output** | `raw_comments.json` (list of comment dicts) |
| **Cost** | ~$0.001/comment (Apify) |
| **Latency** | ~30-60s for 100 comments |
| **File** | `tiktok_insight_miner/scraper.py` |

### Stage 2 — Classify

| Field | Value |
|---|---|
| **Input** | `raw_comments.json` |
| **Model** | `claude-haiku-4-5` (cheap, fast) |
| **Output** | `classified.json` — mỗi comment có bucket (pain/desire/question/objection/praise/mention/other) + summary + confidence |
| **Batch** | 20 comments/API call (configurable) |
| **Cost** | ~$0.0003/comment |
| **Latency** | ~10s/batch |
| **File** | `tiktok_insight_miner/classifier.py` |

### Stage 3 — Report

| Field | Value |
|---|---|
| **Input** | `classified.json` |
| **Output** | `report.md` — distribution table + top 10 quotes per bucket + common themes |
| **Cost** | $0 (pure formatting) |
| **File** | `tiktok_insight_miner/reporter.py` |

### Stage 4 — Brief (heart of system)

| Field | Value |
|---|---|
| **Input** | `classified.json` + niche persona + meta_pains |
| **Model** | `claude-opus-4-7` với adaptive thinking |
| **Output** | `brief.md` + `brief.json` — 10 content angles |
| **Each angle** | title, hook, script outline, CTA, target_insight (quote gốc), target_likes, **psychology_rationale**, **cluster**, **primary_model** (mental model), **vn_concept**, **fb_caption_opening** |
| **Cost** | ~$0.02/run |
| **Latency** | ~30-60s |
| **File** | `tiktok_insight_miner/suggester.py` |
| **Framework** | xem [docs/psychology/insight-mining-framework.md](psychology/insight-mining-framework.md) |

### Stage 5 — Strategy Analysis (Canvas + Synthesis)

| Field | Value |
|---|---|
| **Input** | `classified.json` + `brief.md` + niche persona |
| **Model** | `claude-opus-4-7` với adaptive thinking, raw markdown output (không Pydantic) |
| **Output** | `phan-tich-toan-dien.md` chứa: |
| | **PHẦN B** — Customer Profile Canvas mini (Pains/Gains/Jobs × 4 bước Liệt kê→Sắp xếp→Lựa chọn→Thực thi) |
| | **PHẦN C** — Self-evaluation brief vừa generate (chấm điểm 10 angles) |
| | **PHẦN D** — 3 phát hiện chiến lược + 3 product offer candidates + content roadmap 30 ngày + cờ đỏ |
| **Cost** | ~$0.07/run |
| **Latency** | ~30-60s |
| **File** | `tiktok_insight_miner/strategy_analyst.py` |

### Stage 6 — Auto upload Drive (F1 structure)

| Field | Value |
|---|---|
| **Input** | 3 files: `report.md`, `brief.md`, `phan-tich-toan-dien.md` |
| **Method** | Google Drive API (service account) |
| **Output path** | `insights-packs/runs/<niche-slug>/<YYYY-MM-DD>/<HH-MM>_<user>/{report,brief,phan-tich-toan-dien}.md` |
| **Cost** | $0 (Drive API free) |
| **File** | `tiktok_insight_miner/cowork_exporter.py` |

### Stage C (optional) — CoWork Brief Pack

Sau brief, user có thể cherry-pick 3-5 angles + voice profile → render 1 file `cowork-brief-pack_HHMM.md` (~5KB) tinh gọn cho app content.

| Field | Value |
|---|---|
| **Input** | `brief.md` + voice profile (profiles/chi-hien/) |
| **Output** | `cowork-brief-pack_HHMM.md` |
| **Cost** | $0 (pure parse + render) |
| **File** | `tiktok_insight_miner/cowork_pack.py` |
| **Content** | METADATA / VOICE PROFILE / 3-5 ANGLES / VOCAB GROUNDING / ANTI-PATTERN CHECKLIST / OUTPUT TEMPLATE |

---

## 4. Data schemas

### 4.1 Comment (raw)

```python
class Comment(BaseModel):
    id: str
    text: str
    author: str = ""
    likes: int = 0
    reply_count: int = 0
    created_at: str = ""
    video_url: str = ""
    raw: dict[str, Any] = {}  # Raw từ Apify, giữ debug
```

### 4.2 ClassifiedComment (after Stage 2)

```python
Bucket = Literal["pain", "desire", "question", "objection", "praise", "mention", "other"]

class ClassifiedComment(BaseModel):
    comment: Comment
    bucket: Bucket
    summary: str          # 1 câu tiếng Việt, max 15 từ
    confidence: float     # 0.0-1.0
```

### 4.3 ContentAngle (after Stage 4) — **kỹ sư đọc kỹ schema này**

```python
AngleType = Literal[
    "pain_solution", "desire_fulfillment", "question_answer",
    "myth_busting", "social_proof", "how_to",
    "emotional_positioning", "series_announcement",
]

AudienceCluster = Literal[
    "entrepreneurial_despair",       # làm chủ kiệt sức
    "procrastination_trap",          # đợi đủ điều kiện
    "viral_no_convert",              # có view không ra đơn
    "authentic_trend_fatigue",       # biết phải authentic nhưng không biết kể
    "macro_despair",                 # bất lực kinh tế/xã hội
    "cross_cluster",                 # tension / UGC / pattern frequency
]

VnCulturalConcept = Literal[
    "via_culture",                   # xin vía, trộm vía
    "face_the_dien",                 # thể diện
    "collectivism_tag",              # tag bạn, "ai cũng như mình"
    "hierarchy_anh_chi_em",          # đại từ phù hợp age segment
]

class ContentAngle(BaseModel):
    # Core fields
    title: str                       # 5-15 từ tiếng Việt
    angle_type: AngleType
    target_insight: str              # Quote nguyên văn từ comment gốc
    target_likes: int                # Engagement signal
    hook: str                        # 1-2 câu, max 150 ký tự, CHỨA cụm nguyên văn
    script_outline: list[str]        # 3-5 beat
    cta: str                         # Call-to-action cụ thể
    confidence: float                # 0.0-1.0

    # Psychology layer (v0.3+)
    cluster: AudienceCluster | None
    primary_model: str | None        # vd "peak_end", "loss_aversion", "sunk_cost_fallacy"
    vn_concept: VnCulturalConcept | None
    psychology_rationale: str | None # 1-2 dòng giải thích

    # Fanpage layer (v0.4+)
    fb_caption_opening: str | None   # 3-5 dòng câu mồi (quan trọng hơn hook 3s)
```

### 4.4 Output JSON example (brief.json)

```json
{
  "angles": [
    {
      "title": "Bà Thu Nhi Eatclean - case mẫu cho ai nghĩ 'đời mình bình thường lắm'",
      "angle_type": "social_proof",
      "target_insight": "bà Thu Nhi Eatclean á mn, xung quanh bả toàn gia đình ănuống...",
      "target_likes": 1287,
      "hook": "'Bà Thu Nhi Eatclean, xung quanh toàn gia đình, bác Chiến hàng xóm mà chuyện kể mãi không hết' — đây là proof.",
      "script_outline": [
        "0:00-0:08 Hook đọc nguyên văn comment 1287 likes",
        "0:09-0:25 Social proof: 1287 người đồng tình",
        "..."
      ],
      "cta": "Tag 1 'bác Chiến hàng xóm' trong đời bạn",
      "confidence": 0.93,
      "cluster": "authentic_trend_fatigue",
      "primary_model": "social_proof",
      "vn_concept": "collectivism_tag",
      "psychology_rationale": "Praise comment 1287 likes → social proof. Cluster authentic_trend_fatigue: không lặp 'hãy chân thực'...",
      "fb_caption_opening": "Tuần này có một chị viết dưới video của mình..."
    }
  ]
}
```

---

## 5. Output files cho integration

Mỗi pipeline run sinh ra ở `output/<niche>/<date>/<user>/`:

| File | Size | Mục đích | Format |
|---|:---:|---|---|
| `raw_comments.json` | 100KB-2MB | Raw scrape data (debug) | JSON array of Comment |
| `classified.json` | 50KB-500KB | Comment đã phân loại | JSON array of ClassifiedComment |
| `report.md` | 10-30KB | Distribution + top quotes | Markdown |
| **`brief.md`** | **10-20KB** | **10 angles dạng người đọc** | **Markdown** |
| **`brief.json`** | **5-15KB** | **10 angles dạng app parse** | **JSON ContentAngleBrief** |
| **`phan-tich-toan-dien.md`** | **15-25KB** | **Canvas + Synthesis** | **Markdown** |
| `cowork-brief-pack_HHMM.md` | 3-5KB | Tinh lọc 3-5 angles (optional) | Markdown |

→ Kỹ sư bạn **chủ yếu cần 3 files**: `brief.json` (machine-readable), `phan-tich-toan-dien.md` (strategic context), `cowork-brief-pack_*.md` (nếu có).

---

## 6. Google Drive F1 structure

Sau mỗi pipeline run, 3 files (report + brief + strategy) tự upload vào Drive theo F1 structure:

```
tiktok-miner-shared/                       ← Drive shared root
└── insights-packs/                         ← env INSIGHTS_PACK_DRIVE_FOLDER_ID
    ├── kinh-doanh-27-45/                   ← legacy: insights-pack_v<N>.md (manual select)
    │   ├── insights-pack_v1.md
    │   └── insights-pack_v2.md
    │
    └── runs/                                ← NEW: auto-upload mỗi run
        └── <niche-slug>/                    ← vd "kinh-doanh-27-45"
            └── <YYYY-MM-DD>/                ← vd "2026-06-14"
                ├── 14-30_tuan/              ← <HH-MM>_<user>
                │   ├── report.md
                │   ├── brief.md
                │   └── phan-tich-toan-dien.md
                ├── 18-20_nv_minh/
                │   ├── report.md
                │   ├── brief.md
                │   └── phan-tich-toan-dien.md
                └── ...
```

**Drive folder root ID**: `1S27BXGisZTNZ63EgrINDxhMTVvmrue8W` (anh Tuấn share quyền Editor cho service account `insight-miner-uploader@insight-miner-prod.iam.gserviceaccount.com`).

---

## 7. 5 Integration Patterns — chọn 1

Tuỳ requirement của app content, kỹ sư chọn 1 trong 5 cách tích hợp:

### Pattern A — Pull file từ Drive (đơn giản nhất, recommend)

**Workflow**:
1. App content có **service account riêng** (hoặc dùng chung) với quyền Reader trên folder `insights-packs/runs/`
2. Cron job mỗi 10 phút: list folder mới, download 3 files mới
3. Parse `brief.json` → match với schema ContentAngle → store DB
4. UI app cho user chọn angle → trigger writing flow

**Pros**: Zero coupling với Insight Miner. Insight Miner down vẫn không ảnh hưởng app content (file đã ở Drive).
**Cons**: Latency 10 phút trung bình (polling).

**Code skeleton**:
```python
from googleapiclient.discovery import build
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file('sa.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly'])
service = build('drive', 'v3', credentials=creds)

# List runs folder
results = service.files().list(
    q="'<runs-folder-id>' in parents and trashed=false",
    fields="files(id, name, modifiedTime)",
    orderBy="modifiedTime desc",
    pageSize=10,
).execute()

# Download brief.json từ run mới nhất
brief_id = ...  # navigate vào folder run
file_content = service.files().get_media(fileId=brief_id).execute()
brief_data = json.loads(file_content)
```

### Pattern B — Pull insights pack từ Drive (manual selection workflow)

Khác Pattern A: dùng folder `insights-packs/<niche>/insights-pack_v<N>.md` thay vì `runs/`. File này đã được user **manual cherry-pick** qua webapp (tick checkbox) → cleaner, ít noise.

**Pros**: Data đã được con người chọn (chất lượng cao hơn).
**Cons**: User phải tự click trên webapp Insight Miner trước → workflow chậm.

### Pattern C — Webhook khi pipeline xong (cần build)

Insight Miner gửi HTTP POST đến URL của app content khi pipeline xong:

```json
{
  "event": "pipeline.completed",
  "run_id": "2026-06-14_14-30_tuan_kinh-doanh-27-45",
  "niche": "kinh-doanh-27-45",
  "user": "tuan",
  "drive_folder_url": "https://drive.google.com/drive/folders/...",
  "files": {
    "brief.json": "https://drive.google.com/file/d/.../view",
    "report.md": "...",
    "phan-tich-toan-dien.md": "..."
  },
  "stats": {
    "num_comments": 401,
    "num_angles": 10,
    "cost_usd": 0.22
  }
}
```

**Pros**: Real-time, không cần polling.
**Cons**: Cần **anh Tuấn build webhook side** (chưa có, em estimate 2-3h dev).

### Pattern D — REST API trigger pipeline từ app content (cần build)

App content gọi API endpoint của Insight Miner để **trigger** pipeline:

```http
POST https://insight.lenguyenkhang.com/api/pipeline/run
Authorization: Bearer <token>
Content-Type: application/json

{
  "niche": "kinh-doanh-27-45",
  "urls": ["https://www.tiktok.com/@user/video/123"],
  "max_comments": 100,
  "with_brief": true,
  "with_strategy": true,
  "callback_url": "https://app-content.com/webhook"
}
```

**Pros**: 2 chiều — app content control pipeline.
**Cons**: Cần build API + auth + async job queue (effort 1-2 ngày).

### Pattern E — Shared niche persona / voice profile (read-only)

App content **đọc** file persona + voice profile từ Insight Miner repo để dùng chung:

| File | Mục đích |
|---|---|
| `niche_configs/<slug>.json` | Niche persona (age, life_stage, core_tensions, anti-pattern) |
| `niche_configs/<slug>_meta_pains.md` | 5 hidden pains (cho audience trưởng thành) |
| `profiles/chi-hien/voice_profile.md` | Voice profile của writer |
| `profiles/chi-hien/write_rules.md` | Write rules nội bộ |

→ App content render bài viết dùng cùng voice profile → consistency.

**Implementation**: GitHub raw URL hoặc clone repo:
```bash
curl https://raw.githubusercontent.com/longyenkai83/tiktok-insight-miner/main/niche_configs/kinh-doanh-27-45.json
```

---

## 8. Deployment & infrastructure

### 8.1 Hosting

- **Platform**: Railway (PaaS) — auto-deploy từ GitHub
- **Plan**: Pro $5/tháng (compute $5-10/tháng usage)
- **Container**: Python 3.11-slim Docker
- **Volume**: Mounted `/app/output` (1GB free, persist across rebuild)
- **Region**: US East

### 8.2 Environment variables required

| Var | Mô tả | Bắt buộc |
|---|---|:---:|
| `APIFY_TOKEN` | Apify API token (TikTok scrape) | ✅ |
| `ANTHROPIC_API_KEY` | Anthropic Claude API | ✅ |
| `ANTHROPIC_MODEL` | Default model (vd `claude-haiku-4-5` cho classify) | — |
| `SUGGESTER_MODEL` | Override model cho suggester (default `claude-opus-4-7`) | — |
| `STRATEGY_MODEL` | Override model cho strategy (default `claude-opus-4-7`) | — |
| `CLASSIFY_BATCH_SIZE` | Comments/API call (default 20) | — |
| `DEFAULT_OUTPUT_DIR` | Output folder (default `./output`) | — |
| `WEBAPP_PASSWORD` | Password gate (để trống = open) | — |
| `MAX_RUNS_PER_USER_PER_DAY` | Quota (default 20) | — |
| `INSIGHTS_PACK_DRIVE_FOLDER_ID` | Drive root folder ID | (chỉ khi auto-upload) |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | Service account JSON (single line) | (chỉ khi auto-upload) |
| `INSIGHTS_PACK_DRIVE_DIR` | Local sync path (chỉ dev local) | — |

### 8.3 Pipeline flow (chi tiết deployment)

```
User push code → GitHub → Railway webhook → Docker build (3-5 min)
                                              ↓
                                       Rebuild container
                                              ↓
                                       Mount volume + start streamlit
                                              ↓
                                       webapp.lenguyenkhang.com active
```

Mỗi pipeline run (4-8 phút):
1. Streamlit nhận request → `run_pipeline()` chạy sync trong session thread
2. Files save vào `/app/output/<niche>/<date>/<user>/`
3. Auto upload Drive (best-effort, không fail nếu Drive down)
4. Log row vào `/app/output/usage_log.csv`
5. Show download buttons trong UI

---

## 9. Cost model

### Per-run cost (100 comments, default settings)

| Stage | Cost USD | Note |
|---|:---:|---|
| Stage 1 — Scrape | $0.10 | $0.001/comment × 100 |
| Stage 2 — Classify (Haiku) | $0.03 | $0.0003/comment × 100 |
| Stage 3 — Report | $0 | Pure formatting |
| Stage 4 — Brief (Opus 4.7) | $0.02 | Single API call ~10K tokens |
| Stage 5 — Strategy (Opus 4.7) | $0.07 | Single API call ~15K tokens |
| Stage 6 — Upload Drive | $0 | Drive API free |
| **TỔNG / run** | **~$0.22** | |

### Monthly cost projection

| Pattern dùng | Runs/tháng | Cost/tháng |
|---|:---:|:---:|
| Chị Hiền - 1 run/tuần | 4 | $0.88 |
| Anh Tuấn test nhiều | 20 | $4.40 |
| 5 nhân viên × 5 runs | 100 | $22 |
| Scale lớn 1000 runs | 1000 | $220 |

Cộng Railway hosting ($5-15) + scaling.

### Khi nào cost tăng nhanh?

- `max_comments` từ 100 → 500: Stage 1+2 cost × 5
- Bật cả Strategy: +$0.07/run (32% extra)
- Niche persona injection (current default): cùng cost, không đổi

---

## 10. Limitations + roadmap

### Limitations hiện tại

| Limitation | Mức ảnh hưởng | Workaround |
|---|:---:|---|
| Chỉ scrape TikTok (paste manual cho FB/YT/IG) | 🟠 | Anh Tuấn đang plan Fanpage Graph API integration |
| 1 niche/run (không multi-niche) | 🟡 | User chạy nhiều run riêng |
| Single user, no auth | 🟠 | WEBAPP_PASSWORD shared password |
| No real-time stream (sync request) | 🟡 | User đợi 4-8 phút |
| No webhook (chưa có) | 🟠 | Polling Drive mỗi 10 phút |
| Stage 5 Strategy chỉ raw markdown, không structured | 🟡 | Kỹ sư parse heading H1/H2 thủ công |
| Voice profile chỉ chị Hiền (hardcode) | 🟡 | Multi-profile system planned |

### Roadmap (anh Tuấn confirm khi nào)

| Feature | Effort | Khi nào |
|---|:---:|---|
| Fanpage scrape qua Meta Graph API | 3-4h | Q3 2026 (anh Tuấn quyết) |
| Webhook khi pipeline xong | 2-3h | Khi app content ready |
| REST API trigger pipeline | 1-2 ngày | Khi cần |
| Multi-niche per run | 3-5h | Sau khi 3 niche stable |
| Auth + multi-tenant | 1-2 tuần | Khi scale > 20 users |
| Real-time stream events | 1 tuần | Khi UX cần |

---

## 11. Contact + repo access

### Liên hệ

- **Project owner**: anh Tuấn (lenguyentuan1983@gmail.com)
- **AI assistant** built system: Claude (qua Claude Code IDE)
- **Repo**: https://github.com/longyenkai83/tiktok-insight-miner (private)
- **Drive shared folder**: https://drive.google.com/drive/folders/1S27BXGisZTNZ63EgrINDxhMTVvmrue8W

### Cách kỹ sư bạn lấy access

1. Anh Tuấn invite GitHub username vào repo (Read access đủ — chỉ cần đọc schema + flow)
2. Anh Tuấn share folder Drive với email Google account của bạn (Reader)
3. Anh Tuấn tạo service account riêng cho app content bạn (hoặc dùng chung — quyết định security)

### Docs bổ sung trong repo

| File | Mục đích |
|---|---|
| [CLAUDE.md](../CLAUDE.md) | Project overview (cho AI assistant) |
| [docs/DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) | Cách deploy Railway từ đầu |
| [docs/OPERATION_MANUAL.md](OPERATION_MANUAL.md) | Vận hành hàng ngày |
| [docs/psychology/insight-mining-framework.md](psychology/insight-mining-framework.md) | Framework v1.1 chi tiết (5 cluster + 12 mental models + 4 VN cultural concepts) |
| [docs/psychology/customer-profile-canvas-2745.md](psychology/customer-profile-canvas-2745.md) | Customer Profile Canvas mini cho niche kinh-doanh-27-45 |
| [docs/psychology/sample-brief-fanpage-2745-v1.md](psychology/sample-brief-fanpage-2745-v1.md) | Sample brief human-grade (so sánh chất lượng) |
| [niche_configs/kinh-doanh-27-45.json](../niche_configs/kinh-doanh-27-45.json) | Niche persona config (9 main_problems + persona + positioning) |
| [niche_configs/kinh-doanh-27-45_meta_pains.md](../niche_configs/kinh-doanh-27-45_meta_pains.md) | 5 hidden pains audience không nói công khai |
| [profiles/chi-hien/voice_profile.md](../profiles/chi-hien/voice_profile.md) | Voice profile chị Hiền (12K chars) |
| [profiles/chi-hien/write_rules.md](../profiles/chi-hien/write_rules.md) | Write rules chị Hiền (19K chars) |

---

## 📋 Action items cho kỹ sư bạn

Sau khi đọc xong file này, kỹ sư bạn nên:

1. **Yêu cầu access** (anh Tuấn cấp): GitHub repo Read + Drive folder Reader + service account email
2. **Đọc kỹ Section 4 + 5** (data schemas + output files) — để biết parse gì
3. **Chọn Integration Pattern** (Section 7) — recommend **Pattern A** (pull Drive)
4. **Setup test**: pull 1 brief.json từ Drive, parse, verify match ContentAngle schema
5. **Báo cáo anh Tuấn**: estimate effort + ngày start integration
6. **Sync với anh Tuấn** khi cần thay đổi schema (vd thêm field, đổi cluster names) → tránh break compat

---

## Versioning tài liệu

- **v1.0 (2026-06-14)**: Initial — xuất handoff đầy đủ cho kỹ sư app content
- Anh Tuấn update file này khi có thay đổi lớn (schema, pipeline stages, integration patterns)

---

**End of document. Câu hỏi gì liên hệ anh Tuấn (lenguyentuan1983@gmail.com).**
