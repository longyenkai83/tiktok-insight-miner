# V2 SOURCE-OF-TRUTH — bắt buộc trước khi sửa code

Mọi coding agent **bắt buộc đọc đủ mười một file từ [00-PROJECT-OS.md](docs/v2/00-PROJECT-OS.md) đến [10-STRATEGYZER-FOUNDATIONS.md](docs/v2/10-STRATEGYZER-FOUNDATIONS.md) trước khi sửa code, đặc biệt trước architecture/product-logic changes**. Đọc [PROJECT-STATE](docs/v2/08-PROJECT-STATE.md) để kiểm tra phase và [DECISIONS](docs/v2/07-DECISIONS.md) để kiểm tra quyết định; không suy diễn quyền triển khai từ audit hoặc roadmap.

Strategyzer foundations là explicit architecture dependency. **If implementation conflicts with accepted decisions or Strategyzer foundations: STOP and report.** Không âm thầm diễn giải lại quyết định/nguyên tắc để hợp thức hóa implementation.

Current Phase = Phase 2 — Customer Context. Status = IMPLEMENTED — PENDING ARCHITECT REVIEW. Next Phase = DO NOT START. Chủ dự án cho phép qua DEC-032. Chỉ per-comment context từ signals.json, không clustering/content/product generation/router. Giữ Phase 1 và default legacy compatibility. **Do not start Phase 3. Wait for architecture review.**

Kiến trúc V2 lấy `docs/v2` làm chuẩn. Nội dung dự án V1 bên dưới chỉ mô tả **CURRENT STATE** và quy tắc bảo trì hiện hữu; không được dùng làm kiến trúc đích hoặc ghi đè quyết định V2. Nếu thiếu tài liệu hoặc có mâu thuẫn, nêu rõ để review trước khi code. Test xanh hoặc push code không tự mở phase kế tiếp.

---

# TikTok Insight Miner — Project context

## 🎯 Mục tiêu

CLI Python quét comment TikTok → phân loại bằng Claude → xuất báo cáo markdown insight (pain / desire / question / objection / praise).

Use case: research thị trường, viral hook discovery, content angle mining từ comment thật của audience.

## 🧱 Kiến trúc

```
TikTok video URLs
    │
    ▼
[scraper.py] ──Apify (clockworks/tiktok-comments-scraper)── raw_comments.json
    │
    ▼
[classifier.py] ──Claude (Haiku, batch + structured outputs)── classified.json
    │
    ├──► [reporter.py] ──aggregate + top-quote ranking── report.md
    │
    └──► [suggester.py] ──Claude (Opus 4.7, adaptive thinking)── brief.md
                                                                    (+ brief.json)
```

4 stage độc lập, có thể chạy riêng (`scrape` → `classify` → `report` / `suggest`) hoặc gộp (`run [--with-angles]`).

## 📦 Stack

- **Python 3.11+** (dùng `match/case`, type hints mới)
- **Apify Python client** — scrape TikTok comments
- **Anthropic SDK** — classify comments với prompt caching + structured outputs (`messages.parse()` + Pydantic)
- **Pydantic v2** — data models
- **python-dotenv** — config từ `.env`
- **argparse** — CLI (giữ deps tối thiểu, không thêm typer/click)

## 🗂 Layout

```
tiktok-insight-miner/
├── CLAUDE.md                      # file này
├── README.md                      # user-facing docs
├── pyproject.toml                 # deps + entry point
├── .env.example                   # template (APIFY_TOKEN, ANTHROPIC_API_KEY)
├── .gitignore
├── src/tiktok_insight_miner/
│   ├── __init__.py
│   ├── __main__.py                # python -m tiktok_insight_miner
│   ├── cli.py                     # argparse subcommands
│   ├── models.py                  # Pydantic: Comment, ClassifiedComment, Bucket
│   ├── scraper.py                 # Apify integration
│   ├── classifier.py              # Claude classification (batched + cached)
│   └── reporter.py                # Markdown report generation
└── output/                        # gitignored, mặc định lưu kết quả ở đây
```

## 🪣 Bucket schema

