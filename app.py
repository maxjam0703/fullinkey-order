import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import time

# --- [1. 사용자 및 거래처 설정] ---
USER_DB = {
    "admin": ["fullin123", "이사장", "관리자"],
    "staff1": ["1111", "김기사", "직원"],
    "staff2": ["2222", "박대리", "직원"]
}

CLIENT_INFO = {
    "A 인쇄소": {"주소": "경기도 파주시 문발로 123", "담당자": "강본부장", "연락처": "010-1234-5678"},
    "B 문화사": {"주소": "서울시 중구 을지로 45", "담당자": "이실장", "연락처": "010-9876-5432"},
    "기타": {"주소": "직접입력 필요", "담당자": "확인요망", "연락처": "000-0000-0000"}
}

DB_FILE = "fullinkey_orders_final.csv"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['주문일시', '업체명', '주소', '담당자', '연락처', '규격', '수량', '주문자', '상태', '승인자', '배송담당'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- [2. 디자인 및 여백 설정 (고급형)] ---
def apply_custom_design():
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        
        /* 사이드바 로고 박스 여백 개선 */
        [data-testid="stSidebar"] .stMarkdown h1 {
            background-color: #003366;
            color: white !important;
            padding: 20px 25px !important; /* 안쪽 여백을 넉넉히 주어 글자가 붙지 않게 함 */
            border-radius: 12px;
            font-size: 22px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        /* 상단 탭 디자인 및 여백 개선 */
        .stTabs [data-baseweb="tab-list"] { gap: 12px; padding: 10px 0; }
        .stTabs [data-baseweb="tab"] {
            height: 55px;
            background-color: #ffffff;
            border-radius: 10px;
            padding: 0 30px !important; /* 좌우 여백을 넓혀 답답함 해소 */
            border: 1px solid #dee2e6;
        }
        .stTabs [aria-selected="true"] {
            background-color: #003366 !important;
            color: white !important;
            font-weight: bold;
            border: none;
        }
        
        /* 카드형 컨테이너 */
        div[data-testid="stExpander"], div.stChatMessage {
            background-color: white;
            border-radius: 15px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

# --- [3. 로그인 로직] ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_screen():
    apply_custom_design()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; padding: 50px 0;'><h1>Fullinkey</h1></div>", unsafe_allow_html=True)
        with st.container(border=True):
            user_id = st.text_
