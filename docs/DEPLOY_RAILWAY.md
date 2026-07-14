# Deploy lên Railway — Playbook

> **Phiên bản**: v2 (2026-05-17) — đã verify real deploy + add lessons learned + Volume persist + UI Bước 2-4
> **Mục đích**: deploy Insight Miner lên Railway cloud 24/7 — không cần bật PC
> **Estimated time**: 2-4 giờ first time, ~1 giờ nếu đã quen
> **Cost**: $5-15/tháng Railway + $5-15 API (Apify + Anthropic) = ~$10-30/tháng (~250-750k VNĐ)

---

## 1. Tổng quan kiến trúc sau deploy

```
TRƯỚC (local PC)                       SAU (Railway cloud)
─────────────────                      ───────────────────
[Anh bật PC]                           [Railway 24/7]
  ↓                                       ↓
start-tunnel-named.bat                  Auto deploy từ GitHub
  ↓                                       ↓
Streamlit local:8501                    Streamlit container
  ↓                                       ↓
Cloudflare Tunnel                       Railway domain
  ↓                                       ↓
insight.lenguyenkhang.com               insight.lenguyenkhang.com
                                        (DNS Cloudflare → Railway)
  ↓                                       ↓
Output → G:\My Drive\... sync           Output → Drive API upload
  ↓                                       ↓
CoWork pull from Drive cloud            CoWork pull from Drive cloud
                                        (KHÔNG đổi)
```

→ Sau deploy: PC anh tắt → tunnel tắt → web vẫn live 24/7 trên Railway.

---

## 2. Checklist các bước (7 bước)

### Bước 1 — Anh setup Google Cloud + Service Account (30 phút)

Vì server cloud không có Drive Desktop local, phải dùng Drive API để upload insight pack.

1. Vào https://console.cloud.google.com/
2. Tạo project mới: vd `insight-miner-prod`
3. Vào **APIs & Services → Library** → tìm "Google Drive API" → Enable
4. Vào **IAM & Admin → Service Accounts** → Create Service Account:
   - Name: `insight-miner-uploader`
   - Role: skip (không cần role project-level)
   - Click Create
5. Vào service account vừa tạo → tab **Keys** → Add Key → Create New Key → JSON → Download
6. File JSON tên dạng `insight-miner-prod-xxxxx.json` — **giữ kỹ, anh sẽ paste content vào Railway env var**
7. Mở JSON, copy email `client_email` (dạng `insight-miner-uploader@insight-miner-prod.iam.gserviceaccount.com`)
8. Vào Drive web → folder `tiktok-miner-shared` → Share → add email service account ở Bước 7 → quyền **Editor**

→ Verify: service account đã access được folder Drive.

### Bước 2 — Anh push code lên GitHub (15 phút)

1. Vào https://github.com → tạo repo mới private: `tiktok-insight-miner`
2. Tại local PC:
   ```powershell
   cd D:\Projects\tiktok-insight-miner
   git init
   git add .
   git commit -m "Initial commit — production ready"
   git branch -M main
   git remote add origin https://github.com/<username>/tiktok-insight-miner.git
   git push -u origin main
   ```
3. Verify trên GitHub web: code đã lên, **KHÔNG có `.env`** (đã gitignore)

⚠️ **Quan trọng**: KIỂM TRA `.env` không bị push lên public. Mở repo GitHub → search `APIFY_TOKEN` → nếu thấy = anh đã leak key, phải revoke ngay.

### Bước 3 — Anh tạo Railway project (10 phút)

1. Vào https://railway.com → New Project → Deploy from GitHub repo
2. Chọn repo `tiktok-insight-miner` vừa push
3. Railway sẽ tự detect: Python + `railway.toml` em đã tạo → start command đúng
4. Build xong (3-5 phút) → Railway gen 1 URL tạm dạng `xxx.up.railway.app`

### Bước 4 — Anh set environment variables trên Railway (15 phút)

Vào Railway project → tab **Variables** → add các biến sau:

| Variable | Value | Note |
|---|---|---|
| `APIFY_TOKEN` | (copy từ `.env` local) | API key Apify |
| `ANTHROPIC_API_KEY` | (copy từ `.env` local) | API key Claude |
| `ANTHROPIC_MODEL` | `claude-opus-4-7` | hoặc claude-haiku-4-5 cho rẻ |
| `CLASSIFY_BATCH_SIZE` | `20` | optional |
| `WEBAPP_PASSWORD` | (đặt password mới) | **BẮT BUỘC** — URL public ai cũng vào được |
| `MAX_RUNS_PER_USER_PER_DAY` | `20` | optional |
| `INSIGHTS_PACK_DRIVE_FOLDER_ID` | `1S27BXGisZTNZ63EgrINDxhMTVvmrue8W` | Drive folder ID `insights-packs` |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | (paste full JSON content từ file download Bước 1) | Multi-line OK |

