import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import time

# --- [설정 1. 사용자 DB] ---
USER_DB = {
    "admin": ["fullin123", "이사장", "관리자"],
    "staff1": ["1111", "김철수 기사", "직원"],
    "staff2": ["2222", "박영희 대리", "직원"]
}

# --- [설정 2. 거래처 정보] ---
CLIENT_INFO = {
    "A 인쇄소": {"주소": "경기도 파주시 문발로 123", "담당자": "강본부장", "연락처": "010-1234-5678"},
    "B 문화사": {"주소": "서울시 중구 을지로 45", "담당자": "이실장", "연락처": "010-9876-5432"},
    "C 패키지": {"주소": "인천시 서구 가좌동 78", "담당자": "최과장", "연락처": "010-5555-4444"},
    "기타": {"주소": "직접입력 필요", "담당자": "확인요망", "연락처": "000-0000-0000"}
}

DB_FILE = "fullinkey_orders_v4.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['주문일시', '업체명', '주소', '담당자', '연락처', '규격', '수량', '주문자', '상태', '승인자', '배송담당'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- [디자인: 커스텀 CSS] ---
def apply_custom_design():
    st.markdown("""
        <style>
        /* 메인 배경 및 폰트 */
        .stApp { background-color: #f8f9fa; }
        h1, h2, h3 { color: #003366; font-family: 'Pretendard', sans-serif; }
        
        /* 버튼 디자인 */
        .stButton>button {
            border-radius: 8px;
            border: none;
            height: 3em;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* 카드 스타일 박스 */
        div[data-testid="stExpander"], div.stChatMessage {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        /* 탭 디자인 */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            color: #666;
        }
        .stTabs [aria-selected="true"] { background-color: #003366 !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

# 세션 관리
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- [화면 구성] ---
def login_screen():
    apply_custom_design()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; padding: 50px 0;'>", unsafe_allow_html=True)
        st.title("Fullinkey")
        st.markdown("<p style='color: #666;'>Smart Printing Logistics Solution</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            user_id = st.text_input("ID")
            user_pw = st.text_input("Password", type="password")
            remember = st.checkbox("로그인 상태 유지")
            
            if st.button("LOGIN", use_container_width=True, type="primary"):
                if user_id in USER_DB and USER_DB[user_id][0] == user_pw:
                    st.session_state.logged_in = True
                    st.session_state.user_name = USER_DB[user_id][1]
                    st.session_state.user_role = USER_DB[user_id][2]
                    st.rerun()
                else:
                    st.error("계정 정보를 확인해주세요.")

def main_system():
    apply_custom_design()
    
    with st.sidebar:
        st.markdown(f"### {st.session_state.user_name}")
        st.caption(f"Role: {st.session_state.user_role
