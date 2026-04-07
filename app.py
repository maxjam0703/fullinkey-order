import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- [설정 1. 사용자 데이터베이스] ---
USER_DB = {
    "admin": ["fullin123", "이사장", "관리자"],
    "staff1": ["1111", "김철수 기사", "직원"],
    "staff2": ["2222", "박영희 대리", "직원"]
}

# --- [설정 2. 데이터 저장 파일] ---
DB_FILE = "fullinkey_orders.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['주문일시', '업체명', '규격', '수량', '주문자', '상태', '승인자', '배송담당'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- [시스템 초기화] ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'orders' not in st.session_state:
    st.session_state.orders = load_data()

# --- [화면 1. 로그인 화면] ---
def login_screen():
    st.title("🔑 Full In Key 관리 시스템")
    with st.form("login_form"):
        user_id = st.text_input("아이디")
        user_pw = st.text_input("비밀번호", type="password")
        if st.form_submit_button("접속하기"):
            if user_id in USER_DB and USER_DB[user_id][0] == user_pw:
                st.session_state.logged_in = True
                st.session_state.user_name = USER_DB[user_id][1]
                st.session_state.user_role = USER_DB[user_id][2]
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")

# --- [화면 2. 메인 시스템] ---
def main_system():
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.write(f"권한: **{st.session_state.user_role}**")
    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title("📦 CTP 판재 스마트 주문 관리")
    st.divider()

    # 1. 신규 주문 등록
    st.header("1. 신규 주문 등록")
    with st.form("order_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            client = st.selectbox("거래처", ["A 인쇄소", "B 문화사", "C 패키지", "기타"])
        with c2:
            spec = st.selectbox("규격", ["0.15mm", "0.30mm", "무현상"])
        with c3:
            count = st.number_input("수량(박스)", min_value=1, step=1)
        if st.form_submit_button("주문 저장"):
            new_order = {
                '주문일시': datetime.now().strftime("%Y-%m-%d %H:%M"),
                '업체명': client, '규격': spec, '수량': count,
                '주문자': st.session_state.user_name,
                '상태': '승인대기', '승인자': '-', '배송담당': '-'
            }
            st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
            save_data(st.session_state.orders)
            st.success(f"✅ 주문 접수 완료! (입력: {st.session_state.user_name})")

    st.divider()

    # 2. 주문 승인 (관리자 전용)
    st.header("2. 주문 승인 및 관리")
    if st.session_state.user_role == "관리자":
        pending = st.session_state.orders[st.session_state.orders['상태'] == '승인대기']
        if not pending.empty:
            for idx, row in pending.iterrows():
                with st.expander(f"🔔 [대기] {row['업체명']} ({row['주문자']} 입력)"):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        d_man = st.selectbox("배송자", ["김기사", "이대리", "외부용달"], key=f"d_{idx}")
                    with c2:
                        if st.button("✅ 승인", key=f"app_{idx}"):
                            st.session_state.orders.at[idx, '상태'] = '승인완료'
                            st.session_state.orders.at[idx, '승인자'] = st.session_state.user_name
                            st.session_state.orders.at[idx, '배송담당'] = d_man
                            save_data(st.session_state.orders)
                            st.rerun()
                    with c3:
                        if st.button("❌ 반려", key=f"rej_{idx}"):
                            st.session_state.orders.at[idx, '상태'] = '반려'
                            save_data(st.session_state.orders)
                            st.rerun()
        else:
            st.info("처리할 대기 주문이 없습니다.")
    else:
        st.warning("🔒 관리자 계정으로 접속 시 승인이 가능합니다.")

    st.divider()

    # 3. 전체 현황
    st.header("3. 주문 처리 현황")
    st.dataframe(st.session_state.orders.iloc[::-1], use_container_width=True)

# 실행 제어
if not st.session_state.logged_in:
    st.set_page_config(page_title="Full In Key - Login", layout="centered")
    login_screen()
else:
    st.set_page_config(page_title="Full In Key - Admin", layout="wide")
    main_system()