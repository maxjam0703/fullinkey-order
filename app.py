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

DB_FILE = "fullinkey_orders_v5.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['주문일시', '업체명', '주소', '담당자', '연락처', '규격', '수량', '주문자', '상태', '승인자', '배송담당'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- [디자인 설정] ---
def apply_custom_design():
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        h1, h2, h3 { color: #003366; }
        .stButton>button { border-radius: 8px; height: 3em; transition: all 0.3s; }
        div[data-testid="stExpander"], div.stChatMessage { background-color: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .stTabs [aria-selected="true"] { background-color: #003366 !important; color: white !important; border-radius: 8px; }
        </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- [로그인 화면] ---
def login_screen():
    apply_custom_design()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; padding: 50px 0;'>", unsafe_allow_html=True)
        st.title("Fullinkey")
        st.markdown("<p style='color: #666;'>Smart Printing Logistics Solution</p></div>", unsafe_allow_html=True)
        
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
                    st.error("정보가 올바르지 않습니다.")

# --- [메인 시스템] ---
def main_system():
    apply_custom_design()
    with st.sidebar:
        st.title("Fullinkey")
        st.write(f"👤 **{st.session_state.user_name}** ({st.session_state.user_role})")
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    if 'orders' not in st.session_state:
        st.session_state.orders = load_data()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 주문등록", "👑 승인관리", "🚚 배송업무", "📊 현황"])

    with tab1:
        st.subheader("New Order")
        client = st.selectbox("거래처 선택", list(CLIENT_INFO.keys()))
        info = CLIENT_INFO[client]
        st.info(f"🏠 {info['주소']}\n📞 담당: {info['담당자']} ({info['연락처']})")
        col_a, col_b = st.columns(2)
        spec = col_a.selectbox("규격", ["0.15mm", "0.30mm", "무현상"])
        count = col_b.number_input("수량(박스)", min_value=1, value=10)
        if st.button("🚀 주문 전송", use_container_width=True, type="primary"):
            new_data = {
                '주문일시': datetime.now().strftime("%m/%d %H:%M"),
                '업체명': client, '주소': info['주소'], '담당자': info['담당자'], '연락처': info['연락처'],
                '규격': spec, '수량': count, '주문자': st.session_state.user_name,
                '상태': '승인대기', '승인자': '-', '배송담당': '-'
            }
            st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_data])], ignore_index=True)
            save_data(st.session_state.orders)
            st.success("주문 접수 완료!")

    with tab2:
        if st.session_state.user_role == "관리자":
            pending = st.session_state.orders[st.session_state.orders['상태'] == '승인대기']
            for idx, row in pending.iterrows():
                with st.container(border=True):
                    st.write(f"**{row['업체명']}** | {row['규격']} {row['수량']}박스")
                    if st.button("승인하기", key=f"ap_{idx}", use_container_width=True):
                        st.session_state.orders.at[idx, '상태'] = '배송대기'
                        st.session_state.orders.at[idx, '승인자'] = st.session_state.user_name
                        save_data(st.session_state.orders)
                        st.rerun()
        else: st.warning("관리자 전용 메뉴입니다.")

    with tab3:
        st.subheader("배송 가능 목록")
        waiting = st.session_state.orders[st.session_state.orders['상태'] == '배송대기']
        for idx, row in waiting.iterrows():
            with st.container(border=True):
                st.write(f"📦 **{row['업체명']}** ({row['규격']} {row['수량']}박스)")
                if st.button("배송 시작", key=f"tk_{idx}", use_container_width=True):
                    st.session_state.orders.at[idx, '상태'] = '배송중'
                    st.session_state.orders.at[idx, '배송담당'] = st.session_state.user_name
                    save_data(st.session_state.orders)
                    st.rerun()
        st.divider()
        st.subheader("내 배송 현황")
        mine = st.session_state.orders[(st.session_state.orders['상태'] == '배송중') & (st.session_state.orders['배송담당'] == st.session_state.user_name)]
        for idx, row in mine.iterrows():
            with st.container(border=True):
                st
