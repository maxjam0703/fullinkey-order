import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# 1. 설정
USER_DB = {"admin": ["fullin123", "이사장", "관리자"], "staff1": ["1111", "김기사", "직원"]}
CLIENTS = {"A 인쇄소": "경기 파주", "B 문화사": "서울 을지로", "기타": "직접입력"}
DB_FILE = "fullin_v10.csv"

def load(): return pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=['일시','업체','규격','수량','상태','담당'])
def save(df): df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# 2. 디자인 (파란 박스 안쪽 여백 대폭 강화)
def apply_style():
    st.markdown("""<style>
    .stApp {background:#f8f9fa}
    /* 사이드바 로고 박스 여백 */
    [data-testid='stSidebar'] .stMarkdown h1 {
        background:#003366; color:white; padding:25px 30px!important; border-radius:12px; font-size:22px
    }
    /* 상단 탭(주문, 승인 등) 안쪽 여백 대폭 추가 */
    .stTabs [data-baseweb='tab'] {
        height:60px; padding:0 40px!important; background:white; border-radius:10px; margin-right:10px
    }
    .stTabs [aria-selected='true'] {
        background:#003366!important; color:white!important; font-weight:bold
    }
    </style>""", unsafe_allow_html=True)

# 3. 메인 로직
def main():
    st.set_page_config(page_title="Fullinkey", layout="wide")
    apply_style()
    if 'login' not in st.session_state: st.session_state.login = False
    if not st.session_state.login:
        st.title("🔑 Fullinkey 로그인")
        uid, upw = st.text_input("ID"), st.text_input("PW", type="password")
        if st.button("접속", use_container_width=True, type="primary"):
            if uid in USER_DB and USER_DB[uid][0] == upw:
                st.session_state.login = True
                st.session_state.un, st.session_state.ur = USER_DB[uid][1], USER_DB[uid][2]
                st.rerun()
        return
    with st.sidebar:
        st.title("Fullinkey")
        st.write(f"👤 {st.session_state.un}님")
        if st.button("로그아웃"): st.session_state.login=False; st.rerun()
    if 'df' not in st.session_state: st.session_state.df = load()
    t1, t2, t3, t4 = st.tabs(["📝 주문", "👑 승인", "🚚 배송", "📊 현황"])
    with t1:
        name = st.selectbox("업체", list(CLIENTS.keys()))
        sp = st.selectbox("규격", ["0.15mm", "0.30mm", "무현상"])
        qt = st.number_input("수량", min_value=1, value=10)
        if st.button("주문하기", type="primary"):
            new = {'일시':datetime.now().strftime("%m/%d %H:%M"),'업체':name,'규격':sp,'수량':qt,'상태':'대기','담당':'-'}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new])], ignore_index=True)
            save(st.session_state.df); st.success("완료"); st.rerun()
    with t2:
        if st.session_state.ur == "관리자":
            wait = st.session_state.df[st.session_state.df['상태']=='대기']
            for i, r in wait.iterrows():
                if st.button(f"✅ {r['업체']} 승인", key=f"a{i}"):
                    st.session_state.df.at[i,'상태']='배송전'; save(st.session_state.df); st.rerun()
        else: st.info("관리자 전용")
    with t3:
        ready = st.session_state.df[st.session_state.df['상태']=='배송전']
        for i, r in ready.iterrows():
            if st.button(f"🚚 {r['업체']} 시작", key=f"g{i}"):
                st.session_state.df.at[i,'상태']='중'; st.session_state.df.at[i,'담당']=st.session_state.un
                save(st.session_state.df); st.rerun()
        st.divider()
        ing = st.session_state.df[(st.session_state.df['상태']=='중') & (st.session_state.df['담당']==st.session_state.un)]
        for i, r in ing.iterrows():
            if st.button(f"🏁 {r['업체']} 완료", key=f"f{i}", type="primary"):
                st.session_state.df.at[i,'상태']='완료'; save(st.session_state.df); st.rerun()
    with t4: st.dataframe(st.session_state.df.iloc[::-1], use_container_width=True)

if __name__ == "__main__":
    main()
