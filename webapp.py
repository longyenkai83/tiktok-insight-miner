"""Streamlit web UI nội bộ cho nhân viên dùng TikTok Insight Miner.

Chạy:
    streamlit run webapp.py

Hoặc double-click `start-webapp.bat`. Nhân viên access qua LAN IP (vd http://192.168.1.10:8501).

Auth: nếu set WEBAPP_PASSWORD trong .env, sẽ có password gate. Để trống = open access.
Quota: mỗi user (theo tên/mã NV họ tự nhập) tối đa N runs/24h, set MAX_RUNS_PER_USER_PER_DAY trong .env.
Logging: append vào usage_log.csv ở project root.
"""

from __future__ import annotations

import csv
import os
import re
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from tiktok_insight_miner.classifier import classify_comments, save_classified_json
from tiktok_insight_miner.models import Comment
from tiktok_insight_miner.postrun import post_run_hook, resolve_output_dir
from tiktok_insight_miner.reporter import generate_report
from tiktok_insight_miner.scraper import save_comments_json, scrape_tiktok_comments
from tiktok_insight_miner.suggester import generate_brief

MIN_TEXT_LENGTH = 5  # Comment phải dài tối thiểu 5 ký tự

load_dotenv()

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent
LOG_PATH = PROJECT_ROOT / "usage_log.csv"
OUTPUT_ROOT = Path(os.environ.get("DEFAULT_OUTPUT_DIR", "./output"))
if not OUTPUT_ROOT.is_absolute():
    OUTPUT_ROOT = (PROJECT_ROOT / OUTPUT_ROOT).resolve()
MAX_RUNS_PER_USER_PER_DAY = int(os.environ.get("MAX_RUNS_PER_USER_PER_DAY", "20"))
WEBAPP_PASSWORD = os.environ.get("WEBAPP_PASSWORD", "").strip()

NICHE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")

