"""Test selection.py — tập trung vào cơ chế auto-top (chọn angle không cần người tick).

Auto-top là mắt xích cho agent chạy định kỳ: không có người ngồi tick `[x]` lúc
8h sáng thứ Hai, máy phải tự chọn được angle để dây chuyền đi tiếp sang viết bài.
"""

from __future__ import annotations

import pytest

from tiktok_insight_miner.selection import parse_selected_md

# Mẫu đúng format do insight_bank.py sinh ra.
# 2 dòng tick tay (score 12, 9) + 3 dòng chưa tick (score 20, 15, 15).
SAMPLE_MD = """\
# ✅ Lựa chọn — Top 5 candidates

- [x] `[SCORE 12]` `[P001 KINH_DOANH_KIET_SUC]` `[PAIN_SOLUTION]` "quote tick tay mot" — @userA (3 likes)
  - 💡 Tóm tắt một.
  - 📂 nhóm: **Kinh doanh kiệt sức** · 🎯 intent: `VENT`

- [ ] `[SCORE 20]` `[P002 KINH_DOANH_KIET_SUC]` `[FRAMEWORK]` "quote diem cao nhat" — @userB (50 likes)
  - 💡 Tóm tắt hai.
  - 📂 nhóm: **Kinh doanh kiệt sức** · 🎯 intent: `SEEK_HOWTO`

- [ ] `[SCORE 15]` `[Q001 DONG_GOI_CHUYEN_MON]` `[FAQ_ANSWER]` "quote diem giua, it like" — @userC (2 likes)
  - 💡 Tóm tắt ba.
  - 📂 nhóm: **Đóng gói chuyên môn** · 🎯 intent: `VENT`

- [ ] `[SCORE 15]` `[Q002 DONG_GOI_CHUYEN_MON]` `[FAQ_ANSWER]` "quote diem giua, nhieu like" — @userD (99 likes)
  - 💡 Tóm tắt bốn.
  - 📂 nhóm: **Đóng gói chuyên môn** · 🎯 intent: `VENT`

- [X] `[SCORE 9]` `[D001 TIEN_BAC_BINH_YEN]` `[PAIN_SOLUTION]` "quote tick tay hai, chu X hoa" — @userE (1 likes)
  - 💡 Tóm tắt năm.
  - 📂 nhóm: **Tiền bạc & bình yên** · 🎯 intent: `VENT`
"""


@pytest.fixture
def md_file(tmp_path):
    p = tmp_path / "3-lựa-chọn.md"
    p.write_text(SAMPLE_MD, encoding="utf-8")
    return p


def test_khong_auto_thi_chi_lay_tick_tay(md_file):
    """Hành vi gốc phải giữ nguyên: không truyền auto_top → chỉ angle có [x]."""
    result = parse_selected_md(md_file)
    assert [it["id"] for it in result] == ["P001", "D001"]
    assert all(it["selected_by"] == "manual" for it in result)


def test_bat_duoc_ca_chu_X_hoa(md_file):
    """`- [X]` viết hoa cũng phải tính là đã tick."""
    ids = [it["id"] for it in parse_selected_md(md_file)]
    assert "D001" in ids


def test_auto_top_bu_cho_du_so_luong(md_file):
    """Có 2 tick tay, xin 4 → bù 2 angle điểm cao nhất trong đám chưa tick."""
    result = parse_selected_md(md_file, auto_top=4)
    assert len(result) == 4
    # 2 cái tick tay đứng trước, giữ nguyên thứ tự file
    assert [it["id"] for it in result[:2]] == ["P001", "D001"]
    # Bù: P002 (score 20) trước, rồi Q002 (score 15, 99 likes) hơn Q001 (score 15, 2 likes)
    assert [it["id"] for it in result[2:]] == ["P002", "Q002"]
    assert [it["selected_by"] for it in result] == ["manual", "manual", "auto", "auto"]


def test_khong_ai_tick_thi_may_chon_het(md_file):
    """Trường hợp agent chạy tự động: file chưa ai đụng vào."""
    sach = md_file.parent / "sach.md"
    sach.write_text(SAMPLE_MD.replace("- [x]", "- [ ]").replace("- [X]", "- [ ]"), encoding="utf-8")
    result = parse_selected_md(sach, auto_top=3)
    assert len(result) == 3
    assert all(it["selected_by"] == "auto" for it in result)
    # Xếp theo điểm giảm dần, cùng điểm thì nhiều like hơn trước
    assert [it["id"] for it in result] == ["P002", "Q002", "Q001"]


def test_khong_cat_bot_lua_chon_cua_nguoi(md_file):
    """Đã tick 2 mà xin auto-top 1 → vẫn giữ đủ 2, không vứt bớt ý người."""
    result = parse_selected_md(md_file, auto_top=1)
    assert [it["id"] for it in result] == ["P001", "D001"]


def test_auto_top_lon_hon_so_angle_co_san(md_file):
    """Xin 99 nhưng file chỉ có 5 → trả hết 5, không lỗi."""
    result = parse_selected_md(md_file, auto_top=99)
    assert len(result) == 5


def test_ket_qua_on_dinh_giua_cac_lan_chay(md_file):
    """Chạy lại cùng file phải ra cùng thứ tự — agent chạy tuần không được đảo lung tung."""
    lan_1 = [it["id"] for it in parse_selected_md(md_file, auto_top=4)]
    lan_2 = [it["id"] for it in parse_selected_md(md_file, auto_top=4)]
    assert lan_1 == lan_2


def test_danh_so_thu_tu_lien_tuc(md_file):
    """selected_order phải là 1,2,3... sau khi trộn tick tay + máy chọn."""
    result = parse_selected_md(md_file, auto_top=4)
    assert [it["selected_order"] for it in result] == [1, 2, 3, 4]


def test_file_rong_khong_lam_vo(tmp_path):
    p = tmp_path / "trong.md"
    p.write_text("# Không có angle nào\n", encoding="utf-8")
    assert parse_selected_md(p, auto_top=5) == []