→ Click **Deploy** lại sau khi set env vars.

### Bước 5 — Test URL tạm (5 phút)

1. Mở URL Railway tạm (vd `xxx.up.railway.app`)
2. Nhập password
3. Thử chạy 1 pipeline ngắn (paste 5 comment)
4. Verify: pipeline chạy → tạo file insight → upload Drive API → CoWork pull được

⚠️ Nếu lỗi: check Railway **Logs** tab → debug.

### Bước 6 — Connect custom domain (10 phút)

1. Railway project → **Settings → Networking → Generate Domain** (đã có URL tạm)
2. Click **Custom Domain** → thêm `insight.lenguyenkhang.com`
3. Railway chỉ DNS record (vd CNAME `insight` → `xxx.up.railway.app`)
4. Vào Cloudflare DNS của domain `lenguyenkhang.com`:
   - **Xoá** record cũ pointing tunnel
   - **Thêm** CNAME record:
     - Name: `insight`
     - Target: (giá trị Railway cho)
     - Proxy: **DNS only** (KHÔNG bật orange cloud — Railway tự handle SSL)
5. Đợi 5-15 phút cho DNS propagate
6. Test https://insight.lenguyenkhang.com → load Railway

### Bước 7 — Tắt tunnel + monitor (5 phút)

1. Tắt 2 cửa sổ `start-tunnel-named.bat` trên PC anh
2. PC anh có thể tắt hoàn toàn
3. Monitor Railway 24-48 giờ:
   - Logs có lỗi không
   - Latency từ user thật
   - Cost ước tính

→ Sau 2 ngày stable: anh đi du lịch thoải mái.

---

## 3. Cost dự kiến

| Service | Plan | Cost/tháng |
|---|---|---|
| Railway Hobby | $5 trial credit, sau đó pay-as-you-go | **~$5-10** (tùy traffic) |
| Apify scrape | Pay per usage | **~$5-15** (tùy số run) |
| Anthropic Claude | Pay per token | **~$3-10** |
| Google Drive API | Free quota | **$0** |
| Domain | (anh đã có) | $0 |
| **Tổng** | | **~$13-35** |

→ Khoảng 300-800k VNĐ/tháng. So với PC bật 24/7 (điện ~300k) + thời gian anh → đáng đầu tư.

---

## 4. Vấn đề tiềm năng + Fix

| Vấn đề | Fix |
|---|---|
| Build fail "ModuleNotFoundError: streamlit" | Check `pyproject.toml` có `streamlit>=1.30.0` trong `dependencies`. Đẩy lại. |
| App start fail "Address already in use" | Railway tự inject `$PORT` — check `railway.toml` start command đúng `--server.port $PORT` |
| File output mất sau restart | **Bình thường** — Railway ephemeral storage. Snapshot Drive là cách lưu vĩnh viễn. |
| `usage_log.csv` reset mỗi lần redeploy | Bình thường. Nếu cần persistent → migrate sang Postgres free Railway hoặc Supabase. |
| Drive API "Permission denied" | Check service account email đã share vào folder Drive với role Editor |
| URL DNS chưa point | Đợi 15-30 phút, hoặc dùng https://dnschecker.org check propagation |
| Cloudflare proxy bật → SSL error | Tắt orange cloud trong Cloudflare DNS, để **DNS only** |
| Pipeline timeout sau 5 phút | Railway có 60 phút timeout — đủ. Nếu vẫn timeout, check Apify quota |

---

## 5. Sau khi deploy stable — Cleanup

Sau 1 tuần ổn định, anh có thể:

1. **Tắt Cloudflare Tunnel** hoàn toàn — xoá Named Tunnel ở Cloudflare Zero Trust dashboard
2. **Xoá file** `cloudflared.exe`, `config.yml`, `start-tunnel*.bat` (không cần nữa)
3. **Update doc**: `MVP_WORKFLOW.md`, `README.md` chỉ rõ URL Railway
4. **Backup** GitHub repo + Drive folder định kỳ
5. **Cân nhắc**: setup Railway Pro plan ($20/tháng) nếu scale lên 50+ user — hiệu năng tốt hơn

---

## 6. Roll-back nếu cần

Nếu Railway có vấn đề lớn (down, lỗi không fix được), em có thể:

1. **Quick rollback**: Cloudflare DNS đổi lại CNAME pointing về tunnel cũ
2. **Bật lại tunnel**: chạy `start-tunnel-named.bat` trên PC anh (nếu còn)
3. **Switch traffic**: trong 5 phút user dùng được lại