| Bucket | Định nghĩa |
|---|---|
| `pain` | Vấn đề, frustration, complaint |
| `desire` | Mong muốn, aspiration, "giá mà có..." |
| `question` | Câu hỏi cần giải đáp |
| `objection` | Phản đối, lý do KHÔNG mua/dùng |
| `praise` | Khen ngợi, positive feedback |
| `mention` | Tag/mention người khác (@username) — social signal sharing, không content insight |
| `other` | Spam, emoji-only, off-topic, không phải mention |

**Changelog:**
- v0.6.0 (2026-09-11): **Luồng 2 — fanpage của mình**. [fb_page_source.py](tiktok_insight_miner/fb_page_source.py) gọi Graph API (`/{page}/feed` → `/{post}/comments?filter=stream`; `/{page}/conversations` → `/{conv}/messages`, đối chiếu docs Meta v26.0) → `raw_comments.json` khớp schema scraper, nhãn `raw.platform` = `facebook_page` / `facebook_inbox`. **Ẩn danh cứng**: không lưu tên (author = hash), che SĐT/email/link trước khi ghi đĩa và trước khi gửi Claude, bỏ tin do Page tự gửi, inbox không giữ raw. CLI `tim fb-fetch [--with-inbox] [--probe]` (`--probe` in response thật để đối chiếu field). [reporter.py](tiktok_insight_miner/reporter.py): khi ≥2 nguồn → thêm bảng "Theo nguồn" + nhãn nguồn trên quote; 1 nguồn giữ nguyên format cũ. `tim suggest` thêm `--niche`. Agent: job có `"source"`, thư mục tách `__agent-tiktok/` và `__agent-fb/`, khâu 5 gộp classified → `so-sanh-nguon.md`. Env mới: `FB_PAGE_TOKEN`, `FB_PAGE_ID`. Thêm 20 test (tổng 90). **Chưa chạy với token thật** — anh điền token rồi `tim fb-fetch --probe` trước.
- v0.5.0 (2026-09-11): **Agent định kỳ** — nối liền 5 khâu, chạy tự động không cần người canh. (1) `tim select --auto-top N` ([selection.py](tiktok_insight_miner/selection.py)): máy tự chọn N angle điểm cao nhất khi không ai tick `[x]` — gỡ chỗ đứt duy nhất của dây chuyền. Angle tick tay LUÔN được giữ, không bao giờ bị cắt; mỗi angle mang nhãn `selected_by` = manual/auto. (2) [weekly_agent.py](weekly_agent.py) + [agent_config.json](agent_config.json): chạy liền run → bank → select → production cho nhiều job, một job hỏng không làm chết job khác, có `--dry-run` xem trước không tốn tiền. (3) Khâu 0 lấy từ khoá: rút từ kho `keyword-research-dataforseo/_all_keywords_merged_v2.csv` (3.529 từ khoá), xoay vòng qua `keyword-state.json` nên tuần sau không quét trùng. (4) [start-weekly-agent.bat](start-weekly-agent.bat) cho Windows Task Scheduler. Hướng dẫn: [docs/AGENT_DINH_KY.md](docs/AGENT_DINH_KY.md). Thêm 9 test cho auto-top (tổng 70).
- v0.4.0 (2026-07-21): **Discover stage** — bỏ khâu tìm video thủ công. Hàm `discover_tiktok_videos()` ([scraper.py](src/tiktok_insight_miner/scraper.py)) dùng actor `clockworks/tiktok-scraper` (KHÁC comments-scraper): nhập keyword / hashtag / @profile → tự lấy list video, lọc `min_views`/`min_comments`/`newest_days`, sort theo view. CLI: subcommand `tim discover -o urls.txt` + flag `--keyword/--profile/--hashtag` cho `tim run` (stage 0: discover→scrape→classify→report). Webapp: tab "🔎 Tìm video" đổ URL sang tab Scrape TikTok. Fields đã verify từ raw response (webVideoUrl, playCount, commentCount, createTimeISO, authorMeta.name) — không bịa.
- v0.3.2 (2026-05-04): **Bug fixes**: (1) Classifier fail-fast trên `AuthenticationError` (401) — trước silent skip làm webapp log "success" với 0 comments. (2) Classifier fail-fast nếu 3 batches liên tiếp fail hoặc 0 results — tránh empty downstream crash. (3) `usage_log.csv` ghi với `utf-8-sig` (BOM) để Excel mở đúng tiếng Việt (fix mojibake `TuÃ¢Ìn`).
- v0.3.1 (2026-05-04): **Cloudflare Tunnel** cho nhân viên remote. `start-tunnel.bat` mở Streamlit local + cloudflared quick tunnel song song → public URL `*.trycloudflare.com`. Free, không cần domain, không cần Cloudflare account. Yêu cầu download `cloudflared.exe` 1 lần. **BẮT BUỘC** set `WEBAPP_PASSWORD` trong `.env` trước khi expose public.
- v0.3.0 (2026-05-04): **Web UI nội bộ** ([webapp.py](webapp.py), Streamlit). Cho 5+ nhân viên dùng qua LAN. Features: password gate (optional), per-user quota (default 20 runs/24h), usage logging vào `usage_log.csv`, inline preview report+brief, download buttons. Launch: double-click `start-webapp.bat` hoặc `streamlit run webapp.py`. Cài deps: `pip install -e ".[webapp]"`.
- v0.2.1 (2026-05-03): **Niche init helper** — `tim init <niche>` scaffold folder `output/<niche>/<date>/` với `urls.txt` + `notes.md` template, auto-update `_index.md` master, in lệnh `run` sẵn để copy-paste. Convention: `output/<niche-slug>/<YYYY-MM-DD>/{raw,classified,report,brief,notes}`.
- v0.2.0 (2026-05-03): **Content angle suggester** ([suggester.py](src/tiktok_insight_miner/suggester.py)) — sau classify, dùng Claude Opus 4.7 generate 10 content angle (hook + script outline + CTA) ground vào top pain/desire/question/objection. Output `brief.md` + `brief.json`. CLI: subcommand `suggest`, hoặc `run --with-angles`.
- v0.1.1 (2026-05-03): Thêm bucket `mention` để tách @tag (sharing signal) khỏi `other`. Phát hiện qua run kegel niche: 32% rơi vào `other` chủ yếu là @tag.

