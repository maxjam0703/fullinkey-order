import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# 1. 사용자 및 거래처 설정
USER_DB = {"admin": ["fullin123", "이사장", "관리자"], "staff1": ["1111", "김기사", "직원"]}
CLIENTS = {
    "A 인쇄소": {"주소": "경기도 파주시 문발로 123", "전화": "010-1234-5678"},
    "B 문화사": {"주소": "서울시 중구 을지로 45", "전화": "010-9876-5432"},
    "기타": {"주소": "직접입력", "전화": "000-0000-0000"}
}
DB_FILE = "orders_v6.csv"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['일시','업체','주소','연락처','규격','수량','상태','담당'])

def save_data(df): df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# 2. 디자인 (홈페이지 느낌 반영)
st.set_page_config(page_title="Fullinkey", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    h1, h2, .stTabs [aria-selected="true"] { color: white !important; background-color: #003366 !important; border-radius: 5px; }
    .stButton>button { border-radius: 8px; height: 3em; background-color: #003366; color: white; }
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

if 'login' not in st.session_state: st.session_state.login = False

# 3. 로그인 화면
if not st.session_state.login:
    st.title("🔑 Fullinkey 로그인")
    uid = st.text_input("아이디")
    upw = st.text_input("비밀번호", type="password")
    if st.button("접속하기", use_container_width=True):
        if uid in USER_DB and USER_DB[uid][0] == upw:
            st.session_state.login = True
            st.session_state.uname, st.session_state.urole = USER_DB[uid][1], USER_DB[uid][2]
            st.rerun()
        else: st.error("정보가 틀립니다.")
    st.stop()

# 4. 메인 시스템
with st.sidebar:
    st.header("Fullinkey")
    st.write(f"👤 {st.session_state.uname} ({st.session_state.urole})")
    if st.button("로그아웃"): 
        st.session_state.login = False
        st.rerun()

if 'df' not in st.session_state: st.session_state.df = load_data()
t1, t2, t3, t4 = st.tabs(["📝 주문", "👑 승인", "🚚 배송", "📊 현황"])

with t1:
    st.subheader("신규 주문등록")
    name = st.selectbox("업체선택", list(CLIENTS.keys()))
    c_info = CLIENTS[name]
    st.caption(f"📍 {c_info['주소']}")
    col_a, col_b = st.columns(2)
    spec = col_a.selectbox("규격", ["0.15mm", "0.30mm", "무현상"])
    qty = col_b.number_input("수량", min_value=1, value=10)
    if st.button("주문 전송", type="primary"):
        new = {'일시': datetime.now().strftime("%m/%d %H:%M"), '업체': name, '주소': c_info['주소'], 
               '연락처': c_info['전화'], '규격': spec, '수량': qty, '상태': '대기', '담당': '-'}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new])], ignore_index=True)
        save_data(st.session_state.df); st.success("접수완료!"); st.rerun()

with t2:
    if st.session_state.urole == "관리자":
        wait = st.session_state.df[st.session_state.df['상태']=='대기']
        for i, r in wait.iterrows():
            with st.container(border=True):
                st.write(f"**{r['업체']}** ({r['규격']} {r['수량']}박스)")
                if st.button("승인", key=f"ap_{i}"):
                    st.session_state.df.at[i, '상태'] = '배송전'; save_data(st.session_state.df); st.rerun()
    else: st.info("권한 없음")

with t3:
    st.subheader("배송 리스트")
    ready = st.session_state.df[st.session_state.df['상태']=='배송전']
    for i, r in ready.iterrows():
        with st.container(border=True):
            st.write(f"🚚 **{r['업체']}**")
            if st.button("배송시작", key=f"go_{i}"):
                st.session_state.df.at[i, '상태'] = '중'; st.session_state.df.at[i, '담당'] = st.session_state.uname
                save_data(st.session_state.df); st.rerun()
    st.divider()
    ing = st.session_state.df[(st.session_state.df['상태']=='중') & (st.session_state.df['담당']==st.session_state.uname)]
    for i, r in ing.iterrows():
        with st.container(border=True):
            st.write(f"📍 {r['업체']}")
            c1, c2, c3 = st.columns(3)
            c1.link_button("📞전화", f"tel:{r['연락처']}")
            c2.link_button("🗺️지도", f"https://map.kakao.com/link/search/{urllib.parse.quote(r['주소'])}")
            if c3.button("완료", key=f"ok_{i}"):
                st.session_state.df.at[i, '상태'] = '완료'; save_data(st.session_state.df); st.rerun()

with t4:
    st.dataframe(st.session_state.df.iloc[::-1], use_container_width=True)