→ **Không xoá script tunnel + cloudflared.exe trong 2 tuần đầu** — phòng emergency.

---

## 7. Tài liệu liên quan

- [SETUP_GDRIVE_WORKFLOW.md](SETUP_GDRIVE_WORKFLOW.md) — Setup Drive (Local + API mode)
- [SOP_CLONE_NICHE.md](SOP_CLONE_NICHE.md) — Clone niche mới
- [HANDOFF_DIAGRAM.md](HANDOFF_DIAGRAM.md) — Sơ đồ flow miner → CoWork
- [../.env.example](../.env.example) — Template env vars (có sẵn 2 mode snapshot)
- [../railway.toml](../railway.toml) — Railway deploy config
- [../pyproject.toml](../pyproject.toml) — Dependencies (đã add streamlit + Drive API libs)

---

## 8. Checklist tổng (copy-paste khi deploy)

```markdown
## Deploy Insight Miner lên Railway

### Bước 1 — Google Cloud (30 phút)
- [ ] Tạo Google Cloud project
- [ ] Enable Google Drive API
- [ ] Tạo Service Account 'insight-miner-uploader'
- [ ] Download JSON key
- [ ] Copy email service account
- [ ] Share Drive folder 'tiktok-miner-shared' với email service account (Editor)

### Bước 2 — GitHub (15 phút)
- [ ] Tạo repo private 'tiktok-insight-miner'
- [ ] git init + commit + push
- [ ] Verify .env KHÔNG bị push

### Bước 3 — Railway project (10 phút)
- [ ] New Project from GitHub repo
- [ ] Verify Railway detect Python + railway.toml
- [ ] Build success, có URL tạm

### Bước 4 — Env vars trên Railway (15 phút)
- [ ] APIFY_TOKEN
- [ ] ANTHROPIC_API_KEY
- [ ] ANTHROPIC_MODEL
- [ ] WEBAPP_PASSWORD (BẮT BUỘC!)
- [ ] MAX_RUNS_PER_USER_PER_DAY
- [ ] INSIGHTS_PACK_DRIVE_FOLDER_ID
- [ ] GDRIVE_SERVICE_ACCOUNT_JSON (paste full JSON)
- [ ] Redeploy

### Bước 5 — Test (5 phút)
- [ ] Mở URL Railway tạm
- [ ] Login với password
- [ ] Chạy pipeline ngắn (paste 5 comment)
- [ ] Verify Drive API upload (file mới trên Drive cloud)

### Bước 6 — Custom domain (10 phút)
- [ ] Railway: add custom domain insight.lenguyenkhang.com
- [ ] Cloudflare: thêm CNAME, DNS only
- [ ] Đợi DNS propagate
- [ ] Test https://insight.lenguyenkhang.com

### Bước 7 — Cutover (5 phút)
- [ ] Tắt start-tunnel-named.bat trên PC
- [ ] Monitor Railway logs 24-48h
- [ ] Báo nhân viên + chị Hiền URL mới
```

---

## 9. ⚠️ Lessons Learned từ deploy thực tế (16-17/05/2026)

Đây là gotchas em đã trải qua khi deploy lần đầu — anh đọc trước để né.

### 9.1 Railway Builder PHẢI set Dockerfile (không Nixpacks/Railpack)

**Vấn đề**: Railway default builder là Railpack/Nixpacks. Sẽ chạy `pip install .` → fail với error `'src' does not exist or is not a directory` (vì pyproject.toml có src-layout).

**Fix**:
1. Tạo `Dockerfile` ở root (đã có sẵn trong repo)
2. `railway.toml`: `[build] builder = "DOCKERFILE"`
3. Trong Railway Dashboard → Settings → Build → đổi Builder thành **Dockerfile**
4. Nếu vẫn không work → delete service + create lại từ đầu (Railway tự detect Dockerfile)

### 9.2 Convert sang flat layout (move src/tiktok_insight_miner → root)

**Vấn đề**: src-layout (`src/tiktok_insight_miner/`) fail khi build wheel trong sandbox Railway.

**Fix**: 
- Move folder → `tiktok_insight_miner/` ở root
- `pyproject.toml`: `[tool.setuptools] packages = ["tiktok_insight_miner"]`
- KHÔNG cần `where = ["src"]` nữa

### 9.3 Docker CMD phải dùng exec form với sh -c wrapper

**Vấn đề**: `CMD streamlit run ... --server.port ${PORT:-8501}` (shell form) hoặc `CMD ["streamlit", ...]` (exec form) đều fail vì `$PORT` không expand → Streamlit báo `'$PORT' is not a valid integer`.

**Fix**: 
```dockerfile
CMD ["/bin/sh", "-c", "streamlit run webapp.py --server.address 0.0.0.0 --server.port ${PORT:-8501} --server.headless true"]
```

