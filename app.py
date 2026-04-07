import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import time

# --- [1. 사용자 정보] ---
USER_DB = {
    "admin": ["fullin123", "이사장", "관리자"],
    "staff1": ["1111", "김기사", "직원"],
    "staff2": ["2222", "박대리", "직원"]
}

# --- [2. 거래처 정보] ---
CLIENT_INFO = {
    "A 인쇄소": {"주소": "경기도 파주시 문발로 123", "담당자": "강본부장", "연락처": "010-1234-5678"},
    "B 문화사": {"주소": "서울시 중구 을지로 45", "담당자": "이실장", "연락처": "010-9876-5432"},
    "C 패키지": {"주소": "인천시 서구 가좌동 78", "담당자": "최과장", "연락처": "010-5555-4444"},
    "기타": {"주소": "직접입력 필요", "담당자": "확인요망", "연락처": "000-0000-0000"}
}

DB_FILE = "fullinkey_orders_v5.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['주문일시', '업체명', '주소', '담당자', '연락처', '규격', '수량', '주문자', '상태', '승인자', '배송담당'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- [3. 디자인 설정] ---
def apply_style():
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        h1, h2, h3 { color: #003366 !important; }
        .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; }
        div[data-testid="stExpander"], div.stChatMessage { 
            background-color: white; border-radius: 12px; border: 1px solid #ddd; 
        }
        .stTabs [aria-selected="true"] { 
            background-color: #003366 !important; color: white !important; border-radius: 8px; 
        }
        </style>
    """, unsafe_allow_html=True)

# 세션 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- [4. 로그인 화면] ---
def login_screen():
    apply_style()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; padding: 40px 0;'>", unsafe_allow_html=True)
        st.title("Fullinkey 로그인")
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            user_id = st.text_input("아이디")
            user_pw = st.text_input("비밀번호", type="password")
            if st.button("LOGIN", use_container_width=True, type="primary"):
                if user_id in USER_DB and USER_DB[user_id][0] == user_pw:
                    st.session_state.logged_in = True
                    st.session_state.user_name = USER_DB[user_id][1]
                    st.session_state.user_role = USER_DB[user_id][2]
                    st.rerun()
                else:
                    st.error("계정 정보를 확인해주세요.")

# --- [5. 메인 시스템] ---
def main_system():
    apply_style()
    with st.sidebar:
        st.title("Fullinkey")
        st.write(f"👤 **{st.session_state.user_name}**님")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if 'orders' not in st.session_state:
        st.session_state.orders = load_data()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 주문등록", "👑 승인관리", "🚚 배송업무", "📊 현황"])

    with tab1:
        st.subheader("신규 주문")
        client = st.selectbox("거래처", list(CLIENT_INFO.keys()))
        info = CLIENT_INFO[client]
        st.info(f"🏠 {info['주소']}\n📞 {info['담당자']} ({info['연락처']})")
        col_a, col_b = st.columns(2)
        spec = col_a.selectbox("규격", ["0.15mm", "0.30mm", "무현상"])
        count = col_b.number_input("수량(박스)", min_value
