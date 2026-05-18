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
from tiktok_insight_miner.cowork_exporter import (
    export_for_cowork,
    upload_run_files_to_drive_api,
    upload_run_files_to_drive_local,
)
from tiktok_insight_miner.cowork_pack import (
    generate_cowork_pack,
    parse_brief_angles,
    save_cowork_pack,
)
from tiktok_insight_miner.insight_bank import build_insight_bank
from tiktok_insight_miner.models import Comment
from tiktok_insight_miner.postrun import post_run_hook, resolve_output_dir
from tiktok_insight_miner.reporter import generate_report
from tiktok_insight_miner.scraper import save_comments_json, scrape_tiktok_comments
from tiktok_insight_miner.selection import run_selection
from tiktok_insight_miner.strategy_analyst import generate_strategy_analysis
from tiktok_insight_miner.suggester import generate_brief

MIN_TEXT_LENGTH = 5  # Comment phải dài tối thiểu 5 ký tự

load_dotenv()

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = Path(os.environ.get("DEFAULT_OUTPUT_DIR", "./output"))
if not OUTPUT_ROOT.is_absolute():
    OUTPUT_ROOT = (PROJECT_ROOT / OUTPUT_ROOT).resolve()
# Lưu log trong OUTPUT_ROOT để Railway Volume persist (cùng mount với output files)
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
LOG_PATH = OUTPUT_ROOT / "usage_log.csv"
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
# v0.6: thêm output_dir để click history → restore download buttons
LOG_HEADER = [
    "timestamp", "user", "niche", "num_urls", "num_comments",
    "with_brief", "duration_s", "status", "cost_est_usd", "output_dir",
]


def _infer_output_dir_from_log(row: dict) -> str:
    """v0.6 fix: cho rows cũ KHÔNG có output_dir, infer path từ niche + date.

    Convention thử (theo postrun.resolve_output_dir + paste mode):
    - output/<niche>/<date>/
    - output/<niche>/<date>__<safe_user>/
    - output/<niche>/<date>__manual-import/  (paste mode)

    Trả path đầu tiên tồn tại + có ≥1 file. Trả "" nếu không tìm thấy.
    """
    niche = (row.get("niche") or "").strip()
    user = (row.get("user") or "").strip()
    ts = (row.get("timestamp") or "").strip()
    if not niche or not ts:
        return ""
    try:
        run_date = ts[:10]  # YYYY-MM-DD
    except Exception:
        return ""

    safe_user = re.sub(r"[^a-z0-9_-]", "-", user.lower()) or "anon"
    candidates = [
        OUTPUT_ROOT / niche / run_date,
        OUTPUT_ROOT / niche / f"{run_date}__{safe_user}",
        OUTPUT_ROOT / niche / f"{run_date}__manual-import",
    ]
    for path in candidates:
        if path.exists() and any(path.iterdir()):
            return str(path)
    return ""


def _migrate_log_header_if_needed() -> None:
    """v0.6 fix: nếu CSV cũ có header thiếu column output_dir → migrate.

    Re-write file với header mới + pad rows cũ với output_dir="" để
    csv.DictReader đọc đúng. Idempotent — chỉ chạy 1 lần.
    """
    if not LOG_PATH.exists():
        return
    try:
        with open(LOG_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            existing_header = next(reader, None)
            if not existing_header or "output_dir" in existing_header:
                return  # OK, không cần migrate
            data_rows = list(reader)

        # Migrate: write new header + pad rows
        with open(LOG_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(LOG_HEADER)
            target_len = len(LOG_HEADER)
            for row in data_rows:
                # Pad missing columns với chuỗi rỗng (output_dir của row cũ = "")
                if len(row) < target_len:
                    row = row + [""] * (target_len - len(row))
                elif len(row) > target_len:
                    row = row[:target_len]
                writer.writerow(row)
    except Exception as e:
        # Migration fail không fail pipeline — log warning thôi
        import logging
        logging.getLogger(__name__).warning("CSV log migrate failed: %s", e)


def log_run(
    user: str, niche: str, num_urls: int, num_comments: int,
    with_brief: bool, duration_s: float, status: str, cost_est: float,
    output_dir: str | None = None,
) -> None:
    # utf-8-sig (BOM) để Excel mở đúng tiếng Việt; tránh mojibake (TuÃ¢Ìn → Tuấn)
    # v0.6: auto-migrate header nếu file cũ thiếu column output_dir
    _migrate_log_header_if_needed()

    is_new = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(LOG_HEADER)
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            user, niche, num_urls, num_comments,
            with_brief, round(duration_s, 1), status, round(cost_est, 4),
            output_dir or "",
        ])


def get_user_runs_24h(user: str) -> int:
    """Đếm runs success của user trong 24h gần nhất."""
    if not LOG_PATH.exists():
        return 0
    cutoff = datetime.now() - timedelta(hours=24)
    count = 0
    with open(LOG_PATH, "r", encoding="utf-8-sig") as f:
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


