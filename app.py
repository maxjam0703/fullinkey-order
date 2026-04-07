import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# 1. 기본 설정 및 데이터 로드
USER_DB = {"admin": ["fullin123", "이사장", "관리자"], "staff1": ["1111", "김기사", "직원"]}
CLIENTS = {
    "A 인쇄소": {"주소": "경기도 파주시 문발로 123", "전화": "010-1234-5678"},
    "B 문화사": {"주소": "서울시 중구 을지로 45", "전화": "010-9876-5432"},
    "기타": {"주소": "직접입력", "전화": "000-0000-0000"}
}
DB_FILE = "fullin_data_v7.csv"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['일시','업체','주소','연락처','규격','수량','상태','담당'])

def save_data(df): df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# 2. 디자인 설정 (여백 및 톤앤매너 개선)
st.set_page_config(page_title="Fullinkey", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    /* 사이드바 로고 박스 여백 부여 */
    [data-testid="stSidebar"] .stMarkdown h1 {
        background-color: #003366; color: white !important;
        padding: 20px !important; border-radius: 12px;
        font-size: 22px; margin-bottom: 20px;
    }
    /* 상단 탭 여백 및 디자인 */
    .stTabs [data-baseweb="tab"] {
        height: 50px; padding: 0 30px !important;
        background-color: white; border-radius: 8px; border: 1px solid #ddd;
    }
    .stTabs [aria-selected="true"] {
        background-color: #003366 !important; color: white !important;
    }
    .stButton>button { border-radius: 8px; height: 3em; }
    </style>
""", unsafe_allow_html=True)

if 'login' not in st.session_state: st.session_state.login = False

# 3. 로그인 화면
if not st.session_state.login:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("🔑 Fullinkey 로그인")
        with st.container(border=True):
            uid = st.text_input("아이디")
            upw = st.text_input("비밀번호", type="password")
            if st.button("접속하기", use_container_width=True, type="primary"):
                if uid in USER_DB and USER_DB[uid][0] == upw:
                    st.session_state.login = True
                    st.session_state.uname, st.session_state.urole = USER_DB[uid][1], USER_DB[uid][2]
                    st.rerun()
                else: st.error("정보가 틀립니다.")
    st.stop()

# 4. 메인 시스템
with st.sidebar:
    st.title("Fullinkey") # 여백 적용된 로고
    st.write(f"👤 {st.session_state.uname} ({st.session_state.urole})")
    if st.button("로그아웃"): 
        st.session_state.login = False
        st.rerun()

if 'df' not in st.session_state: st.session_state.df = load_data()
t1, t2, t3, t4 = st.tabs(["📝 주문등록", "👑 승인관리", "🚚 배송업무", "📊 현황"])

with t1:
    st.subheader("신규 주문")
    name = st.selectbox("업체선택", list(CLIENTS.keys()))
    info = CLIENTS[name]
    st.info(f"📍 {info['주소']}")
    c_a, c_b = st.columns(2)
    spec = c_a.selectbox("규격", ["0.15mm", "0.30mm", "무현상"])
    qty = c_b.number_input("수량", min_value=1, value=10)
    if st.button("🚀 주문 전송", type="primary", use_container_width=True):
        new = {'일시': datetime.now().strftime("%m/%d %H:%M"), '업체': name, '주소': info['주소'], '연락처': info['전화'], '규격': spec, '수량': qty, '상태': '대기', '담당': '-'}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new])], ignore_index=True)
        save_data(st.session_state.df); st.success("접수완료!"); st.rerun()

with t2:
    if st.session_state.urole == "관리자":
        wait = st.session_state.df[st.session_state.df['상태']=='대기']
        for i, r in wait.iterrows():
            with st
