"""Test fb_page_source.py — luồng insight thứ 2 (fanpage của mình).

Không gọi Graph API thật. Dùng hàm `fetch` giả trả response đúng cấu trúc
`{"data": [...], "paging": {...}}` như tài liệu Meta.

Trọng tâm: ẩn danh hoá phải đúng — đây là dữ liệu khách hàng.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tiktok_insight_miner.fb_page_source import (
    GraphAPIError,
    anonymize_text,
    anonymous_author,
    fetch_page_comments,
    fetch_page_inbox,
    graph_paginate,
)

PAGE_ID = "111222333"


def _fb_time(days_ago: int) -> str:
    t = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%S+0000")


# --- Ẩn danh hoá ---

class TestAnonymize:
    def test_che_so_dien_thoai_viet_nam(self):
        assert anonymize_text("gọi em 0912345678 nhé") == "gọi em [sđt] nhé"
        assert anonymize_text("sđt +84 912 345 678") == "sđt [sđt]"
        assert anonymize_text("zalo 0912.345.678") == "zalo [sđt]"

    def test_che_email(self):
        assert anonymize_text("mail tuan.le@gmail.com") == "mail [email]"

    def test_che_link(self):
        assert anonymize_text("xem https://shopee.vn/abc nha") == "xem [link] nha"
        assert anonymize_text("vào www.example.com") == "vào [link]"

    def test_giu_nguyen_text_thuong(self):
        s = "Chị ơi khoá học bao nhiêu tiền, em ở Hà Nội"
        assert anonymize_text(s) == s

    def test_khong_che_so_nam_hay_gia(self):
        # 2026, 500k không phải SĐT — không được che
        assert anonymize_text("năm 2026 giá 500k") == "năm 2026 giá 500k"

    def test_ten_gia_on_dinh_va_khong_lo_id(self):
        a = anonymous_author("10001")
        assert a == anonymous_author("10001")
        assert a.startswith("fb-") and len(a) == 11
        assert "10001" not in a

    def test_khong_co_id_thi_unknown(self):
        assert anonymous_author("") == "fb-unknown"
        assert anonymous_author(None) == "fb-unknown"


# --- Phân trang ---

class TestPaginate:
    def test_di_het_cac_trang(self):
        calls: list[str] = []

        def fake(path, token, params, ver):
            calls.append(path)
            if path == "x/edge":
                return {"data": [{"id": "1"}, {"id": "2"}],
                        "paging": {"next": "https://graph/next?after=abc"}}
            return {"data": [{"id": "3"}]}

        items = list(graph_paginate("x/edge", "tok", {}, fetch=fake))
        assert [i["id"] for i in items] == ["1", "2", "3"]
        assert calls == ["x/edge", "https://graph/next?after=abc"]

    def test_max_items_dung_som(self):
        def fake(path, token, params, ver):
            return {"data": [{"id": str(i)} for i in range(10)],
                    "paging": {"next": "https://graph/next"}}

        items = list(graph_paginate("x", "tok", {}, max_items=3, fetch=fake))
        assert len(items) == 3


# --- Luồng comment ---

def _fake_comments_api(page_id=PAGE_ID):
    """Fanpage có 1 bài, 4 comment: 1 của Page, 1 rỗng, 2 của khách (1 có SĐT)."""
    def fake(path, token, params, ver):
        if path.endswith("/feed"):
            return {"data": [{
                "id": "post_1",
                "message": "Bài mới",
                "created_time": _fb_time(3),
                "permalink_url": "https://www.facebook.com/p/post_1",
            }]}
        if path == "post_1/comments":
            assert params["filter"] == "stream"
            return {"data": [
                {"id": "c1", "message": "Chị ơi giá bao nhiêu",
                 "from": {"id": "u1", "name": "Nguyễn Văn A"},
                 "like_count": 3, "comment_count": 1, "created_time": _fb_time(2)},
                {"id": "c2", "message": "Dạ chị inbox em nhé",
                 "from": {"id": page_id, "name": "Fanpage"},
                 "like_count": 0, "comment_count": 0, "created_time": _fb_time(2)},
                {"id": "c3", "message": "",
                 "from": {"id": "u2"}, "like_count": 0, "comment_count": 0},
                {"id": "c4", "message": "gọi em 0987654321",
                 "from": {"id": "u3", "name": "Trần B"},
                 "like_count": 1, "comment_count": 0, "created_time": _fb_time(1),
                 "parent": {"id": "c1"}},
            ]}
        raise AssertionError(f"endpoint không mong đợi: {path}")
    return fake


class TestFetchComments:
    def test_bo_comment_cua_page_va_comment_rong(self):
        cs = fetch_page_comments(PAGE_ID, "tok", since_days=14, fetch=_fake_comments_api())
        assert [c.id for c in cs] == ["c1", "c4"]

    def test_an_danh_va_che_sdt(self):
        cs = fetch_page_comments(PAGE_ID, "tok", fetch=_fake_comments_api())
        c4 = next(c for c in cs if c.id == "c4")
        assert c4.text == "gọi em [sđt]"
        assert c4.author.startswith("fb-")
        assert "Trần" not in c4.author
        # Không được rò tên thật ở bất kỳ đâu trong raw
        assert "Trần" not in str(c4.raw) and "Nguyễn" not in str(c4.raw)

    def test_mapping_dung_schema_comment(self):
        cs = fetch_page_comments(PAGE_ID, "tok", fetch=_fake_comments_api())
        c1 = cs[0]
        assert c1.likes == 3
        assert c1.reply_count == 1
        assert c1.video_url == "https://www.facebook.com/p/post_1"
        assert c1.raw["platform"] == "facebook_page"
        assert c1.raw["post_id"] == "post_1"
        assert c1.raw["is_reply"] is False

    def test_reply_duoc_danh_dau(self):
        cs = fetch_page_comments(PAGE_ID, "tok", fetch=_fake_comments_api())
        c4 = next(c for c in cs if c.id == "c4")
        assert c4.raw["is_reply"] is True
        assert c4.raw["parent_id"] == "c1"

    def test_feed_rong_khong_loi(self):
        def fake(path, token, params, ver):
            return {"data": []}
        assert fetch_page_comments(PAGE_ID, "tok", fetch=fake) == []


# --- Luồng inbox ---

def _fake_inbox_api(page_id=PAGE_ID):
    """2 hội thoại: 1 mới (có tin khách + tin page), 1 cũ hơn mốc → dừng."""
    def fake(path, token, params, ver):
        if path.endswith("/conversations"):
            return {"data": [
                {"id": "t_new", "updated_time": _fb_time(2),
                 "participants": {"data": [{"id": "u9", "name": "Khách C", "email": "c@x.com"}]}},
                {"id": "t_old", "updated_time": _fb_time(40),
                 "participants": {"data": [{"id": "u8", "name": "Khách D"}]}},
            ]}
        if path == "t_new/messages":
            return {"data": [
                {"id": "m1", "message": "Em muốn hỏi khoá học, sđt em 0911222333",
                 "from": {"id": "u9", "name": "Khách C"}, "created_time": _fb_time(2)},
                {"id": "m2", "message": "Dạ chị để lại số em gọi",
                 "from": {"id": page_id, "name": "Fanpage"}, "created_time": _fb_time(2)},
                {"id": "m3", "message": "tin cũ từ tháng trước",
                 "from": {"id": "u9"}, "created_time": _fb_time(45)},
            ]}
        if path == "t_old/messages":
            raise AssertionError("không được gọi hội thoại cũ hơn mốc")
        raise AssertionError(f"endpoint không mong đợi: {path}")
    return fake


class TestFetchInbox:
    def test_chi_giu_tin_khach_trong_moc(self):
        ms = fetch_page_inbox(PAGE_ID, "tok", since_days=14, fetch=_fake_inbox_api())
        assert [m.id for m in ms] == ["m1"]

    def test_an_danh_tuyet_doi(self):
        ms = fetch_page_inbox(PAGE_ID, "tok", since_days=14, fetch=_fake_inbox_api())
        m = ms[0]
        assert m.text == "Em muốn hỏi khoá học, sđt em [sđt]"
        assert m.author.startswith("fb-")
        dump = m.model_dump_json()
        for bi_mat in ("Khách C", "c@x.com", "0911222333", "u9"):
            assert bi_mat not in dump, f"rò rỉ: {bi_mat}"

    def test_raw_chi_giu_id_ky_thuat(self):
        ms = fetch_page_inbox(PAGE_ID, "tok", since_days=14, fetch=_fake_inbox_api())
        assert set(ms[0].raw.keys()) == {"platform", "conversation_id"}
        assert ms[0].raw["platform"] == "facebook_inbox"

    def test_dung_som_khi_gap_hoi_thoai_cu(self):
        # _fake_inbox_api raise nếu gọi t_old/messages → test này pass nghĩa là đã dừng đúng
        fetch_page_inbox(PAGE_ID, "tok", since_days=14, fetch=_fake_inbox_api())


# --- Lỗi ---

class TestErrors:
    def test_loi_co_goi_y_sua(self):
        e = GraphAPIError(190, "Error validating access token", "/x")
        assert "190" in str(e)
        assert "FB_PAGE_TOKEN" in str(e)

    def test_loi_khong_ro_ma_van_ok(self):
        e = GraphAPIError(None, "lỗi mạng", "/x")
        assert "lỗi mạng" in str(e)
