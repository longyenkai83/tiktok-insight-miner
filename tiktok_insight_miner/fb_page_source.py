"""Facebook Page source — lấy comment + tin nhắn inbox từ fanpage CỦA CHÍNH MÌNH qua Graph API.

Đây là luồng insight thứ hai, song song với TikTok:
  - TikTok  → thị trường rộng, người lạ chưa biết mình
  - Fanpage → khách của mình, đã theo dõi, đã tương tác

Output khớp 100% schema `Comment` của scraper.py, nên classify → bank → select → production
chạy y nguyên. Nhãn nguồn nằm ở `raw["platform"]`:
  "facebook_page"  = comment công khai dưới bài đăng
  "facebook_inbox" = tin nhắn khách gửi vào inbox

Endpoint (theo tài liệu Meta Graph API, đối chiếu 2026-09-11):
  GET /{page-id}/feed                       → bài đăng
  GET /{post-id}/comments?filter=stream     → comment mọi cấp (cả reply)
  GET /{page-id}/conversations              → hội thoại inbox
  GET /{conversation-id}/messages           → tin nhắn trong hội thoại

Quyền cần trên Page access token:
  comment: pages_read_engagement
  inbox:   thêm pages_messaging + pages_manage_metadata

RIÊNG TƯ — luật cứng của module này:
  1. Không lưu tên thật người gửi. `author` = "fb-" + 8 ký tự hash của id.
  2. Che số điện thoại / email / URL trong text TRƯỚC khi ghi ra đĩa và trước khi gửi lên Claude.
  3. Bỏ mọi tin do chính Page gửi (câu trả lời của mình, không phải tiếng khách).
  4. `raw` chỉ giữ id kỹ thuật (post_id, conversation_id), KHÔNG giữ response thô của inbox.

KHÔNG BỊA TÊN FIELD: mọi field đọc bằng .get(). Chạy `tim fb-fetch --probe` để in response
thật của 1 post + 1 comment + 1 hội thoại, đối chiếu trước khi tin vào mapping.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterator

from tiktok_insight_miner.models import Comment

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.facebook.com"
DEFAULT_API_VERSION = "v26.0"  # bản đang hiện trên docs Meta lúc đối chiếu
PAGE_SIZE = 100
MAX_RETRY = 3

COMMENT_FIELDS = "id,message,from,like_count,comment_count,created_time,parent"
POST_FIELDS = "id,message,created_time,permalink_url"
CONVERSATION_FIELDS = "id,updated_time,participants"
MESSAGE_FIELDS = "id,message,from,created_time"

# Mã lỗi Graph API hay gặp → lời giải thích đời thường
ERROR_HINTS = {
    190: "Token hết hạn hoặc không hợp lệ — tạo Page access token mới rồi cập nhật FB_PAGE_TOKEN trong .env",
    10: "Thiếu quyền — token chưa được cấp pages_read_engagement (comment) hoặc pages_messaging (inbox)",
    200: "Thiếu quyền — token chưa được cấp đủ permission cho thao tác này",
    4: "Chạm giới hạn gọi API của app — đợi 1 giờ rồi chạy lại",
    17: "Chạm giới hạn gọi API của user — đợi 1 giờ rồi chạy lại",
    32: "Chạm giới hạn gọi API của Page — đợi 1 giờ rồi chạy lại",
    613: "Chạm giới hạn gọi API — đợi rồi chạy lại",
    100: "Tham số sai — thường do page-id sai, hoặc field không tồn tại ở phiên bản API này",
}

RATE_LIMIT_CODES = {4, 17, 32, 613}


class GraphAPIError(RuntimeError):
    """Lỗi từ Graph API, kèm mã và gợi ý cách sửa."""

    def __init__(self, code: int | None, message: str, endpoint: str):
        self.code = code
        self.endpoint = endpoint
        hint = ERROR_HINTS.get(code or -1, "")
        full = f"Graph API lỗi {code}: {message} (tại {endpoint})"
        if hint:
            full += f"\n   → {hint}"
        super().__init__(full)


# --- Ẩn danh hoá ---

# SĐT Việt Nam: 0xxxxxxxxx (10 số), +84xxxxxxxxx, 84xxxxxxxxx, có thể có dấu cách/chấm/gạch giữa
_PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?!\d)"
)
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def anonymize_text(text: str) -> str:
    """Che thông tin định danh trong text. Giữ nguyên phần còn lại để không mất ý."""
    if not text:
        return text
    text = _URL_RE.sub("[link]", text)
    text = _EMAIL_RE.sub("[email]", text)
    text = _PHONE_RE.sub("[sđt]", text)
    return text


def anonymous_author(user_id: str | None) -> str:
    """Tên giả ổn định từ id: cùng người → cùng tên giả, nhưng không lần ngược ra được."""
    if not user_id:
        return "fb-unknown"
    return "fb-" + hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:8]


# --- Gọi Graph API ---

def _build_url(api_version: str, path: str, params: dict[str, Any]) -> str:
    path = path.lstrip("/")
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return f"{GRAPH_BASE}/{api_version}/{path}?{query}"


def graph_get(
    path: str,
    token: str,
    params: dict[str, Any] | None = None,
    api_version: str = DEFAULT_API_VERSION,
) -> dict[str, Any]:
    """GET một endpoint, trả JSON. Tự retry khi bị giới hạn tốc độ. Lỗi thì raise GraphAPIError."""
    params = dict(params or {})
    params["access_token"] = token
    url = _build_url(api_version, path, params)
    # Không log token
    safe_url = url.replace(token, "***")

    for attempt in range(1, MAX_RETRY + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "tiktok-insight-miner/0.5"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
            data = json.loads(body)
        except urllib.error.HTTPError as e:
            # Graph API trả lỗi dạng JSON trong body kể cả khi HTTP 4xx
            try:
                data = json.loads(e.read().decode("utf-8"))
            except Exception:
                raise GraphAPIError(e.code, str(e), safe_url) from e
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt < MAX_RETRY:
                logger.warning("Lỗi mạng (%s), thử lại %d/%d", e, attempt, MAX_RETRY)
                time.sleep(2 * attempt)
                continue
            raise GraphAPIError(None, f"lỗi mạng: {e}", safe_url) from e

        err = data.get("error") if isinstance(data, dict) else None
        if not err:
            return data

        code = err.get("code")
        if code in RATE_LIMIT_CODES and attempt < MAX_RETRY:
            wait = 30 * attempt
            logger.warning("Bị giới hạn tốc độ (code %s) — đợi %ds rồi thử lại", code, wait)
            time.sleep(wait)
            continue
        raise GraphAPIError(code, err.get("message", "không rõ"), safe_url)

    raise GraphAPIError(None, "hết số lần thử", safe_url)


def graph_paginate(
    path: str,
    token: str,
    params: dict[str, Any],
    api_version: str = DEFAULT_API_VERSION,
    max_items: int | None = None,
    fetch: Callable[..., dict[str, Any]] | None = None,
) -> Iterator[dict[str, Any]]:
    """Duyệt hết các trang của một edge, yield từng item.

    `fetch` cho phép thay graph_get bằng hàm giả khi test — không cần token thật.
    """
    fetch = fetch or graph_get
    params = dict(params)
    params.setdefault("limit", PAGE_SIZE)
    dem = 0
    next_url: str | None = None

    while True:
        if next_url is None:
            data = fetch(path, token, params, api_version)
        elif fetch is graph_get:
            # Trang sau: Graph API trả sẵn URL đầy đủ (đã kèm token) — gọi thẳng
            data = _get_absolute(next_url)
        else:
            # Hàm giả khi test: nhận URL trang sau ở vị trí path, params=None
            data = fetch(next_url, token, None, api_version)

        for item in data.get("data", []) or []:
            yield item
            dem += 1
            if max_items and dem >= max_items:
                return

        next_url = (data.get("paging") or {}).get("next")
        if not next_url:
            return


def _get_absolute(url: str) -> dict[str, Any]:
    """Gọi URL trang-sau mà Graph API đã trả sẵn (đã kèm access_token)."""
    req = urllib.request.Request(url, headers={"User-Agent": "tiktok-insight-miner/0.5"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read().decode("utf-8"))
        except Exception:
            raise GraphAPIError(e.code, str(e), "(trang sau)") from e
    err = data.get("error") if isinstance(data, dict) else None
    if err:
        raise GraphAPIError(err.get("code"), err.get("message", "không rõ"), "(trang sau)")
    return data


# --- Thời gian ---

def _since_unix(since_days: int) -> int:
    return int((datetime.now(timezone.utc) - timedelta(days=since_days)).timestamp())


def _parse_fb_time(s: str | None) -> datetime | None:
    """Graph API trả '2026-09-01T10:20:30+0000'."""
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


# --- Luồng 1: comment dưới bài đăng ---

def fetch_page_comments(
    page_id: str,
    token: str,
    since_days: int = 14,
    api_version: str = DEFAULT_API_VERSION,
    max_posts: int | None = None,
    fetch: Callable[..., dict[str, Any]] | None = None,
) -> list[Comment]:
    """Lấy comment (mọi cấp) của các bài đăng trong `since_days` ngày gần nhất.

    Bỏ comment do chính Page viết. Ẩn danh người viết. Che SĐT/email/link.
    """
    posts = list(graph_paginate(
        f"{page_id}/feed", token,
        {"fields": POST_FIELDS, "since": _since_unix(since_days)},
        api_version, max_items=max_posts, fetch=fetch,
    ))
    logger.info("Fanpage %s: %d bài đăng trong %d ngày", page_id, len(posts), since_days)

    comments: list[Comment] = []
    bo_qua_page = 0
    for post in posts:
        post_id = post.get("id")
        if not post_id:
            continue
        permalink = post.get("permalink_url") or ""
        post_time = post.get("created_time") or ""

        for c in graph_paginate(
            f"{post_id}/comments", token,
            {"fields": COMMENT_FIELDS, "filter": "stream"},
            api_version, fetch=fetch,
        ):
            tu = c.get("from") or {}
            tu_id = str(tu.get("id") or "")
            if tu_id and tu_id == str(page_id):
                bo_qua_page += 1
                continue  # câu trả lời của mình, không phải tiếng khách

            text = anonymize_text((c.get("message") or "").strip())
            if not text:
                continue  # comment chỉ có sticker/ảnh

            comments.append(Comment(
                id=str(c.get("id") or ""),
                text=text,
                author=anonymous_author(tu_id),
                likes=int(c.get("like_count") or 0),
                reply_count=int(c.get("comment_count") or 0),
                created_at=str(c.get("created_time") or ""),
                video_url=permalink,
                raw={
                    "platform": "facebook_page",
                    "post_id": post_id,
                    "post_created_time": post_time,
                    "is_reply": bool(c.get("parent")),
                    "parent_id": (c.get("parent") or {}).get("id", ""),
                },
            ))

    logger.info(
        "Fanpage %s: %d comment của khách (bỏ %d comment do Page tự viết)",
        page_id, len(comments), bo_qua_page,
    )
    return comments


# --- Luồng 2: tin nhắn inbox ---

def fetch_page_inbox(
    page_id: str,
    token: str,
    since_days: int = 14,
    api_version: str = DEFAULT_API_VERSION,
    max_conversations: int | None = None,
    fetch: Callable[..., dict[str, Any]] | None = None,
) -> list[Comment]:
    """Lấy tin nhắn KHÁCH gửi vào inbox trong `since_days` ngày gần nhất.

    Chỉ giữ tin từ phía khách. Ẩn danh hoàn toàn. Che SĐT/email/link.
    KHÔNG lưu response thô — inbox là dữ liệu nhạy cảm nhất.
    """
    moc = datetime.now(timezone.utc) - timedelta(days=since_days)
    messages: list[Comment] = []
    so_hoi_thoai = 0

    for conv in graph_paginate(
        f"{page_id}/conversations", token,
        {"fields": CONVERSATION_FIELDS},
        api_version, max_items=max_conversations, fetch=fetch,
    ):
        conv_id = conv.get("id")
        if not conv_id:
            continue
        # Tài liệu Meta: conversations không hỗ trợ lọc theo thời gian → lọc phía mình.
        # Hội thoại sắp theo updated_time giảm dần, gặp cái cũ hơn mốc là dừng luôn.
        cap_nhat = _parse_fb_time(conv.get("updated_time"))
        if cap_nhat and cap_nhat < moc:
            break
        so_hoi_thoai += 1

        for m in graph_paginate(
            f"{conv_id}/messages", token,
            {"fields": MESSAGE_FIELDS},
            api_version, fetch=fetch,
        ):
            tu = m.get("from") or {}
            tu_id = str(tu.get("id") or "")
            if tu_id and tu_id == str(page_id):
                continue  # tin của mình / nhân viên trả lời

            luc = _parse_fb_time(m.get("created_time"))
            if luc and luc < moc:
                continue

            text = anonymize_text((m.get("message") or "").strip())
            if not text:
                continue  # tin chỉ có ảnh/sticker

            messages.append(Comment(
                id=str(m.get("id") or ""),
                text=text,
                author=anonymous_author(tu_id),
                likes=0,
                reply_count=0,
                created_at=str(m.get("created_time") or ""),
                video_url="",
                raw={
                    "platform": "facebook_inbox",
                    "conversation_id": conv_id,
                },
            ))

    logger.info(
        "Inbox %s: %d tin nhắn của khách từ %d hội thoại (%d ngày)",
        page_id, len(messages), so_hoi_thoai, since_days,
    )
    return messages


# --- Probe: in response thật để đối chiếu tên field ---

def probe(
    page_id: str,
    token: str,
    api_version: str = DEFAULT_API_VERSION,
    with_inbox: bool = False,
) -> dict[str, Any]:
    """Gọi thật 1 bài + 1 comment + (1 hội thoại) và trả về response thô.

    Mục đích: đối chiếu tên field trước khi tin mapping — rule "không bịa field".
    Dữ liệu inbox trong probe được che tên/số trước khi trả về.
    """
    ket_qua: dict[str, Any] = {"api_version": api_version, "page_id": page_id}

    feed = graph_get(f"{page_id}/feed", token, {"fields": POST_FIELDS, "limit": 1}, api_version)
    ket_qua["post_sample"] = (feed.get("data") or [None])[0]

    post_id = (ket_qua["post_sample"] or {}).get("id")
    if post_id:
        cm = graph_get(
            f"{post_id}/comments", token,
            {"fields": COMMENT_FIELDS, "filter": "stream", "limit": 1}, api_version,
        )
        mau = (cm.get("data") or [None])[0]
        if mau and mau.get("from"):
            mau = dict(mau)
            mau["from"] = {"id": "(che)", "name": "(che)"}
        ket_qua["comment_sample"] = mau

    if with_inbox:
        cv = graph_get(
            f"{page_id}/conversations", token,
            {"fields": CONVERSATION_FIELDS, "limit": 1}, api_version,
        )
        conv = (cv.get("data") or [None])[0]
        if conv:
            conv = dict(conv)
            conv["participants"] = "(che)"
            ket_qua["conversation_sample"] = conv
            ms = graph_get(
                f"{conv['id']}/messages", token,
                {"fields": MESSAGE_FIELDS, "limit": 1}, api_version,
            )
            mau = (ms.get("data") or [None])[0]
            if mau:
                mau = dict(mau)
                mau["from"] = "(che)"
                mau["message"] = anonymize_text(mau.get("message") or "")
                ket_qua["message_sample"] = mau
        else:
            ket_qua["conversation_sample"] = None

    return ket_qua