st.set_page_config(
    page_title="Insight Miner — Lắng nghe audience, viết bài chạm sâu",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Custom theme CSS ---
def inject_custom_css() -> None:
    """Inject CSS để override Streamlit default + apply brand identity warm/premium."""
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

        <style>
        /* Global */
        .stApp {
            background-color: #FAFAF7;
        }
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #2D2A26;
            font-weight: 400;
            line-height: 1.6;
        }

        /* Hero header */
        .brand-header {
            text-align: center;
            padding: 2.5rem 0 1.5rem;
            border-bottom: 1px solid #E5DCC8;
            margin-bottom: 2.5rem;
        }
        .brand-title {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 3rem;
            font-weight: 500;
            color: #2D2A26;
            margin: 0;
            letter-spacing: -0.02em;
            line-height: 1.1;
        }
        .brand-accent {
            color: #8B6F47;
            font-style: italic;
        }
        .brand-tagline {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            color: #6B6058;
            margin-top: 0.75rem;
            font-weight: 300;
            letter-spacing: 0.01em;
        }
        .brand-divider {
            width: 60px;
            height: 2px;
            background: linear-gradient(to right, transparent, #8B6F47, transparent);
            margin: 1.25rem auto 0;
        }

        /* Streamlit headings */
        h1, h2, h3 {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-weight: 500;
            color: #2D2A26;
            letter-spacing: -0.015em;
        }
        h1 { font-size: 2.2rem; }
        h2 { font-size: 1.6rem; margin-top: 1.5rem; }
        h3 { font-size: 1.25rem; }

        /* Buttons — primary */
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background-color: #8B6F47;
            color: #FAFAF7;
            border-radius: 10px;
            border: none;
            padding: 0.6rem 1.8rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 0.95rem;
            letter-spacing: 0.01em;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(45, 42, 38, 0.05);
        }
        .stButton > button[kind="primary"]:hover,
        .stDownloadButton > button[kind="primary"]:hover {
            background-color: #6F5736;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(139, 111, 71, 0.25);
        }
        .stButton > button[kind="secondary"],
        .stDownloadButton > button {
            background-color: #FFFFFF;
            color: #2D2A26;
            border: 1px solid #E5DCC8;
            border-radius: 10px;
            padding: 0.55rem 1.5rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .stButton > button[kind="secondary"]:hover {
            border-color: #8B6F47;
            color: #8B6F47;
        }

        /* Inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
            border-radius: 10px !important;
            border: 1px solid #E5DCC8 !important;
            background-color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            color: #2D2A26 !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #8B6F47 !important;
            box-shadow: 0 0 0 3px rgba(139, 111, 71, 0.1) !important;
            outline: none !important;
        }
        .stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label, .stCheckbox label {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            color: #4A413A;
            font-size: 0.9rem;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            border-bottom: 1px solid #E5DCC8;
            padding-bottom: 0;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.6rem 0 0.8rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 0.95rem;
            color: #6B6058;
            background: transparent;
            border: none;
        }
        .stTabs [aria-selected="true"] {
            color: #8B6F47 !important;
            border-bottom: 2px solid #8B6F47 !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #F0EBE2;
            border-right: 1px solid #E5DCC8;
        }
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #6B6058;
            margin-top: 1.5rem;
        }

        /* Info/warning/success boxes */
        [data-testid="stAlert"] {
            border-radius: 12px;
            border: none;
            background-color: #F5F0E5;
            padding: 1rem 1.25rem;
        }
        [data-testid="stAlert"][data-baseweb="notification"] {
            font-family: 'Inter', sans-serif;
            color: #2D2A26;
        }

        /* Metric */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E5DCC8;
            border-radius: 10px;
            padding: 1rem 1.25rem;
        }
        [data-testid="stMetricLabel"] {
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 500;
            color: #6B6058;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.8rem;
            font-weight: 500;
            color: #2D2A26;
        }

        /* Status block */
        [data-testid="stStatusWidget"], div[data-testid="stExpander"] {
            background-color: #FFFFFF;
            border: 1px solid #E5DCC8;
            border-radius: 12px;
        }

        /* Hide Streamlit branding (footer) */
        footer { visibility: hidden; }
        #MainMenu { visibility: hidden; }
        header[data-testid="stHeader"] {
            background-color: transparent;
        }

        /* Custom footer */
        .brand-footer {
            text-align: center;
            padding: 2.5rem 0 1rem;
            margin-top: 3rem;
            border-top: 1px solid #E5DCC8;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: #8B7F73;
            font-weight: 300;
        }
        .brand-footer-accent {
            color: #8B6F47;
            font-weight: 500;
        }

        /* Caption text */
        [data-testid="stCaptionContainer"] {
            font-family: 'Inter', sans-serif;
            color: #6B6058;
            font-size: 0.85rem;
            font-style: italic;
        }

        /* --- Landing sections (About / How-to / FAQ) --- */

        .section-divider {
            height: 1px;
            background: linear-gradient(to right, transparent, #E5DCC8, transparent);
            margin: 3.5rem 0 2.5rem;
        }

        .section-heading {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 2rem;
            font-weight: 500;
            color: #2D2A26;
            margin: 0 0 1.5rem 0;
            letter-spacing: -0.015em;
        }

        /* About card (2 column grid) */
        .about-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2.5rem;
            margin-bottom: 1rem;
        }
        @media (max-width: 768px) {
            .about-grid { grid-template-columns: 1fr; }
        }
        .about-card, .creator-card {
            background: #FFFFFF;
            border: 1px solid #E5DCC8;
            border-radius: 14px;
            padding: 2rem;
        }
        .about-card p {
            font-family: 'Inter', sans-serif;
            color: #4A413A;
            font-size: 0.98rem;
            line-height: 1.7;
            margin: 0 0 1rem 0;
        }
        .about-card strong {
            color: #2D2A26;
            font-weight: 600;
        }
        .about-card h3 {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.4rem;
            color: #2D2A26;
            margin: 1.5rem 0 0.75rem 0;
            font-weight: 500;
        }
        .about-card ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .about-card ul li {
            font-family: 'Inter', sans-serif;
            color: #4A413A;
            padding: 0.5rem 0 0.5rem 1.5rem;
            position: relative;
            line-height: 1.6;
        }
        .about-card ul li::before {
            content: "✦";
            color: #8B6F47;
            position: absolute;
            left: 0;
            top: 0.5rem;
            font-size: 0.85rem;
        }
        .about-divider {
            height: 1px;
            background: #E5DCC8;
            margin: 1.5rem 0;
        }

        /* Creator side card */
        .creator-card {
            background: #F0EBE2;
        }
        .creator-card h3 {
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #6B6058;
            margin: 0 0 1rem 0;
        }
        .creator-row {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.25rem;
        }
        .creator-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(135deg, #8B6F47, #A88660);
            color: #FAFAF7;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.4rem;
            font-weight: 500;
        }
        .creator-name {
            font-family: 'Inter', sans-serif;
            color: #2D2A26;
            font-weight: 500;
            font-size: 1.05rem;
            margin: 0;
        }
        .creator-role {
            font-family: 'Inter', sans-serif;
            color: #6B6058;
            font-size: 0.85rem;
            margin: 0;
        }
        .creator-meta {
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            color: #6B6058;
            padding: 0.5rem 0;
            border-top: 1px solid #E5DCC8;
            display: flex;
            justify-content: space-between;
        }
        .tags-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.75rem;
        }
        .tag-chip {
            background: #FFFFFF;
            color: #6B6058;
            border: 1px solid #E5DCC8;
            border-radius: 999px;
            padding: 0.3rem 0.85rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 500;
        }

        /* How-to steps */
        .steps-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
            margin-top: 1rem;
        }
        @media (max-width: 900px) {
            .steps-grid { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 500px) {
            .steps-grid { grid-template-columns: 1fr; }
        }
        .step-card {
            background: #FFFFFF;
            border: 1px solid #E5DCC8;
            border-radius: 14px;
            padding: 1.5rem;
            transition: all 0.2s;
            position: relative;
            overflow: hidden;
        }
        .step-card:hover {
            border-color: #8B6F47;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(139, 111, 71, 0.1);
        }
        .step-number {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 2.5rem;
            font-weight: 500;
            color: #8B6F47;
            line-height: 1;
            margin-bottom: 0.5rem;
            opacity: 0.7;
        }
        .step-title {
            font-family: 'Cormorant Garamond', Georgia, serif;
            font-size: 1.2rem;
            font-weight: 500;
            color: #2D2A26;
            margin: 0 0 0.5rem 0;
            line-height: 1.3;
        }
        .step-desc {
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            color: #6B6058;
            line-height: 1.55;
            margin: 0;
        }

        /* FAQ expanders */
        details {
            background: #FFFFFF;
            border: 1px solid #E5DCC8;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            transition: all 0.2s;
        }
        details:hover {
            border-color: #8B6F47;
        }
        details[open] {
            background: #FFFFFF;
            border-color: #8B6F47;
        }
        details summary {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            color: #2D2A26;
            cursor: pointer;
            font-size: 0.95rem;
            outline: none;
        }
        details summary::marker {
            color: #8B6F47;
        }
        details p {
            font-family: 'Inter', sans-serif;
            color: #4A413A;
            font-size: 0.92rem;
            line-height: 1.65;
            margin: 0.75rem 0 0 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header() -> None:
    """Render brand header — hero giới thiệu tool."""
    st.markdown(
        """
        <div class="brand-header">
            <h1 class="brand-title">Insight <span class="brand-accent">Miner</span></h1>
            <p class="brand-tagline">Lắng nghe audience thật — viết bài chạm sâu, không sáo rỗng</p>
            <div class="brand-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_brand_footer() -> None:
    """Footer nhẹ ở cuối page."""
    st.markdown(
        """
        <div class="brand-footer">
            Insight Miner — <span class="brand-footer-accent">Lê Nguyễn Tuấn</span> ·
            Dành cho phụ nữ làm chủ chuyên môn
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_about_section() -> None:
    """About + Creator + Tags (2-column grid). HTML compact (no leading space, no blank line)
    để tránh Streamlit markdown parser break."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    html = (
        '<div class="about-grid">'
        '<div class="about-card">'
        '<h2 class="section-heading" style="margin-top: 0;">Về tool này</h2>'
        '<p>Insight Miner biến comment thật của audience trên TikTok, Facebook, YouTube... thành <strong>kho insight có taxonomy + scoring</strong> — sẵn sàng cho việc viết bài chạm sâu, không sáo rỗng.</p>'
        '<p>Phù hợp cho <strong>phụ nữ làm chủ chuyên môn 27-54</strong> — coach, marketer, agency, brand owner. Tool không viết bài thay, nó giúp em <strong>nghe đúng nỗi đau khán giả trước khi viết</strong>.</p>'
        '<h3>Điểm nổi bật</h3>'
        '<ul>'
        '<li><strong>Liệt kê insight</strong> không bỏ sót — phân loại pain / desire / question / objection từ comment thật</li>'
        '<li><strong>Sắp xếp theo 9-12 nhóm vấn đề</strong> đặc trưng ngành, mỗi nhóm có score demand</li>'
        '<li><strong>Anh chọn insight muốn dùng</strong> bằng cách tick checkbox — AI không tự quyết</li>'
        '<li><strong>Handoff sang xưởng viết bài</strong> (CoWork) qua Google Drive — máy nào cũng dùng được</li>'
        '<li><strong>Hỗ trợ 2 nguồn data</strong>: scrape TikTok tự động HOẶC paste comment thủ công (FB, YT, group...)</li>'
        '</ul>'
        '<h3>Dùng cho ai</h3>'
        '<ul>'
        '<li>Coach / mentor đang xây kênh personal brand</li>'
        '<li>Marketer cá nhân research audience trước khi viết</li>'
        '<li>Agency content cần hệ thống hoá research insight</li>'
        '<li>Brand owner muốn nghe khán giả thay vì đoán</li>'
        '</ul>'
        '<div class="about-divider"></div>'
        '<div style="display: flex; gap: 2rem; font-family: Inter, sans-serif; font-size: 0.85rem; color: #6B6058;">'
        '<div><div style="text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.3rem;">Cost</div><div>~$0.05-0.30/run</div></div>'
        '<div><div style="text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.3rem;">Thời gian</div><div>2-5 phút/run</div></div>'
        '<div><div style="text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 0.3rem;">Phiên bản</div><div>v0.4 (2026-05)</div></div>'
        '</div>'
        '</div>'
        '<div>'
        '<div class="creator-card">'
        '<h3>Người làm</h3>'
        '<div class="creator-row">'
        '<div class="creator-avatar">T</div>'
        '<div>'
        '<p class="creator-name">Lê Nguyễn Tuấn</p>'
        '<p class="creator-role">Marketer · 10+ năm</p>'
        '</div>'
        '</div>'
        '<div class="creator-meta"><span>Build cho cộng đồng coaching cùng chị Hiền</span></div>'
        '</div>'
        '<div class="creator-card" style="margin-top: 1rem;">'
        '<h3>Phù hợp với</h3>'
        '<div class="tags-row">'
        '<span class="tag-chip">Coaching</span>'
        '<span class="tag-chip">Personal Brand</span>'
        '<span class="tag-chip">Content Marketing</span>'
        '<span class="tag-chip">Research Audience</span>'
        '<span class="tag-chip">TikTok</span>'
        '<span class="tag-chip">Facebook</span>'
        '<span class="tag-chip">Insight Mining</span>'
        '<span class="tag-chip">Phụ nữ kinh doanh</span>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_how_to_use() -> None:
    """Hướng dẫn sử dụng 4 bước — card grid. HTML compact format."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    html = (
        '<h2 class="section-heading">Hướng dẫn sử dụng</h2>'
        '<p style="font-family: Inter, sans-serif; color: #6B6058; font-size: 0.95rem; margin-bottom: 0;">4 bước, làm 1 lần là quen. Mỗi run mất 2-5 phút.</p>'
        '<div class="steps-grid">'
        '<div class="step-card">'
        '<div class="step-number">01</div>'
        '<h3 class="step-title">Đặt tên niche</h3>'
        '<p class="step-desc">Trong ô <em>Niche slug</em>, gõ tên ngắn cho ngành/đối tượng em đang nghiên cứu. Ví dụ: <code>kinh-doanh-27-45</code>, <code>skincare-acne</code>. Dùng dấu gạch ngang, không khoảng trắng.</p>'
        '</div>'
        '<div class="step-card">'
        '<div class="step-number">02</div>'
        '<h3 class="step-title">Chọn cách lấy data</h3>'
        '<p class="step-desc"><strong>Tab "Scrape TikTok"</strong>: paste 3-5 URL video — tool tự lấy comment.<br><br><strong>Tab "Paste comment"</strong>: copy comment từ Facebook, YouTube, group... paste mỗi dòng 1 cái.</p>'
        '</div>'
        '<div class="step-card">'
        '<div class="step-number">03</div>'
        '<h3 class="step-title">Bấm "Chạy pipeline"</h3>'
        '<p class="step-desc">Tool sẽ phân loại comment thành 7 nhóm (pain, desire, question...) và tạo báo cáo + content angle brief.<br><br>Chờ 2-5 phút. <strong>Đừng đóng tab.</strong></p>'
        '</div>'
        '<div class="step-card">'
        '<div class="step-number">04</div>'
        '<h3 class="step-title">Tải file insight</h3>'
        '<p class="step-desc">Khi xong, em tải <code>report.md</code> + <code>brief.md</code> về xem.<br><br>Hoặc đợi <strong>CoWork tự pull qua Google Drive</strong> — viết bài bằng voice riêng của em.</p>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_faq() -> None:
    """FAQ section — câu hỏi thường gặp. HTML compact format."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-heading">Câu hỏi thường gặp</h2>', unsafe_allow_html=True)
    html = (
        '<details>'
        '<summary>Tool này có miễn phí không?</summary>'
        '<p>Bản nội bộ này miễn phí cho thành viên cộng đồng coaching cùng chị Hiền. Cost thực tế là API (~$0.05-0.30 cho mỗi lần chạy, tuỳ số comment + có generate brief hay không) — anh Tuấn đang trả hộ trong giai đoạn beta.</p>'
        '</details>'
        '<details>'
        '<summary>Em cần bao nhiêu comment là đủ để có insight tốt?</summary>'
        '<p>Tối thiểu <strong>30 comment</strong> để có distribution đáng tin. Lý tưởng <strong>80-150 comment</strong> — đủ data để phân loại 9 nhóm vấn đề. Dưới 30 comment vẫn chạy được nhưng score và distribution dễ lệch.</p>'
        '</details>'
        '<details>'
        '<summary>Em không có TikTok URL — chỉ có comment Facebook thì làm sao?</summary>'
        '<p>Dùng tab <strong>"Paste comment thủ công"</strong>. Copy từng comment từ FB (hoặc YouTube, Zalo, group...) — mỗi dòng 1 cái — paste vào ô. Chọn "Nguồn" là <em>facebook</em> để trace sau. Tool sẽ phân tích y như comment TikTok.</p>'
        '</details>'
        '<details>'
        '<summary>Sau khi có insight, em viết bài thế nào?</summary>'
        '<p>File <code>report.md</code> cho em <strong>tổng quan 7 nhóm bucket</strong> + top quote mỗi nhóm. File <code>brief.md</code> (nếu bật) cho em <strong>10 content angle đã được Claude đề xuất</strong> — kèm hook + script outline + CTA.<br><br>Nếu em là khách của chị Hiền dùng CoWork — insight tự pull sang đó, chị Hiền dẫn em viết theo voice riêng.</p>'
        '</details>'
        '<details>'
        '<summary>Insight được lưu ở đâu? Em có truy cập lại được không?</summary>'
        '<p>Mỗi run lưu vào folder riêng theo niche + ngày — em có thể tải file đầy đủ ngay sau khi chạy xong. Quota nội bộ: mỗi người 20 runs/24h. Anh Tuấn quản trị giúp.</p>'
        '</details>'
        '<details>'
        '<summary>Tool có dùng được cho ngành khác ngoài coaching không?</summary>'
        '<p>Có. Hiện tại tool config sẵn cho niche <em>"phụ nữ kinh doanh 27-45"</em> (chị Hiền). Để dùng cho ngành khác (skincare, mẹ-bé, BĐS, đầu tư...) cần config taxonomy riêng — anh Tuấn hỗ trợ setup trong 30 phút.</p>'
        '</details>'
        '<details>'
        '<summary>Em gặp lỗi khi chạy, làm sao?</summary>'
        '<p>Nếu pipeline báo lỗi (timeout, không scrape được, classify fail...) — chụp màn hình + thông báo cho anh Tuấn qua Zalo/chat.<br><br>Một số lỗi thường gặp: URL TikTok không hợp lệ (phải dùng URL video đầy đủ, không phải link rút gọn), comment paste có ký tự đặc biệt, hoặc API quota hết.</p>'
        '</details>'
    )
    st.markdown(html, unsafe_allow_html=True)


# --- Auth gate ---
def check_auth() -> bool:
    """Password gate đơn giản. Skip nếu WEBAPP_PASSWORD trống trong .env."""
    if not WEBAPP_PASSWORD:
        return True
    if st.session_state.get("authenticated"):
        return True

    st.title("🔒 Đăng nhập")
    st.caption("Hỏi sếp Tuấn để lấy password.")
    pw = st.text_input("Password", type="password", key="pw_input")
    if st.button("Vào"):
        if pw == WEBAPP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Sai password.")
    return False


# --- Logging + quota ---
LOG_HEADER = [
    "timestamp", "user", "niche", "num_urls", "num_comments",
    "with_brief", "duration_s", "status", "cost_est_usd",
]


def log_run(
    user: str, niche: str, num_urls: int, num_comments: int,
    with_brief: bool, duration_s: float, status: str, cost_est: float,
) -> None:
    # utf-8-sig (BOM) để Excel mở đúng tiếng Việt; tránh mojibake (TuÃ¢Ìn → Tuấn)
    is_new = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(LOG_HEADER)
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            user, niche, num_urls, num_comments,
            with_brief, round(duration_s, 1), status, round(cost_est, 4),
        ])


def get_user_runs_24h(user: str) -> int:
    """Đếm runs success của user trong 24h gần nhất."""
    if not LOG_PATH.exists():
        return 0
    cutoff = datetime.now() - timedelta(hours=24)
    count = 0
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("user") != user:
                continue
            try:
                ts = datetime.fromisoformat(row["timestamp"])
            except (ValueError, KeyError):
                continue
            if ts >= cutoff and row.get("status") == "success":
                count += 1
    return count


def estimate_cost(num_comments: int, with_brief: bool, mode: str = "scrape") -> float:
    """Rough estimate (USD): Apify $0.001/cmt + Haiku classify $0.0003/cmt + brief $0.02.

    Mode 'paste' → không có Apify cost (chỉ classify + brief).
    """
    apify = num_comments * 0.001 if mode == "scrape" else 0.0
    return apify + num_comments * 0.0003 + (0.02 if with_brief else 0.0)


def parse_text_to_comments(text: str, platform: str = "manual") -> list[Comment]:
    """Parse text (mỗi dòng 1 comment) → list Comment objects.

    Args:
        text: raw text, mỗi dòng 1 comment. Bỏ qua dòng rỗng + dòng <5 ký tự.
        platform: ghi vào raw['platform'] để trace nguồn (facebook, youtube, manual...)

    Returns:
        List Comment với id paste-NNNN, default likes=0, author=unknown.
    """
    comments: list[Comment] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for idx, line in enumerate(lines, 1):
        if len(line) < MIN_TEXT_LENGTH:
            continue
        comments.append(Comment(
            id=f"paste-{idx:04d}",
            text=line,
            author="unknown",
            likes=0,
            reply_count=0,
            created_at="",
            video_url="",
            raw={"platform": platform, "imported_from": "webapp_paste"},
        ))
    return comments


# --- Pipeline ---
def run_pipeline(
    urls: list[str],
    niche: str,
    user: str,
    max_comments: int,
    with_brief: bool,
    num_angles: int,
    status,
    comments_paste: str | None = None,
    platform: str = "manual",
) -> dict:
    """Chạy pipeline, update progress qua status block. Trả về dict paths + counts.

    2 mode:
    - Scrape TikTok: pass `urls`, `comments_paste=None`. Output → output/<niche>/<date>/
    - Paste manual: pass `comments_paste`, platform. Output → output/<niche>/<date>__manual-import/
    """
    today = date.today().isoformat()
    mode = "paste" if comments_paste else "scrape"

    if mode == "paste":
        # Convention giống tim import-comments: thêm suffix __manual-import
        output_dir = OUTPUT_ROOT / niche / f"{today}__manual-import"
    else:
        output_dir = resolve_output_dir(OUTPUT_ROOT, niche, today, user)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_path = output_dir / "raw_comments.json"
    classified_path = output_dir / "classified.json"
    report_path = output_dir / "report.md"
    brief_path = output_dir / "brief.md"

    # Stage 1: scrape HOẶC parse paste
    if mode == "paste":
        status.update(label="✍️ [1/4] Đang parse comment paste...", state="running")
        comments = parse_text_to_comments(comments_paste, platform=platform)
        save_comments_json(comments, raw_path)
        status.write(f"✓ Parsed **{len(comments)}** comments từ paste (platform: {platform})")
        if not comments:
            raise RuntimeError(
                "Không parse được comment nào — kiểm tra paste có nội dung không + mỗi dòng tối thiểu 5 ký tự."
            )
    else:
        status.update(label="🔍 [1/4] Đang scrape TikTok comments (Apify)...", state="running")
        comments = scrape_tiktok_comments(urls, max_comments_per_video=max_comments)
        save_comments_json(comments, raw_path)
        status.write(f"✓ Scraped **{len(comments)}** comments từ {len(urls)} URLs")
        if not comments:
            raise RuntimeError("Không scrape được comment nào — URLs có hợp lệ không?")

    # Stage 2: classify
    status.update(
        label=f"🤖 [2/4] Đang classify {len(comments)} comments (Claude)... "
              f"~{(len(comments) // 20 + 1) * 7}s",
    )
    classified = classify_comments(comments)
    save_classified_json(classified, classified_path)
    status.write(f"✓ Classified **{len(classified)}** comments")

    # Stage 3: report
    status.update(label="📊 [3/4] Đang generate report...")
    generate_report(classified, report_path)
    status.write(f"✓ Report saved")

    # Stage 4: brief (optional)
    angles_count = 0
    if with_brief:
        status.update(label="🎬 [4/4] Đang generate content angle brief (Claude, 30-60s)...")
        angles = generate_brief(classified, brief_path, num_angles=num_angles)
        angles_count = len(angles)
        status.write(f"✓ Generated **{angles_count}** content angles")

    status.update(label="🎉 Pipeline complete!", state="complete")
    return {
        "output_dir": output_dir,
        "raw_path": raw_path,
        "classified_path": classified_path,
        "report_path": report_path,
        "brief_path": brief_path if with_brief else None,
        "num_comments": len(comments),
        "num_classified": len(classified),
        "num_angles": angles_count,
    }


# --- UI ---
def render_sidebar() -> tuple[str, int, bool, int]:
    """Render sidebar: user info, settings, recent runs."""
    with st.sidebar:
        st.header("👤 Người dùng")
        user = st.text_input(
            "Tên / mã NV (bắt buộc)",
            value=st.session_state.get("user", ""),
            placeholder="vd: nv_minh, marketing_lan",
            help="Dùng để track usage và quota cá nhân.",
        ).strip()
        st.session_state.user = user

        if user:
            runs = get_user_runs_24h(user)
            remaining = MAX_RUNS_PER_USER_PER_DAY - runs
            st.metric(
                "Runs trong 24h",
                f"{runs}/{MAX_RUNS_PER_USER_PER_DAY}",
                delta=f"{remaining} còn lại" if remaining > 0 else "Hết quota",
                delta_color="normal" if remaining > 0 else "inverse",
            )

        st.divider()
        st.header("⚙️ Settings")
        max_comments = st.slider(
            "Max comments / video", 10, 500, 100, 10,
            help="Càng nhiều insight càng đầy đủ nhưng cost cao hơn.",
        )
        with_brief = st.checkbox(
            "Generate content angle brief", value=True,
            help="Stage 4 — Claude generate hook + script outline + CTA.",
        )
        num_angles = st.slider(
            "Số content angle", 5, 20, 10,
            disabled=not with_brief,
        )

        st.divider()
        st.header("📚 10 runs gần nhất")
        if LOG_PATH.exists():
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))[-10:][::-1]
            for r in rows:
                ts = r["timestamp"][:16].replace("T", " ")
                icon = "✅" if r.get("status") == "success" else "❌"
                st.caption(
                    f"{icon} `{ts}` **{r['user']}** · {r['niche']} · "
                    f"{r['num_comments']}cmt · ${r['cost_est_usd']}"
                )
        else:
            st.caption("_Chưa có run nào._")

    return user, max_comments, with_brief, num_angles


def render_results(result: dict, with_brief: bool, duration: float) -> None:
    """Hiển thị download buttons + inline render."""
    st.success(
        f"🎉 Done in **{duration:.0f}s** — "
        f"{result['num_comments']} comments classified"
        + (f", {result['num_angles']} angles" if with_brief else "")
    )

    st.subheader("📁 Download files")
    cols = st.columns(4 if with_brief else 3)
    files_to_show = [
        ("📊 report.md", result["report_path"], "text/markdown"),
        ("💾 classified.json", result["classified_path"], "application/json"),
        ("📦 raw_comments.json", result["raw_path"], "application/json"),
    ]
    if with_brief and result["brief_path"]:
        files_to_show.insert(1, ("🎬 brief.md", result["brief_path"], "text/markdown"))

    for col, (label, path, mime) in zip(cols, files_to_show):
        with col:
            st.download_button(
                f"⬇️ {label}",
                data=path.read_bytes(),
                file_name=path.name,
                mime=mime,
                use_container_width=True,
            )

    st.subheader("📖 Xem nhanh")
    tab_labels = ["📊 Report"]
    if with_brief:
        tab_labels.append("🎬 Brief")
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        st.markdown(result["report_path"].read_text(encoding="utf-8"))
    if with_brief:
        with tabs[1]:
            st.markdown(result["brief_path"].read_text(encoding="utf-8"))


def _render_landing_sections() -> None:
    """Render About + How-to + FAQ + Footer. Luôn chạy ở cuối main() qua finally block."""
    render_about_section()
    render_how_to_use()
    render_faq()
    render_brand_footer()


def main() -> None:
    inject_custom_css()

    if not check_auth():
        return

    try:
        render_brand_header()
        st.caption(
            f"Quét comment audience → phân loại insight → handoff cho viết bài. "
            f"Quota nội bộ: {MAX_RUNS_PER_USER_PER_DAY} runs/người/24h."
        )

        user, max_comments, with_brief, num_angles = render_sidebar()

        if not user:
            st.warning("👈 Nhập tên/mã ở sidebar trước khi tiếp tục.")
            return

        runs_today = get_user_runs_24h(user)
        if runs_today >= MAX_RUNS_PER_USER_PER_DAY:
            st.error(
                f"🚫 Em đã chạy **{runs_today} runs** trong 24h qua — "
                f"vượt quota {MAX_RUNS_PER_USER_PER_DAY}. Đợi 24h hoặc liên hệ anh Tuấn."
            )
            return

        st.subheader("1️⃣ Input")

        # Niche slug — chung cho cả 2 mode
        niche = st.text_input(
            "Niche slug",
            placeholder="vd: skincare-acne, kinh-doanh-27-45",
            help="kebab-case, không khoảng trắng. Output → output/<niche>/<today>[__manual-import]/",
        ).strip().lower()

        # 2 tab: scrape URL HOẶC paste comment
        tab_url, tab_paste = st.tabs([
            "🎬 Scrape TikTok URL (auto Apify)",
            "✍️ Paste comment thủ công (FB / YT / nguồn khác)",
        ])

        submit = False
        urls_list: list[str] = []
        comments_paste = ""
        platform = "manual"
        source_mode = "scrape"
        valid_lines: list[str] = []

        with tab_url:
            urls_text = st.text_area(
                "TikTok video URLs (mỗi dòng 1 cái, # = comment)",
                placeholder=(
                    "https://www.tiktok.com/@user1/video/123\n"
                    "https://www.tiktok.com/@user2/video/456"
                ),
                height=140,
                key="urls_input",
            )
            urls_list = [
                u.strip() for u in urls_text.splitlines()
                if u.strip() and not u.strip().startswith("#")
            ]

            # Cost preview cho scrape mode
            if urls_list:
                est_total = len(urls_list) * max_comments
                est_cost = estimate_cost(est_total, with_brief, mode="scrape")
                st.info(
                    f"📊 **Preview**: {len(urls_list)} videos × {max_comments} = ~{est_total} comments. "
                    f"**Cost estimate ~${est_cost:.2f}** (Apify + Claude). "
                    f"Pipeline mất ~{1 + len(urls_list) * 0.5 + (1 if with_brief else 0):.0f}-{2 + len(urls_list) * 1 + (1 if with_brief else 0):.0f} phút."
                )

            submit_url = st.button(
                "🚀 Chạy pipeline (Scrape TikTok)",
                type="primary",
                disabled=not (niche and urls_list),
                use_container_width=True,
                key="submit_url",
            )
            if submit_url:
                submit = True
                source_mode = "scrape"

        with tab_paste:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                comments_paste = st.text_area(
                    "Paste comment (mỗi dòng 1 cái, tối thiểu 5 ký tự — dòng ngắn bị skip)",
                    placeholder=(
                        "mệt quá em ơi, làm sao giờ\n"
                        "kinh doanh tháng này lại lỗ tiếp\n"
                        "không biết bắt đầu xây kênh từ đâu\n"
                        "..."
                    ),
                    height=300,
                    key="paste_input",
                    help=(
                        "Mỗi dòng = 1 comment. Copy từ Facebook, YouTube, group, fanpage... "
                        "Không cần header CSV. Comment <5 ký tự bị skip."
                    ),
                )
            with col_b:
                platform = st.selectbox(
                    "Nguồn comment",
                    ["manual", "facebook", "youtube", "fb_group", "fanpage", "zalo_oa", "tiktok_manual", "other"],
                    index=0,
                    key="platform_select",
                    help="Ghi vào field `platform` của mỗi comment để trace nguồn sau này.",
                )

            # Đếm số comment hợp lệ
            valid_lines = [
                l.strip() for l in comments_paste.splitlines()
                if l.strip() and len(l.strip()) >= MIN_TEXT_LENGTH
            ]

            if valid_lines:
                est_cost = estimate_cost(len(valid_lines), with_brief, mode="paste")
                st.info(
                    f"📊 **Preview**: {len(valid_lines)} comments hợp lệ. "
                    f"**Cost estimate ~${est_cost:.2f}** (chỉ Claude — không có Apify). "
                    f"Pipeline mất ~{max(1, len(valid_lines) // 30)}-{max(2, len(valid_lines) // 15)} phút."
                )
            elif comments_paste:
                st.warning("⚠️ Không có dòng nào ≥5 ký tự. Check lại paste.")

            submit_paste = st.button(
                "🚀 Chạy pipeline (Paste manual)",
                type="primary",
                disabled=not (niche and valid_lines),
                use_container_width=True,
                key="submit_paste",
            )
            if submit_paste:
                submit = True
                source_mode = "paste"

        # Nếu chưa submit → return ngay, finally block sẽ render landing sections
        if not submit:
            return

        # Validate niche slug (common)
        if not NICHE_SLUG_RE.match(niche):
            st.error(
                f"❌ Niche slug không hợp lệ: '{niche}'. "
                "Dùng kebab-case (a-z, 0-9, dấu -). Ví dụ: `skincare-acne`."
            )
            return

        # Run pipeline
        st.subheader("2️⃣ Đang chạy")
        if source_mode == "scrape":
            st.caption("⏰ Pipeline mất 2-5 phút (scrape TikTok). **Đừng đóng tab hoặc bấm refresh.**")
        else:
            st.caption(f"⏰ Pipeline mất 1-3 phút ({len(valid_lines)} comment paste). **Đừng đóng tab.**")

        start_time = time.time()
        with st.status("Đang khởi động...", expanded=True) as status:
            try:
                if source_mode == "paste":
                    result = run_pipeline(
                        urls=[], niche=niche, user=user,
                        max_comments=max_comments, with_brief=with_brief,
                        num_angles=num_angles, status=status,
                        comments_paste=comments_paste, platform=platform,
                    )
                else:
                    result = run_pipeline(
                        urls=urls_list, niche=niche, user=user,
                        max_comments=max_comments, with_brief=with_brief,
                        num_angles=num_angles, status=status,
                    )
                duration = time.time() - start_time
                cost = estimate_cost(result["num_comments"], with_brief, mode=source_mode)
                log_run(
                    user=user, niche=niche,
                    num_urls=len(urls_list) if source_mode == "scrape" else 0,
                    num_comments=result["num_comments"],
                    with_brief=with_brief, duration_s=duration,
                    status="success", cost_est=cost,
                )
                # Post-run hooks: update _index.md + LATEST.md (best-effort, không crash UI)
                try:
                    post_run_hook(
                        project_root=PROJECT_ROOT,
                        output_root=OUTPUT_ROOT,
                        output_dir=result["output_dir"],
                        classified_path=result["classified_path"],
                        niche=niche,
                        user=user,
                        num_videos=len(urls_list),
                        with_brief=with_brief,
                        duration_s=duration,
                        cost_est_usd=cost,
                        brief_path=result.get("brief_path"),
                    )
                except Exception as hook_err:
                    st.warning(f"Index/LATEST update lỗi (không ảnh hưởng kết quả): {hook_err}")

                st.subheader("3️⃣ Kết quả")
                render_results(result, with_brief, duration)

            except Exception as e:
                duration = time.time() - start_time
                log_run(
                    user=user, niche=niche,
                    num_urls=len(urls_list) if source_mode == "scrape" else 0,
                    num_comments=0,
                    with_brief=with_brief, duration_s=duration,
                    status="error", cost_est=0.0,
                )
                status.update(label=f"❌ Lỗi: {type(e).__name__}", state="error")
                st.error(f"Pipeline lỗi: {e}")
                st.exception(e)

    finally:
        # Always render landing sections — chạy DÙ return ở đâu trong try block
        _render_landing_sections()


if __name__ == "__main__":
    main()