Mỗi comment được gán đúng 1 bucket + summary 1 câu (tiếng Việt) + confidence 0.0-1.0.

## 🔑 Config (.env)

```bash
APIFY_TOKEN=apify_api_xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Optional
ANTHROPIC_MODEL=claude-opus-4-7        # mặc định; có thể đổi sang claude-haiku-4-5 cho cost
CLASSIFY_BATCH_SIZE=20                 # comments per API call
DEFAULT_OUTPUT_DIR=./output
```

## 💡 Quyết định kỹ thuật

1. **Prompt caching**: System prompt (định nghĩa bucket + format) được cache với `cache_control: ephemeral` → batch sau hit cache, giảm 90% cost cho phần system.
2. **Structured outputs**: Dùng `client.messages.parse()` với Pydantic schema → đảm bảo response đúng format, không cần regex parse.
3. **Batch classification**: Gửi N comment/lần (default 20) thay vì 1-by-1 → tiết kiệm token và thời gian.
4. **Giữ raw data**: Mỗi stage save JSON intermediate → có thể re-run stage sau mà không scrape lại.
5. **Model default**: `claude-opus-4-7` (theo global rule). User muốn cheap thì set `ANTHROPIC_MODEL=claude-haiku-4-5` trong `.env` — classification là task đơn giản, Haiku chạy ổn.

## 🚀 CLI usage

```bash
# Scrape + classify + report (all-in-one)
tim run --urls https://www.tiktok.com/@user/video/123 --max-comments 200

# Hoặc từng stage
tim scrape --urls-file urls.txt --max-comments 200 -o output/raw.json
tim classify -i output/raw.json -o output/classified.json
tim report -i output/classified.json -o output/report.md
```

## ✋ Rule khi code project này

1. **Không bịa Apify field names** — actor `clockworks/tiktok-comments-scraper` có schema riêng, đọc raw response trước khi map. Dùng `.get()` resilient.
2. **Không hard-code prompt cố định cho domain cụ thể** — prompt phải general đủ để áp dụng cho mọi niche. User có thể tùy chỉnh `--system-prompt` nếu cần.
3. **Verify cache hit** sau request đầu — log `usage.cache_read_input_tokens` để confirm prompt caching đang work.
4. **Đừng silently truncate** — nếu comment quá dài, log warning rồi truncate có ghi rõ, không nuốt im lặng.
