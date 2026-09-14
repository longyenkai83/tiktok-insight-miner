"""Agent định kỳ — chạy liền mạch từ tìm từ khoá đến file kịch bản, không cần người canh.

Chuỗi 5 khâu cho mỗi job trong agent_config.json:

    0. keyword    lấy từ khoá (từ config, hoặc rút từ kho keyword-research-dataforseo)
    1. run        tìm video → quét comment → phân loại → báo cáo [→ brief angle]
    2. bank       dựng 3 file liệt kê / sắp xếp / lựa chọn
    3. select     tự tick N angle điểm cao nhất  (--auto-top)
    4. production sinh file kịch bản đầy đủ trong 4-thực-thi/   ← KHÂU VIẾT BÀI
    5. so sánh    (nếu có cả job TikTok lẫn job fanpage cùng niche) → so-sanh-nguon.md

Hai nguồn, chọn bằng "source" trong job:
    "tiktok"        thị trường rộng — khâu 1 là `run` (đã gộp sẵn discover→scrape→classify→report)
    "facebook_page" fanpage của mình — khâu 1 nối tay: fb-fetch → classify → report → suggest

Cách dùng:
    python weekly_agent.py --dry-run     # xem sẽ chạy gì, KHÔNG tốn tiền
    python weekly_agent.py               # chạy thật, mọi job đang bật
    python weekly_agent.py --job <tên>   # chỉ chạy 1 job

Mỗi lần chạy để lại trong output/_agent-logs/:
    <ngày>__<job>.log     toàn bộ log thô, để truy vết khi hỏng
    <ngày>-tom-tat.md     bản tóm tắt ngắn, cho anh và cho agent Claude đọc
    keyword-state.json    nhớ tuần trước đã quét từ khoá nào, tuần này quét cái khác

Nguyên tắc: một job hỏng KHÔNG làm chết các job còn lại. Một khâu hỏng thì dừng
job đó tại chỗ và ghi rõ hỏng ở khâu nào, không chạy tiếp các khâu sau.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "agent_config.json"
OUTPUT_ROOT = PROJECT_ROOT / "output"
LOG_ROOT = OUTPUT_ROOT / "_agent-logs"
NICHE_CONFIG_DIR = PROJECT_ROOT / "niche_configs"
KEYWORD_STATE_PATH = LOG_ROOT / "keyword-state.json"

# Tên ngắn của nguồn, dùng đặt tên thư mục
SOURCE_SHORT = {"tiktok": "tiktok", "facebook_page": "fb"}

# Force UTF-8 trên Windows (console mặc định cp1252 không in được tiếng Việt)
if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


# --- Đọc cấu hình ---

def load_config(path: Path) -> dict:
    if not path.exists():
        sys.exit(
            f"❌ Không thấy file cấu hình: {path}\n"
            f"   Tạo agent_config.json trước (xem mẫu trong repo)."
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"❌ agent_config.json sai cú pháp JSON: {e}")


def merge_defaults(job: dict, defaults: dict) -> dict:
    """Ghép defaults vào job. Khoá bắt đầu bằng '_' là ghi chú, bỏ qua."""
    merged = {k: v for k, v in defaults.items() if not k.startswith("_")}
    merged.update({k: v for k, v in job.items() if not k.startswith("_")})
    return merged


# --- Khâu 0: nguồn từ khoá ---

def load_keyword_state() -> dict:
    """Nhớ job nào đã quét từ khoá nào, để tuần sau quét cái khác."""
    if not KEYWORD_STATE_PATH.exists():
        return {}
    try:
        return json.loads(KEYWORD_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"⚠️  keyword-state.json hỏng — coi như chưa quét gì, bắt đầu lại vòng.")
        return {}


def save_keyword_state(state: dict) -> None:
    KEYWORD_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    KEYWORD_STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def doc_kho_tu_khoa(nguon: dict) -> list[dict]:
    """Đọc file CSV từ khoá (kho keyword-research-dataforseo) → list dict đã lọc.

    CSV phải có cột `keyword`. Các cột `vol`, `kd`, `intent`, `source` là tuỳ chọn:
    thiếu cột nào thì bộ lọc tương ứng bị bỏ qua, không làm hỏng cả job.
    """
    path = Path(nguon["file"])
    if not path.exists():
        raise FileNotFoundError(f"Không thấy file từ khoá: {path}")

    min_vol = int(nguon.get("min_vol", 0))
    max_kd = nguon.get("max_kd")
    loc_intent = [s.lower() for s in (nguon.get("intent") or [])]
    loc_source = (nguon.get("source_contains") or "").lower()

    ket_qua: list[dict] = []
    # utf-8-sig: file xuất từ Excel thường có BOM ở đầu
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            kw = (row.get("keyword") or "").strip()
            if not kw:
                continue

            try:
                vol = int(float(row.get("vol") or 0))
            except ValueError:
                vol = 0
            if vol < min_vol:
                continue

            if max_kd is not None:
                try:
                    kd = float(row.get("kd") or 0)
                except ValueError:
                    kd = 0.0
                if kd > float(max_kd):
                    continue

            if loc_intent and (row.get("intent") or "").strip().lower() not in loc_intent:
                continue

            if loc_source and loc_source not in (row.get("source") or "").lower():
                continue

            ket_qua.append({"keyword": kw, "vol": vol})

    # Volume cao trước; cùng volume thì theo bảng chữ cái cho kết quả ổn định
    ket_qua.sort(key=lambda r: (-r["vol"], r["keyword"]))
    return ket_qua


def chon_tu_khoa(job: dict, state: dict) -> tuple[list[str], str]:
    """Trả về (danh sách từ khoá, câu giải thích lấy từ đâu).

    Ưu tiên keyword khai thẳng trong job. Không có thì rút từ kho CSV.
    """
    khai_tay = [k for k in (job.get("keyword") or []) if str(k).strip()]
    if khai_tay:
        return khai_tay, "khai thẳng trong agent_config.json"

    nguon = job.get("keyword_source")
    if not nguon or not nguon.get("file"):
        return [], "không có nguồn từ khoá"

    tat_ca = doc_kho_tu_khoa(nguon)
    if not tat_ca:
        return [], f"kho từ khoá lọc xong không còn dòng nào ({nguon['file']})"

    so_luong = int(nguon.get("top", 3))
    ten_job = job["name"]

    if not nguon.get("rotate", True):
        chon = tat_ca[:so_luong]
        return [r["keyword"] for r in chon], f"top {len(chon)} theo lượt tìm, không xoay vòng"

    da_dung = set(state.get(ten_job, {}).get("da_dung", []))
    con_lai = [r for r in tat_ca if r["keyword"] not in da_dung]

    ghi_chu = ""
    if len(con_lai) < so_luong:
        # Hết vòng → quét lại từ đầu
        con_lai = tat_ca
        da_dung = set()
        ghi_chu = " (đã quét hết kho, bắt đầu vòng mới)"

    chon = con_lai[:so_luong]
    ten_kw = [r["keyword"] for r in chon]

    state[ten_job] = {
        "da_dung": sorted(da_dung | set(ten_kw)),
        "tong_kho": len(tat_ca),
        "lan_cuoi": datetime.now().strftime("%Y-%m-%d"),
    }

    con = len(tat_ca) - len(state[ten_job]["da_dung"])
    return ten_kw, f"rút từ kho {len(tat_ca)} từ khoá, còn {con} chưa quét{ghi_chu}"


# --- Kiểm tra job ---

def validate_job(job: dict) -> list[str]:
    """Trả về danh sách lỗi. Rỗng nghĩa là job chạy được."""
    loi: list[str] = []

    if not job.get("name"):
        loi.append("thiếu 'name'")

    niche = job.get("niche")
    if not niche:
        loi.append("thiếu 'niche'")
    elif not (NICHE_CONFIG_DIR / f"{niche}.json").exists():
        loi.append(f"không thấy niche_configs/{niche}.json")

    source = job.get("source", "tiktok")
    if source == "tiktok":
        co_nguon = (
            (job.get("keyword") or [])
            or (job.get("profile") or [])
            or (job.get("hashtag") or [])
            or (job.get("keyword_source") or {}).get("file")
        )
        if not co_nguon:
            loi.append("chưa có keyword/profile/hashtag/keyword_source — không biết quét gì")
    elif source == "facebook_page":
        if not (job.get("page_id") or os.environ.get("FB_PAGE_ID")):
            loi.append("thiếu page_id (trong job) hoặc FB_PAGE_ID (trong .env)")
        if not os.environ.get("FB_PAGE_TOKEN"):
            loi.append("thiếu FB_PAGE_TOKEN trong .env")
    else:
        loi.append(f"source '{source}' không hỗ trợ — chỉ có: tiktok, facebook_page")

    return loi


# --- Dựng câu lệnh cho từng khâu ---

def _lap_co(ten: str, gia_tri) -> list[str]:
    """Biến list thành --keyword a --keyword b ..."""
    if not gia_tri:
        return []
    if isinstance(gia_tri, str):
        gia_tri = [gia_tri]
    out: list[str] = []
    for v in gia_tri:
        if str(v).strip():
            out += [ten, str(v)]
    return out


def build_commands(
    job: dict, output_dir: Path, tu_khoa: list[str]
) -> list[tuple[str, list[str]]]:
    """Trả về [(tên khâu, argv), ...] theo đúng thứ tự phải chạy."""
    py = [sys.executable, "-m", "tiktok_insight_miner"]
    niche = job["niche"]
    niche_config = str(NICHE_CONFIG_DIR / f"{niche}.json")
    classified = str(output_dir / "classified.json")
    lua_chon_md = str(output_dir / "3-lựa-chọn.md")
    selected_json = str(output_dir.parent / "_master" / "selected_angles.json")

    cmds: list[tuple[str, list[str]]] = []
    source = job.get("source", "tiktok")

    if source == "tiktok":
        # Khâu 1 — `run` gộp sẵn: tìm video → quét → phân loại → báo cáo [→ brief]
        cmd_run = py + ["run", "-o", str(output_dir), "--niche", niche]
        cmd_run += _lap_co("--keyword", tu_khoa)
        cmd_run += _lap_co("--profile", job.get("profile"))
        cmd_run += _lap_co("--hashtag", job.get("hashtag"))
        cmd_run += _lap_co("--lang", job.get("lang"))
        cmd_run += ["--max-comments", str(job.get("max_comments", 200))]
        cmd_run += ["--limit", str(job.get("limit", 10))]
        cmd_run += ["--min-views", str(job.get("min_views", 0))]
        cmd_run += ["--min-comments", str(job.get("min_comments", 1))]
        if job.get("newest_days"):
            cmd_run += ["--newest-days", str(job["newest_days"])]
        if job.get("with_angles", True):
            cmd_run += ["--with-angles"]
        cmds.append(("1. quét + phân loại + báo cáo", cmd_run))

    elif source == "facebook_page":
        # Khâu 1 — fanpage của mình: không có `run` gộp, nối tay 3-4 lệnh
        raw = str(output_dir / "raw_comments.json")
        cmd_fb = py + ["fb-fetch", "-o", raw,
                       "--since-days", str(job.get("since_days", 14))]
        if job.get("page_id"):
            cmd_fb += ["--page-id", str(job["page_id"])]
        if job.get("with_inbox", False):
            cmd_fb += ["--with-inbox"]
        cmds.append(("1a. lấy comment fanpage", cmd_fb))
        cmds.append(("1b. phân loại", py + ["classify", "-i", raw, "-o", classified]))
        cmds.append(("1c. báo cáo", py + ["report", "-i", classified,
                                          "-o", str(output_dir / "report.md")]))
        if job.get("with_angles", True):
            cmds.append(("1d. brief góc nội dung",
                         py + ["suggest", "-i", classified,
                               "-o", str(output_dir / "brief.md"), "--niche", niche]))

    # Khâu 2 — dựng bảng insight
    cmds.append((
        "2. dựng bảng insight",
        py + ["bank", "-i", classified, "--config", niche_config, "-o", str(output_dir)],
    ))

    # Khâu 3 — tự chọn angle (không cần người tick)
    cmds.append((
        "3. tự chọn angle",
        py + ["select", "-i", lua_chon_md, "--niche", niche,
              "--auto-top", str(job.get("auto_top", 5))],
    ))

    # Khâu 4 — viết kịch bản
    if job.get("run_production", True):
        cmds.append((
            "4. viết kịch bản",
            py + ["production", "-i", selected_json, "--config", niche_config],
        ))

    return cmds


# --- Chạy một job ---

def run_job(job: dict, ngay: str, dry_run: bool, state: dict) -> dict:
    ten = job["name"]
    # Mỗi nguồn một thư mục cùng tầng: <niche>/<ngày>__agent-tiktok/ và <niche>/<ngày>__agent-fb/
    # (cùng tầng để `select` vẫn suy đúng niche_root = thư mục cha)
    source_short = SOURCE_SHORT.get(job.get("source", "tiktok"), job.get("source", "x"))
    output_dir = OUTPUT_ROOT / job["niche"] / f"{ngay}__agent-{source_short}"

    ket_qua = {
        "job": ten,
        "niche": job["niche"],
        "output_dir": str(output_dir.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "cac_khau": [],
        "thanh_cong": True,
        "hong_o_khau": None,
        "tu_khoa": [],
        "bat_dau": datetime.now().isoformat(timespec="seconds"),
    }

    source = job.get("source", "tiktok")
    ket_qua["source"] = source

    print(f"\n{'=' * 66}")
    print(f"JOB: {ten}   (niche: {job['niche']} · nguồn: {source})")

    # Khâu 0 — chọn từ khoá. Chỉ TikTok cần; fanpage lấy theo page_id, không có từ khoá.
    tu_khoa: list[str] = []
    giai_thich = ""
    try:
        if source == "tiktok":
            tu_khoa, giai_thich = chon_tu_khoa(job, state)
    except (FileNotFoundError, OSError) as e:
        print(f"  ❌ HỎNG ở khâu 0 (lấy từ khoá) — {e}")
        ket_qua["cac_khau"].append({
            "khau": "0. lấy từ khoá", "trang_thai": "hỏng", "ly_do": str(e),
        })
        ket_qua["thanh_cong"] = False
        ket_qua["hong_o_khau"] = "0. lấy từ khoá"
        return ket_qua

    ket_qua["tu_khoa"] = tu_khoa
    ket_qua["nguon_tu_khoa"] = giai_thich

    co_profile_hashtag = bool(job.get("profile") or job.get("hashtag"))
    if source == "tiktok" and not tu_khoa and not co_profile_hashtag:
        ly_do = f"không lấy được từ khoá nào ({giai_thich})"
        print(f"  ❌ HỎNG ở khâu 0 — {ly_do}")
        ket_qua["cac_khau"].append({
            "khau": "0. lấy từ khoá", "trang_thai": "hỏng", "ly_do": ly_do,
        })
        ket_qua["thanh_cong"] = False
        ket_qua["hong_o_khau"] = "0. lấy từ khoá"
        return ket_qua

    if tu_khoa:
        print(f"Từ khoá tuần này ({giai_thich}):")
        for kw in tu_khoa:
            print(f"   · {kw}")
    if source == "tiktok":
        ket_qua["cac_khau"].append({"khau": "0. lấy từ khoá", "trang_thai": "xong"})

    print(f"Thư mục kết quả: {output_dir}")
    print(f"{'=' * 66}")

    cmds = build_commands(job, output_dir, tu_khoa)

    if dry_run:
        for ten_khau, argv in cmds:
            print(f"\n  [{ten_khau}]")
            print(f"    {subprocess.list2cmdline(argv[1:])}")
            ket_qua["cac_khau"].append({"khau": ten_khau, "trang_thai": "thử-chạy"})
        return ket_qua

    output_dir.mkdir(parents=True, exist_ok=True)
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    log_path = LOG_ROOT / f"{ngay}__{ten}.log"

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n{'=' * 66}\n{datetime.now():%Y-%m-%d %H:%M:%S} — JOB {ten}\n")
        log.write(f"Từ khoá: {', '.join(tu_khoa) if tu_khoa else '(không có)'}\n")
        log.write(f"{'=' * 66}\n")

        for ten_khau, argv in cmds:
            print(f"\n▶ {ten_khau}...")
            log.write(f"\n--- {ten_khau} ---\n$ {subprocess.list2cmdline(argv[1:])}\n")
            log.flush()

            proc = subprocess.run(
                argv,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            log.write(proc.stdout or "")
            if proc.stderr:
                log.write("\n[stderr]\n" + proc.stderr)
            log.flush()

            if proc.returncode == 0:
                print("  ✓ xong")
                ket_qua["cac_khau"].append({"khau": ten_khau, "trang_thai": "xong"})
                continue

            dong = (proc.stderr or proc.stdout or "").strip().splitlines()
            ly_do = dong[-1] if dong else f"mã lỗi {proc.returncode}"
            print(f"  ❌ HỎNG — {ly_do}")
            print(f"     Log đầy đủ: {log_path}")
            ket_qua["cac_khau"].append({
                "khau": ten_khau, "trang_thai": "hỏng", "ly_do": ly_do,
            })
            ket_qua["thanh_cong"] = False
            ket_qua["hong_o_khau"] = ten_khau
            break  # khâu sau phụ thuộc khâu trước — không chạy tiếp

        ket_qua["log"] = str(log_path.relative_to(PROJECT_ROOT)).replace("\\", "/")

    ket_qua["ket_thuc"] = datetime.now().isoformat(timespec="seconds")
    return ket_qua


# --- Tóm tắt ---

def dem_file_kich_ban(job: dict) -> int:
    """Đếm file kịch bản thật trên đĩa — không đoán."""
    thu_muc = OUTPUT_ROOT / job["niche"] / "4-thực-thi"
    if not thu_muc.exists():
        return 0
    return len(list(thu_muc.glob("angle-*.md")))


# --- Khâu 5: so sánh 2 luồng (thị trường vs khách của mình) ---

def so_sanh_nguon(ket_qua_list: list[dict], ngay: str) -> list[Path]:
    """Với mỗi niche có ≥2 job chạy trọn từ ≥2 nguồn khác nhau: gộp classified.json
    rồi sinh 1 report đa nguồn. Reporter tự tách bảng theo nguồn — không cần code thêm.

    Trả về list file so sánh đã sinh (rỗng nếu không có cặp nào để so).
    """
    theo_niche: dict[str, list[dict]] = {}
    for k in ket_qua_list:
        if k["thanh_cong"]:
            theo_niche.setdefault(k["niche"], []).append(k)

    da_sinh: list[Path] = []
    for niche, jobs in theo_niche.items():
        nguon = {j.get("source", "tiktok") for j in jobs}
        if len(nguon) < 2:
            continue

        gop: list = []
        for j in jobs:
            f = PROJECT_ROOT / j["output_dir"] / "classified.json"
            if not f.exists():
                print(f"  ⚠️  Bỏ qua {j['job']} trong so sánh — không thấy {f.name}")
                continue
            try:
                gop.extend(json.loads(f.read_text(encoding="utf-8")))
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Bỏ qua {j['job']} trong so sánh — {f.name} hỏng: {e}")

        if not gop:
            continue

        thu_muc = OUTPUT_ROOT / niche / f"{ngay}__agent-so-sanh"
        thu_muc.mkdir(parents=True, exist_ok=True)
        gop_json = thu_muc / "classified.json"
        gop_json.write_text(json.dumps(gop, ensure_ascii=False, indent=2), encoding="utf-8")
        out_md = thu_muc / "so-sanh-nguon.md"

        proc = subprocess.run(
            [sys.executable, "-m", "tiktok_insight_miner", "report",
             "-i", str(gop_json), "-o", str(out_md)],
            cwd=PROJECT_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if proc.returncode == 0:
            print(f"  ✓ So sánh {niche}: {sorted(nguon)} → {out_md}")
            da_sinh.append(out_md)
            for j in jobs:
                j["so_sanh"] = str(out_md.relative_to(PROJECT_ROOT)).replace("\\", "/")
        else:
            dong = (proc.stderr or proc.stdout or "").strip().splitlines()
            print(f"  ❌ So sánh {niche} hỏng — {dong[-1] if dong else proc.returncode}")

    return da_sinh


def viet_tom_tat(ket_qua_list: list[dict], ngay: str) -> Path:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    path = LOG_ROOT / f"{ngay}-tom-tat.md"

    xong = [k for k in ket_qua_list if k["thanh_cong"]]
    hong = [k for k in ket_qua_list if not k["thanh_cong"]]

    L: list[str] = []
    L.append(f"# 🤖 Agent chạy ngày {ngay}")
    L.append("")
    L.append(f"> Ghi lúc {datetime.now():%Y-%m-%d %H:%M:%S}")
    L.append("")
    L.append(f"**{len(xong)}/{len(ket_qua_list)} job chạy trọn.**")
    L.append("")

    if hong:
        L.append("## ❌ Job hỏng")
        L.append("")
        for k in hong:
            L.append(f"- **{k['job']}** — dừng ở khâu *{k['hong_o_khau']}*")
            for khau in k["cac_khau"]:
                if khau["trang_thai"] == "hỏng":
                    L.append(f"  - Lý do: `{khau.get('ly_do', 'không rõ')}`")
            if k.get("log"):
                L.append(f"  - Log: [{k['log']}]({k['log']})")
        L.append("")

    if xong:
        L.append("## ✅ Job chạy trọn")
        L.append("")
        for k in xong:
            L.append(f"### {k['job']}")
            L.append("")
            if k.get("tu_khoa"):
                L.append(f"**Từ khoá đã quét**: {', '.join(k['tu_khoa'])}")
                L.append(f"_({k.get('nguon_tu_khoa', '')})_")
                L.append("")
            L.append(f"- Insight thô: [{k['output_dir']}/report.md]({k['output_dir']}/report.md)")
            L.append(f"- Góc nội dung: [{k['output_dir']}/brief.md]({k['output_dir']}/brief.md)")
            L.append(
                f"- Kịch bản đã viết: `output/{k['niche']}/4-thực-thi/` "
                f"({k.get('so_file_kich_ban', 0)} file)"
            )
            if k.get("so_sanh"):
                L.append(f"- 🔀 **So sánh thị trường vs khách**: [{k['so_sanh']}]({k['so_sanh']})")
            L.append("")

    L.append("---")
    L.append("")
    L.append("_Angle do máy tự chọn mang nhãn `selected_by: auto` trong `selected_angles.json`._")
    L.append("_Muốn đổi: mở `3-lựa-chọn.md`, tick tay rồi chạy lại `tim select`._")

    path.write_text("\n".join(L) + "\n", encoding="utf-8")
    return path


# --- Entry point ---

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent định kỳ: quét insight TikTok → viết kịch bản, không cần người canh.",
    )
    parser.add_argument(
        "--config", type=str, default=str(CONFIG_PATH),
        help="Đường dẫn agent_config.json",
    )
    parser.add_argument(
        "--job", type=str, default=None,
        help="Chỉ chạy 1 job theo tên (bỏ qua cờ enabled của job đó)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="In ra câu lệnh sẽ chạy rồi dừng. KHÔNG gọi API, không tốn tiền.",
    )
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    defaults = cfg.get("defaults", {})
    jobs_all = [merge_defaults(j, defaults) for j in cfg.get("jobs", [])]

    if args.job:
        jobs = [j for j in jobs_all if j.get("name") == args.job]
        if not jobs:
            co = ", ".join(j.get("name", "?") for j in jobs_all) or "(không có job nào)"
            sys.exit(f"❌ Không thấy job tên '{args.job}'. Job có trong file: {co}")
    else:
        jobs = [j for j in jobs_all if j.get("enabled")]

    if not jobs:
        print("ℹ️  Không có job nào đang bật.")
        print(f'   Mở {args.config}, điền từ khoá rồi đổi "enabled": true.')
        return

    hop_le: list[dict] = []
    for job in jobs:
        loi = validate_job(job)
        if loi:
            print(f"⚠️  Bỏ qua job '{job.get('name', '?')}': {'; '.join(loi)}")
            continue
        hop_le.append(job)

    if not hop_le:
        sys.exit("❌ Không job nào đủ điều kiện chạy. Xem cảnh báo bên trên.")

    if args.dry_run:
        print("🔍 CHẾ ĐỘ THỬ — chỉ in lệnh, không chạy, không tốn tiền.")

    ngay = datetime.now().strftime("%Y-%m-%d")
    state = load_keyword_state()
    ket_qua_list: list[dict] = []

    for job in hop_le:
        kq = run_job(job, ngay, args.dry_run, state)
        if not args.dry_run and kq["thanh_cong"]:
            kq["so_file_kich_ban"] = dem_file_kich_ban(job)
        ket_qua_list.append(kq)

    print(f"\n{'=' * 66}")
    xong = sum(1 for k in ket_qua_list if k["thanh_cong"])
    print(f"XONG: {xong}/{len(ket_qua_list)} job chạy trọn")

    if not args.dry_run:
        save_keyword_state(state)
        # Khâu 5 — có cả TikTok lẫn fanpage cùng niche thì sinh bảng so sánh
        if len({k.get("source") for k in ket_qua_list if k["thanh_cong"]}) >= 2:
            print("\n▶ 5. so sánh thị trường vs khách của mình...")
            so_sanh_nguon(ket_qua_list, ngay)
        print(f"📄 Tóm tắt: {viet_tom_tat(ket_qua_list, ngay)}")

    if any(not k["thanh_cong"] for k in ket_qua_list):
        sys.exit(1)


if __name__ == "__main__":
    main()