Exec form gọi shell explicit → `${PORT:-8501}` expand đúng.

### 9.4 KHÔNG dùng startCommand trong railway.toml

**Vấn đề**: `startCommand` trong railway.toml chạy exec form, KHÔNG shell expand → `$PORT` literal.

**Fix**: Bỏ `startCommand` ra khỏi `[deploy]` section trong railway.toml. Để Dockerfile CMD run.

### 9.5 Procfile cũng phải sh -c wrapper (nếu có)

**Fix**:
```
web: /bin/sh -c "streamlit run webapp.py --server.address 0.0.0.0 --server.port ${PORT:-8501} ..."
```

### 9.6 CSV encoding utf-8-sig (BOM) match

**Vấn đề**: `log_run` ghi utf-8-sig (BOM cho Excel), nhưng `render_sidebar` + `get_user_runs_24h` đọc utf-8 (không BOM) → BOM bytes ghép vào key đầu → `KeyError: 'timestamp'`.

**Fix**: Đọc cũng dùng `encoding="utf-8-sig"`.

### 9.7 Streamlit session_state để persist result

**Vấn đề**: Click checkbox = Streamlit re-run từ đầu. Nếu `result` chỉ là local var → mất → Section 3+4 biến mất.

**Fix**: Save `result` vào `st.session_state["pipeline_result"]` sau pipeline xong. Render Section 3+4 từ session_state.

### 9.8 Cloudflare proxy phải TẮT cho Railway custom domain

**Vấn đề**: Bật Cloudflare proxy (orange cloud) → Railway không verify SSL được → "Too many redirects" hoặc handshake failed.

**Fix**: Trong Cloudflare DNS, CNAME `insight` đổi proxy status sang **DNS only** (cloud xám). Bỏ qua cảnh báo "Proxying is required" — đó chỉ là suggestion.

### 9.9 GitHub Repo not found → install Railway GitHub App

**Vấn đề**: Railway authenticated qua OAuth nhưng KHÔNG install GitHub App → không pull được private repo.

**Fix**: Vào `https://github.com/settings/installations` → Configure Railway App → chọn repo `tiktok-insight-miner`. Hoặc tạm thời make repo Public.

### 9.10 PowerShell + git workflow gotchas

- **cd vào đúng folder**: Mỗi PowerShell mới mở ở `C:\Users\...` → phải `cd D:\Projects\tiktok-insight-miner`
- **KHÔNG paste token vào PowerShell prompt thường** — chỉ paste khi git prompt password
- **GitHub Personal Access Token** dễ leak qua screenshot → revoke ngay nếu lộ

### 9.11 Railway Volume cho persistent storage

**Vấn đề**: Container restart → mất tất cả file trong `/app/output/` (ephemeral storage).

**Fix**: 
1. Project canvas → + Create → Volume → attach service `web` → mount `/app/output`
2. Move `usage_log.csv` vào `OUTPUT_ROOT` (sửa code) — để cùng volume cover
3. Insight pack lên Drive là backup tin cậy thứ 2 (Drive cloud không phụ thuộc Railway)

---

## 10. Section 4: Upload Drive UI (Bước 2-4)

Sau deploy ban đầu, em add tính năng web cho phép user tick + upload Drive trực tiếp.

**Trước**: Web chỉ làm Bước 1 (scrape + classify + report). Bước 2-4 phải chạy CLI local.

**Sau** (commit `d573b16`): Web tự động:
- Sau pipeline xong → tự chạy `tim bank` (sắp xếp)
- Hiển thị candidates grouped theo nhóm vấn đề (collapsible expander)
- User tick các insight muốn handoff
- Bấm "📤 Upload sang Google Drive" → tự chạy `tim select` + `tim export-for-cowork` → upload Drive API

→ Full automation. KHÔNG cần PC anh chạy CLI.

**Yêu cầu**:
- Niche có sẵn config (`niche_configs/<slug>.json`) — chỉ niche `kinh-doanh-27-45` có sẵn
- Env vars `INSIGHTS_PACK_DRIVE_FOLDER_ID` + `GDRIVE_SERVICE_ACCOUNT_JSON` set trên Railway

---

## 11. Tài liệu liên quan thêm

- [OPERATION_MANUAL.md](OPERATION_MANUAL.md) — Vận hành hằng ngày sau deploy

---

**Updated**: 2026-05-17 · v2 (đã verify deploy thực tế + 11 gotchas + UI Bước 2-4 + Volume)
**Tinh thần**: Deploy 1 lần, chạy mãi. Anh đi du lịch không cần bật PC. Đã trải qua → đóng gói lại cho lần sau né.