def estimate_cost(
    num_comments: int,
    with_brief: bool,
    mode: str = "scrape",
    with_strategy: bool = False,
) -> float:
    """Rough estimate (USD): Apify $0.001/cmt + Haiku classify $0.0003/cmt +
    brief $0.02 + strategy $0.07.

    Mode 'paste' → không có Apify cost (chỉ classify + brief + strategy).
    """
    apify = num_comments * 0.001 if mode == "scrape" else 0.0
    brief = 0.02 if with_brief else 0.0
    strategy = 0.07 if (with_brief and with_strategy) else 0.0
    return apify + num_comments * 0.0003 + brief + strategy


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
    with_strategy: bool = True,
) -> dict:
    """Chạy pipeline, update progress qua status block. Trả về dict paths + counts.

    2 mode:
    - Scrape TikTok: pass `urls`, `comments_paste=None`. Output → output/<niche>/<date>/
    - Paste manual: pass `comments_paste`, platform. Output → output/<niche>/<date>__manual-import/

    v0.5 (Stage 5): with_strategy → generate phan-tich-toan-dien.md (Canvas + Chấm brief + Synthesis)
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
    strategy_path = output_dir / "phan-tich-toan-dien.md"

    # Tính tổng stages cho label progress
    total_stages = 3 + (1 if with_brief else 0) + (1 if (with_brief and with_strategy) else 0)

    # Stage 1: scrape HOẶC parse paste
    if mode == "paste":
        status.update(label=f"✍️ [1/{total_stages}] Đang parse comment paste...", state="running")
        comments = parse_text_to_comments(comments_paste, platform=platform)
        save_comments_json(comments, raw_path)
        status.write(f"✓ Parsed **{len(comments)}** comments từ paste (platform: {platform})")
        if not comments:
            raise RuntimeError(
                "Không parse được comment nào — kiểm tra paste có nội dung không + mỗi dòng tối thiểu 5 ký tự."
            )
    else:
        status.update(label=f"🔍 [1/{total_stages}] Đang scrape TikTok comments (Apify)...", state="running")
        comments = scrape_tiktok_comments(urls, max_comments_per_video=max_comments)
        save_comments_json(comments, raw_path)
        status.write(f"✓ Scraped **{len(comments)}** comments từ {len(urls)} URLs")
        if not comments:
            raise RuntimeError("Không scrape được comment nào — URLs có hợp lệ không?")

    # Stage 2: classify
    status.update(
        label=f"🤖 [2/{total_stages}] Đang classify {len(comments)} comments (Claude)... "
              f"~{(len(comments) // 20 + 1) * 7}s",
    )
    classified = classify_comments(comments)
    save_classified_json(classified, classified_path)
    status.write(f"✓ Classified **{len(classified)}** comments")

    # Stage 3: report
    status.update(label=f"📊 [3/{total_stages}] Đang generate report...")
    generate_report(classified, report_path)
    status.write(f"✓ Report saved")

    # Stage 4: brief (optional)
    angles_count = 0
    if with_brief:
        status.update(label=f"🎬 [4/{total_stages}] Đang generate content angle brief (Claude Opus, 30-60s)...")
        angles = generate_brief(classified, brief_path, num_angles=num_angles)
        angles_count = len(angles)
        status.write(f"✓ Generated **{angles_count}** content angles")

    # Stage 5: strategy analysis (chỉ chạy nếu with_brief=True vì cần brief làm input)
    strategy_generated = False
    if with_brief and with_strategy:
        status.update(label=f"🧠 [5/{total_stages}] Đang phân tích strategy (Canvas + Chấm brief + Synthesis, Opus, 30-60s)...")
        try:
            generate_strategy_analysis(
                classified=classified,
                brief_md_path=brief_path,
                output_path=strategy_path,
                niche_slug=niche,
            )
            strategy_generated = True
            status.write(f"✓ Strategy analysis saved (Canvas + Chấm brief + Synthesis)")
        except Exception as e:
            # Strategy fail KHÔNG fail toàn pipeline — brief + report đã có
            status.write(f"⚠️ Strategy analysis lỗi (brief + report vẫn OK): {e}")

    # v0.5: Auto-upload run files lên Drive (F1 structure: runs/niche/date/time-user/)
    # Best-effort: nếu Drive config có. Không fail pipeline nếu upload fail.
    drive_run_info: dict | None = None
    drive_folder_id = os.environ.get("INSIGHTS_PACK_DRIVE_FOLDER_ID", "").strip()
    gdrive_json = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON", "").strip()
    drive_local_dir = os.environ.get("INSIGHTS_PACK_DRIVE_DIR", "").strip()

    files_to_upload: dict[str, Path] = {
        "report": report_path,
    }
    if with_brief and brief_path.exists():
        files_to_upload["brief"] = brief_path
    if strategy_generated and strategy_path.exists():
        files_to_upload["strategy"] = strategy_path

    if drive_folder_id and gdrive_json:
        status.update(label="☁️ Đang upload run files lên Google Drive...")
        try:
            drive_run_info = upload_run_files_to_drive_api(
                files=files_to_upload,
                niche_slug=niche,
                user=user,
                root_folder_id=drive_folder_id,
                service_account_json=gdrive_json,
            )
            if drive_run_info:
                num_up = len(drive_run_info.get("uploaded_files", []))
                num_skip = len(drive_run_info.get("skipped", []))
                status.write(f"✓ Drive uploaded {num_up} files (skipped {num_skip}) → folder `{drive_run_info.get('folder_path')}`")
        except Exception as e:
            status.write(f"⚠️ Drive upload lỗi (file vẫn save local): {e}")
    elif drive_local_dir:
        status.update(label="📂 Đang copy run files sang Drive Desktop sync...")
        try:
            drive_run_info = upload_run_files_to_drive_local(
                files=files_to_upload,
                niche_slug=niche,
                user=user,
                snapshot_root=Path(drive_local_dir),
            )
            if drive_run_info:
                num_up = len(drive_run_info.get("uploaded_files", []))
                status.write(f"✓ Local Drive sync: {num_up} files → `{drive_run_info.get('folder_local_path')}`")
        except Exception as e:
            status.write(f"⚠️ Local Drive copy lỗi: {e}")

    status.update(label="🎉 Pipeline complete!", state="complete")
    return {
        "output_dir": output_dir,
        "raw_path": raw_path,
        "classified_path": classified_path,
        "report_path": report_path,
        "brief_path": brief_path if with_brief else None,
        "strategy_path": strategy_path if strategy_generated else None,
        "drive_run_info": drive_run_info,
        "num_comments": len(comments),
        "num_classified": len(classified),
        "num_angles": angles_count,
    }


# --- UI ---
def render_sidebar() -> tuple[str, int, bool, int, bool]:
    """Render sidebar: user info, settings, recent runs.

    v0.5: returns thêm with_strategy flag (Stage 5).
    """
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
        with_strategy = st.checkbox(
            "🧠 Generate Phân tích toàn diện (+~$0.07)",
            value=True,
            disabled=not with_brief,
            help=(
                "Stage 5 — Claude Opus tổng hợp Customer Profile Canvas "
                "(Pains/Gains/Jobs) + chấm điểm brief + 3 phát hiện chiến lược + "
                "product offer + content roadmap 30 ngày. Cost ~$0.07, +30-60s."
            ),
        )

        # v0.7: Backup section — safety net trước khi push code mới
        st.divider()
        st.header("🔒 Backup")
        st.caption("Tải về file log + folder list trước khi anh push code mới")
        if LOG_PATH.exists():
            log_bytes = LOG_PATH.read_bytes()
            st.download_button(
                "📥 Backup usage_log.csv",
                data=log_bytes,
                file_name=f"usage_log_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Tải về snapshot log Railway Volume hiện tại. Cất an toàn ở local.",
                key="backup_log_btn",
            )
            # Show size + row count
            try:
                with open(LOG_PATH, "r", encoding="utf-8-sig") as _f:
                    _row_count = sum(1 for _ in _f) - 1  # trừ header
                st.caption(f"📊 {_row_count} rows · {len(log_bytes) / 1024:.1f} KB")
            except Exception:
                pass
        else:
            st.caption("_Chưa có log file._")

        st.divider()
        st.header("📚 10 runs gần nhất")
        st.caption("👆 Click vào run để xem lại + tải file")
        if LOG_PATH.exists():
            # v0.6 fix: auto-migrate header trước khi đọc (rows cũ thiếu output_dir)
            _migrate_log_header_if_needed()
            with open(LOG_PATH, "r", encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))[-10:][::-1]
            for idx, r in enumerate(rows):
                ts = r.get("timestamp", "")[:16].replace("T", " ")
                icon = "✅" if r.get("status") == "success" else "❌"
                label = (
                    f"{icon} {ts} · {r.get('user', '?')} · {r.get('niche', '?')[:20]}\n"
                    f"{r.get('num_comments', '0')}cmt · ${r.get('cost_est_usd', '0')}"
                )
                # v0.6: nếu output_dir empty (run cũ trước commit bd0e2bf), infer path
                out_dir = (r.get("output_dir") or "").strip()
                if not out_dir and r.get("status") == "success":
                    out_dir = _infer_output_dir_from_log(r)
                if r.get("status") == "success" and out_dir:
                    if st.button(label, key=f"hist_{idx}_{ts}", use_container_width=True):
                        st.session_state["selected_history_run"] = {
                            "output_dir": out_dir,
                            "timestamp": ts,
                            "user": r.get("user", ""),
                            "niche": r.get("niche", ""),
                            "num_comments": r.get("num_comments", "0"),
                            "cost": r.get("cost_est_usd", "0"),
                        }
                        st.rerun()
                else:
                    st.caption(label.replace("\n", " — "))
        else:
            st.caption("_Chưa có run nào._")

    return user, max_comments, with_brief, num_angles, with_strategy


def render_history_run(history: dict) -> None:
    """Restore download buttons + preview cho 1 run trong history.

    v0.6: Click 1 run trong sidebar history → load lại files từ output_dir
    để tải về (nếu file vẫn còn trên Railway Volume).
    """
    out_dir = Path(history["output_dir"])

    st.markdown("---")
    st.subheader(f"📚 Xem lại run: {history['timestamp']}")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("User", history["user"])
    col_b.metric("Niche", history["niche"])
    col_c.metric("Comments", history["num_comments"])
    col_d.metric("Cost", f"${history['cost']}")

    if not out_dir.exists():
        st.error(
            f"⚠️ Folder không còn tồn tại: `{out_dir}`. "
            "File có thể đã bị xoá hoặc Railway Volume đã reset. "
            "Check Google Drive backup (folder runs/...) thay thế."
        )
        if st.button("🔙 Đóng (về run hiện tại)"):
            del st.session_state["selected_history_run"]
            st.rerun()
        return

    # Tìm các file output có thể tải
    candidates = {
        "📊 report.md": out_dir / "report.md",
        "🎬 brief.md": out_dir / "brief.md",
        "🧠 phan-tich-toan-dien.md": out_dir / "phan-tich-toan-dien.md",
        "💾 classified.json": out_dir / "classified.json",
        "📦 raw_comments.json": out_dir / "raw_comments.json",
    }
    existing = [(label, p) for label, p in candidates.items() if p.exists()]

    if not existing:
        st.warning(f"Folder tồn tại nhưng KHÔNG có file output: `{out_dir}`")
    else:
        st.markdown(f"**📁 Files ({len(existing)} files):**")
        # Render download buttons
        cols = st.columns(min(len(existing), 5))
        for col, (label, path) in zip(cols, existing):
            with col:
                mime = "text/markdown" if path.suffix == ".md" else "application/json"
                st.download_button(
                    f"⬇️ {label}",
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime=mime,
                    use_container_width=True,
                    key=f"hist_dl_{path.name}",
                )

        # Inline preview với tabs
        md_files = [(label, path) for label, path in existing if path.suffix == ".md"]
        if md_files:
            tab_labels = [label for label, _ in md_files]
            tabs = st.tabs(tab_labels)
            for tab, (_, path) in zip(tabs, md_files):
                with tab:
                    st.markdown(path.read_text(encoding="utf-8"))

    if st.button("🔙 Đóng (về run hiện tại)", key="close_history"):
        del st.session_state["selected_history_run"]
        st.rerun()


# --- Bước 2-4 helpers: Sắp xếp + Lựa chọn + Upload Drive ---

# Match cả [ ], [x], [X] và biến thể có space — accept mọi state
CANDIDATE_RE = re.compile(
    r"^\s*-\s*\[\s*[xX ]\s*\]\s*"
    r"`\[SCORE\s+(?P<score>\d+)\]`\s*"
    r"`\[(?P<id>\S+)\s+(?P<problem>[A-Z_]+)\]`\s*"
    r"`\[(?P<opportunity>[A-Z_]+)\]`\s*"
    r"\"(?P<quote>.+?)\"\s*"
    r"—\s*@(?P<author>\S+)\s*"
    r"\((?P<likes>\d+)\s*likes?\)",
    re.MULTILINE,
)


def parse_candidates(md_path: Path) -> list[dict]:
    """Parse 3-lựa-chọn.md → list candidates với metadata cho UI checkbox."""
    if not md_path.exists():
        return []
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    candidates: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = CANDIDATE_RE.match(line)
        if m:
            cand = {
                "id": m.group("id"),
                "score": int(m.group("score")),
                "problem_code": m.group("problem"),
                "opportunity": m.group("opportunity"),
                "quote": m.group("quote"),
                "author": m.group("author"),
                "likes": int(m.group("likes")),
                "summary": "",
                "ticked_already": "[x]" in line or "[X]" in line,
            }
            # Get summary from next continuation lines
            j = i + 1
            while j < len(lines) and (lines[j].startswith(" ") or lines[j].startswith("\t")):
                if "💡" in lines[j]:
                    cand["summary"] = lines[j].split("💡", 1)[1].strip()
                    break
                j += 1
            candidates.append(cand)
            i = j if j > i else i + 1
        else:
            i += 1
    return candidates


def mark_ticked(md_path: Path, selected_ids: set[str]) -> int:
    """Edit 3-lựa-chọn.md — replace `[ ]` thành `[x]` cho candidate có id trong selected_ids.

    Returns: số dòng đã tick.
    """
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    ticked_count = 0
    for i, line in enumerate(lines):
        for id_ in selected_ids:
            if f"[{id_} " in line and ("- [ ]" in line or "- [  ]" in line):
                lines[i] = re.sub(r"- \[\s*\]", "- [x]", line, count=1)
                ticked_count += 1
                break
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ticked_count


def render_handoff_section(
    result: dict,
    niche: str,
    user: str,
) -> None:
    """Render UI Bước 2-4: bank + tick + select + export-to-Drive.

    Chỉ work khi niche có sẵn niche_configs/<slug>.json.
    """
    st.markdown("---")
    st.subheader("4️⃣ Chọn insight + Upload sang Google Drive")
    st.caption(
        "Sau khi pipeline xong, anh chọn các insight đáng dùng → upload sang Google Drive "
        "để CoWork pull về viết bài. Bước này không bắt buộc — anh có thể bỏ qua nếu chỉ test."
    )

    # Check niche config exists
    config_path = PROJECT_ROOT / "niche_configs" / f"{niche}.json"
    if not config_path.exists():
        st.info(
            f"💡 Niche `{niche}` chưa có config taxonomy. Để dùng tính năng này, "
            f"cần file `niche_configs/{niche}.json`. Hiện chỉ niche `kinh-doanh-27-45` có sẵn — "
            f"liên hệ anh Tuấn để setup niche mới (~30 phút)."
        )
        return

    # Check Drive env vars
    drive_folder_id = os.environ.get("INSIGHTS_PACK_DRIVE_FOLDER_ID", "").strip()
    gdrive_json = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON", "").strip()
    if not (drive_folder_id and gdrive_json):
        st.warning(
            "⚠️ Drive upload chưa cấu hình. Cần env var `INSIGHTS_PACK_DRIVE_FOLDER_ID` + "
            "`GDRIVE_SERVICE_ACCOUNT_JSON` trên Railway. Liên hệ anh Tuấn."
        )
        return

    output_dir = result["classified_path"].parent

    # State key prefix — unique per run để session_state không lẫn giữa các pipeline run
    state_key = f"handoff_{result['classified_path'].stat().st_mtime_ns}"

    # Bước 2: Auto run bank (chỉ chạy 1 lần)
    bank_key = f"{state_key}_bank"
    if bank_key not in st.session_state:
        with st.spinner("📊 Đang sắp xếp insight theo nhóm vấn đề..."):
            try:
                bank_stats = build_insight_bank(
                    result["classified_path"],
                    config_path,
                    output_dir=output_dir,
                )
                st.session_state[bank_key] = bank_stats
            except Exception as e:
                st.error(f"❌ Lỗi sắp xếp: {e}")
                return
    else:
        bank_stats = st.session_state[bank_key]

    # Hiển thị tổng quan
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng insight", bank_stats["total"])
    col2.metric("Actionable", bank_stats["kept"])
    col3.metric("Loại bỏ", bank_stats["skipped_bucket"] + bank_stats["skipped_short"])

    # Bước 3: Parse candidates + render checkbox
    lua_chon_path = bank_stats["lua_chon_path"]
    candidates = parse_candidates(lua_chon_path)

    if not candidates:
        st.warning(
            "Không có candidate nào đạt threshold (score ≥ 20). "
            "Pipeline này chưa đủ insight chất lượng cao — anh có thể scrape thêm video / paste thêm comment."
        )
        return

    st.markdown(f"**Top {len(candidates)} insight** — anh tick chọn các angle muốn handoff sang CoWork:")

    # Render checkboxes (group theo problem_code để dễ scan)
    by_problem: dict[str, list[dict]] = {}
    for c in candidates:
        by_problem.setdefault(c["problem_code"], []).append(c)

    selected_ids: set[str] = set()
    for problem_code, cands in by_problem.items():
        with st.expander(f"📂 {problem_code} ({len(cands)} insight)", expanded=True):
            for c in cands:
                label = (
                    f"`{c['id']}` **[{c['score']}]** — "
                    f"_{c['summary'] or c['quote'][:80]}_ "
                    f"({c['author']} · {c['likes']} likes)"
                )
                # Default check nếu đã tick từ trước
                key = f"{state_key}_cb_{c['id']}"
                checked = st.checkbox(
                    label,
                    value=c["ticked_already"],
                    key=key,
                )
                if checked:
                    selected_ids.add(c["id"])

    if not selected_ids:
        st.caption("👆 Anh chưa chọn insight nào. Tick checkbox để chọn.")
        return

    st.info(f"✓ Đã chọn **{len(selected_ids)}** insight")

    # Bước 4: Build pack + Upload Drive button
    pack_bytes_key = f"{state_key}_pack_bytes"
    pack_fname_key = f"{state_key}_pack_fname"
    pack_drive_key = f"{state_key}_pack_drive"
    pack_logs_key = f"{state_key}_pack_logs"

    if st.button(
        f"📦 Tạo insight pack + Upload Drive ({len(selected_ids)} insight)",
        type="primary",
        key=f"{state_key}_upload",
    ):
        with st.spinner("Đang tạo insight pack + thử upload Drive..."):
            try:
                # 1. Mark ticked in 3-lựa-chọn.md
                ticked = mark_ticked(lua_chon_path, selected_ids)
                st.caption(f"✓ Tick {ticked} insight trong 3-lựa-chọn.md")

                # 2. Run selection → tạo selected_angles.json
                sel_result = run_selection(lua_chon_path, niche_slug=niche)
                st.caption(f"✓ Selection: {sel_result['added']} mới, {sel_result['total']} tổng")

                # 3. Export pack — LUÔN build file local. Drive upload là best-effort.
                import logging as _logging
                _log_records: list[str] = []

                class _UIHandler(_logging.Handler):
                    def emit(self, record):
                        if record.levelno >= _logging.WARNING:
                            _log_records.append(self.format(record))

                _ui_handler = _UIHandler()
                _ui_handler.setFormatter(_logging.Formatter("%(levelname)s: %(message)s"))
                _logger_root = _logging.getLogger("tiktok_insight_miner.cowork_exporter")
                _logger_root.addHandler(_ui_handler)

                try:
                    export_result = export_for_cowork(
                        selected_path=sel_result["json_path"],
                        config_path=config_path,
                        drive_folder_id=drive_folder_id,
                        gdrive_service_account_json=gdrive_json,
                    )
                finally:
                    _logger_root.removeHandler(_ui_handler)

                # File pack LUÔN có (export_for_cowork build trước khi upload Drive)
                pack_path = export_result["output_path"]
                if pack_path and pack_path.exists():
                    pack_bytes = pack_path.read_bytes()
                    pack_fname = f"insights-pack_{niche}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                    st.session_state[pack_bytes_key] = pack_bytes
                    st.session_state[pack_fname_key] = pack_fname
                    st.session_state[pack_logs_key] = _log_records
                    drive_info = export_result.get("snapshot_drive_info")
                    if drive_info:
                        st.session_state[pack_drive_key] = drive_info
                    else:
                        st.session_state[pack_drive_key] = None
                else:
                    st.error("❌ Build pack fail — file output không tồn tại.")

            except Exception as e:
                st.error(f"❌ Lỗi tạo pack: {e}")
                st.exception(e)

    # ALWAYS render kết quả từ session_state (persist qua re-run khi click download)
    if pack_bytes_key in st.session_state:
        drive_info = st.session_state.get(pack_drive_key)
        _log_records = st.session_state.get(pack_logs_key, [])

        if drive_info:
            st.success(
                f"🎉 Upload Drive thành công — `insights-pack_v{drive_info['version']}.md`"
            )
            st.markdown(f"🔗 [Xem trên Google Drive]({drive_info['web_link']})")
        else:
            st.warning(
                "⚠️ **Upload Drive fail — nhưng file insight pack đã tạo xong.** "
                "Anh tải về máy ở nút bên dưới rồi upload thủ công vào Drive folder Shared Drive "
                "(drag drop trên drive.google.com)."
            )
            if _log_records:
                with st.expander("🔧 Chi tiết lỗi Drive"):
                    for rec in _log_records:
                        st.code(rec)

        # LUÔN show download button — anh upload thủ công nếu Drive auto fail
        st.markdown("**📥 Tải insight pack về máy** (để upload thủ công nếu cần):")
        st.download_button(
            label=f"⬇️ Download {st.session_state[pack_fname_key]}",
            data=st.session_state[pack_bytes_key],
            file_name=st.session_state[pack_fname_key],
            mime="text/markdown",
            type="primary" if not drive_info else "secondary",
            key=f"{state_key}_dl_pack",
            use_container_width=True,
        )
        st.caption(
            "💡 **Upload thủ công**: mở https://drive.google.com → vào Shared Drive folder "
            "`insights-packs/kinh-doanh-27-45/` → New → File upload → chọn file vừa tải."
        )


def render_results(result: dict, with_brief: bool, duration: float) -> None:
    """Hiển thị download buttons + inline render.

    v0.5: thêm tab Phân tích toàn diện nếu strategy_path có.
    """
    has_strategy = result.get("strategy_path") is not None
    drive_info = result.get("drive_run_info")

    st.success(
        f"🎉 Done in **{duration:.0f}s** — "
        f"{result['num_comments']} comments classified"
        + (f", {result['num_angles']} angles" if with_brief else "")
        + (" + 🧠 Phân tích toàn diện" if has_strategy else "")
    )

    # v0.5: Drive auto-upload status
    if drive_info:
        num_uploaded = len(drive_info.get("uploaded_files", []))
        folder_path = drive_info.get("folder_path", "")
        folder_link = drive_info.get("folder_web_link") or drive_info.get("folder_local_path", "")
        st.info(
            f"☁️ **Auto-uploaded {num_uploaded} files lên Google Drive** — "
            f"folder: `{folder_path}`"
        )
        if folder_link and folder_link.startswith("http"):
            st.markdown(f"🔗 [Mở folder trên Google Drive]({folder_link})")
        # List uploaded files
        with st.expander(f"📋 Chi tiết {num_uploaded} files đã upload", expanded=False):
            for f in drive_info.get("uploaded_files", []):
                label = f.get("label", "?")
                name = f.get("file_name", "?")
                link = f.get("web_link", "")
                if link:
                    st.markdown(f"- **{label}**: [{name}]({link})")
                else:
                    st.markdown(f"- **{label}**: `{name}`")
            skipped = drive_info.get("skipped", [])
            if skipped:
                st.caption(f"⚠️ Skipped (không upload được): {', '.join(skipped)}")

    st.subheader("📁 Download files")

    # Build files list dynamic
    files_to_show = [
        ("📊 report.md", result["report_path"], "text/markdown"),
        ("💾 classified.json", result["classified_path"], "application/json"),
        ("📦 raw_comments.json", result["raw_path"], "application/json"),
    ]
    if with_brief and result["brief_path"]:
        files_to_show.insert(1, ("🎬 brief.md", result["brief_path"], "text/markdown"))
    if has_strategy:
        files_to_show.insert(2 if with_brief else 1,
            ("🧠 phan-tich-toan-dien.md", result["strategy_path"], "text/markdown"))

    cols = st.columns(len(files_to_show))
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
    if has_strategy:
        tab_labels.append("🧠 Phân tích toàn diện")
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        st.markdown(result["report_path"].read_text(encoding="utf-8"))
    tab_idx = 1
    if with_brief:
        with tabs[tab_idx]:
            st.markdown(result["brief_path"].read_text(encoding="utf-8"))
        tab_idx += 1
    if has_strategy:
        with tabs[tab_idx]:
            st.markdown(result["strategy_path"].read_text(encoding="utf-8"))

    # v0.7 — Stage C: CoWork Brief Pack section
    if with_brief and result.get("brief_path"):
        render_cowork_pack_section(result)


def render_cowork_pack_section(result: dict) -> None:
    """v0.7 — Stage C Refinement: cherry-pick 3-5 angle từ brief → CoWork Pack.

    User tick chọn angles + chọn platform → generate file `cowork-brief-pack_*.md`
    để Hiền paste vào CoWork. KHÔNG đụng file cũ (chỉ read brief.md + create new).
    """
    st.markdown("---")
    st.subheader("📦 Build CoWork Pack (Stage C — Tinh lọc)")
    st.caption(
        "Cherry-pick 3-5 angle TỐT NHẤT từ brief 10 angles → 1 file 'data tinh' để Hiền "
        "paste vào CoWork viết bài. KHÔNG đụng file cũ."
    )

    brief_path = result["brief_path"]
    try:
        angles = parse_brief_angles(brief_path)
    except Exception as e:
        st.error(f"❌ Parse brief.md fail: {e}")
        return

    if not angles:
        st.warning("⚠️ Không parse được angle nào từ brief.md. Brief format có đúng chuẩn không?")
        return

    output_dir = result["output_dir"]
    niche_slug = output_dir.parent.parent.name if output_dir.parent.parent.name != "output" else "unknown"

    # Try load niche persona để show niche_name đẹp
    try:
        from tiktok_insight_miner.suggester import load_niche_persona
        cfg = load_niche_persona(niche_slug)
        niche_name = cfg.get("niche_name", niche_slug) if cfg else niche_slug
    except Exception:
        niche_name = niche_slug

    # UI: cherry-pick + settings
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(f"**📋 Chọn 3-5 angle muốn dùng** (từ {len(angles)} angles trong brief):")
        selected_indices: list[int] = []
        for a in angles:
            label = (
                f"**#{a['idx']}** — {a['title'][:60]} "
                f"`[{a['demand_likes']} likes · {a['confidence']:.2f}]`"
            )
            if st.checkbox(label, key=f"angle_pick_{a['idx']}", help=a.get("hook", "")[:200]):
                selected_indices.append(a["idx"])

    with col_right:
        st.markdown("**⚙️ Settings**")
        platform = st.selectbox(
            "Target platform",
            ["Fanpage", "TikTok", "Fanpage + TikTok"],
            index=0,
            key="cowork_platform",
        )
        voice_slug = st.selectbox(
            "Voice profile",
            ["chi-hien", "(none)"],
            index=0,
            key="cowork_voice",
            help="Persona viết — chi-hien = chị Hiền (default)",
        )

    n_selected = len(selected_indices)
    if n_selected == 0:
        st.info("👆 Tick chọn 3-5 angle ở trên để generate Pack")
        return
    if n_selected < 3:
        st.warning(f"⚠️ Mới chọn {n_selected} — recommend ≥3 angle cho 1 pack")
    elif n_selected > 5:
        st.warning(f"⚠️ Chọn {n_selected} — recommend ≤5 (quá nhiều = Hiền khó focus)")

    if st.button(
        f"📦 Generate CoWork Pack ({n_selected} angles)",
        type="primary",
        key="cowork_gen_btn",
        use_container_width=True,
    ):
        with st.spinner("Đang generate CoWork Pack..."):
            try:
                selected_angles = [a for a in angles if a["idx"] in selected_indices]
                run_id = output_dir.name  # vd "2026-05-17" hoặc "2026-05-17__tuan"

                # Get drive folder URL nếu có
                drive_url = ""
                drive_info = result.get("drive_run_info")
                if drive_info:
                    drive_url = drive_info.get("folder_web_link", "")

                pack_content = generate_cowork_pack(
                    selected_angles=selected_angles,
                    niche_name=niche_name,
                    niche_slug=niche_slug,
                    run_id=run_id,
                    drive_folder_url=drive_url,
                    platform=platform,
                    voice_profile_slug=voice_slug if voice_slug != "(none)" else "",
                    total_comments=result.get("num_comments", 0),
                )

                pack_filename = f"cowork-brief-pack_{datetime.now().strftime('%H%M')}.md"
                pack_path = output_dir / pack_filename
                save_cowork_pack(pack_content, pack_path)

                # Save vào session_state để persist qua re-run
                st.session_state["cowork_pack_content"] = pack_content
                st.session_state["cowork_pack_path"] = str(pack_path)
                st.session_state["cowork_pack_filename"] = pack_filename

                # Best-effort upload Drive
                drive_folder_id = os.environ.get("INSIGHTS_PACK_DRIVE_FOLDER_ID", "").strip()
                gdrive_json = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON", "").strip()
                if drive_folder_id and gdrive_json:
                    try:
                        drive_pack_info = upload_run_files_to_drive_api(
                            files={"cowork_pack": pack_path},
                            niche_slug=niche_slug,
                            user=result.get("user", "anon"),
                            root_folder_id=drive_folder_id,
                            service_account_json=gdrive_json,
                        )
                        if drive_pack_info:
                            st.session_state["cowork_pack_drive"] = drive_pack_info
                    except Exception as e:
                        st.warning(f"⚠️ Upload Drive fail (pack vẫn save local): {e}")

                st.success(f"✅ CoWork Pack generated — {len(pack_content)} chars")
            except Exception as e:
                st.error(f"❌ Generate fail: {e}")
                st.exception(e)

    # ALWAYS render kết quả từ session_state (persist qua re-run)
    if "cowork_pack_content" in st.session_state:
        st.markdown("---")
        st.markdown("### 🎁 CoWork Pack ready")

        col_dl, col_drive = st.columns(2)
        with col_dl:
            st.download_button(
                f"⬇️ Tải {st.session_state.get('cowork_pack_filename', 'cowork-pack.md')}",
                data=st.session_state["cowork_pack_content"],
                file_name=st.session_state.get("cowork_pack_filename", "cowork-pack.md"),
                mime="text/markdown",
                type="primary",
                use_container_width=True,
                key="cowork_dl_btn",
            )
        with col_drive:
            drive_pack = st.session_state.get("cowork_pack_drive")
            if drive_pack and drive_pack.get("uploaded_files"):
                first = drive_pack["uploaded_files"][0]
                link = first.get("web_link", "")
                if link:
                    st.link_button(
                        "🔗 Mở trên Google Drive",
                        url=link,
                        use_container_width=True,
                    )

        with st.expander("👁 Preview CoWork Pack content", expanded=False):
            st.markdown(st.session_state["cowork_pack_content"])


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

        user, max_comments, with_brief, num_angles, with_strategy = render_sidebar()

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
                est_cost = estimate_cost(est_total, with_brief, mode="scrape", with_strategy=with_strategy)
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
                est_cost = estimate_cost(len(valid_lines), with_brief, mode="paste", with_strategy=with_strategy)
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

        # Submit click → chạy pipeline mới, save vào session_state
        if submit:
            # Validate niche slug
            if not NICHE_SLUG_RE.match(niche):
                st.error(
                    f"❌ Niche slug không hợp lệ: '{niche}'. "
                    "Dùng kebab-case (a-z, 0-9, dấu -). Ví dụ: `skincare-acne`."
                )
                return

            # Clear pipeline result cũ trước khi chạy mới
            if "pipeline_result" in st.session_state:
                del st.session_state["pipeline_result"]

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
                            with_strategy=with_strategy,
                        )
                    else:
                        result = run_pipeline(
                            urls=urls_list, niche=niche, user=user,
                            max_comments=max_comments, with_brief=with_brief,
                            num_angles=num_angles, status=status,
                            with_strategy=with_strategy,
                        )
                    duration = time.time() - start_time
                    cost = estimate_cost(result["num_comments"], with_brief, mode=source_mode, with_strategy=with_strategy)
                    log_run(
                        user=user, niche=niche,
                        num_urls=len(urls_list) if source_mode == "scrape" else 0,
                        num_comments=result["num_comments"],
                        with_brief=with_brief, duration_s=duration,
                        status="success", cost_est=cost,
                        output_dir=str(result["output_dir"]),
                    )
                    # Post-run hooks (best-effort)
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

                    # 💾 SAVE vào session_state để persist qua re-run (click checkbox, etc.)
                    st.session_state["pipeline_result"] = {
                        "result": result,
                        "with_brief": with_brief,
                        "duration": duration,
                        "niche": niche,
                        "user": user,
                    }
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

        # ALWAYS render Section 3 + 4 từ session_state nếu có (persist qua re-run)
        if "pipeline_result" in st.session_state:
            saved = st.session_state["pipeline_result"]
            st.subheader("3️⃣ Kết quả")
            render_results(saved["result"], saved["with_brief"], saved["duration"])
            render_handoff_section(saved["result"], saved["niche"], saved["user"])

        # v0.6: Render history run nếu user click trong sidebar
        if "selected_history_run" in st.session_state:
            render_history_run(st.session_state["selected_history_run"])

    finally:
        # Always render landing sections — chạy DÙ return ở đâu trong try block
        _render_landing_sections()


if __name__ == "__main__":
    main()
