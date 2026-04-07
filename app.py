import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- [설정 1. 사용자 DB] ---
USER_DB = {
    "admin": ["fullin123", "이사장", "관리자"],
    "staff1": ["1111", "김철수 기사", "직원"],
    "staff2": ["2222", "박영희 대리", "직원"]
}

DB_FILE = "fullinkey_orders.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['주문일시', '업체명', '규격', '수량', '주문자', '상태', '승인자', '배송담당'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'orders' not in st.session_state:
    st.session_state.orders = load_data()

# --- [로그인 화면] ---
def login_screen():
    st.title("🔑 Full In Key")
    with st.container():
        user_id = st.text_input("아이디")
        user_pw = st.text_input("비밀번호", type="password")
        if st.button("로그인", use_container_width=True):
            if user_id in USER_DB and USER_DB[user_id][0] == user_pw:
                st.session_state.logged_in = True
                st.session_state.user_name = USER_DB[user_id][1]
                st.session_state.user_role = USER_DB[user_id][2]
                st.rerun()
            else:
                st.error("아이디/비밀번호 오류")

# --- [메인 시스템] ---
def main_system():
    with st.sidebar:
        st.title("메뉴")
        st.write(f"👤 **{st.session_state.user_name}**")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.title("📦 Full In Key 주문관리")
    
    # 탭 구성: 입력 / 사장님 승인 / 기사님 배송 / 현황
    tab1, tab2, tab3, tab4 = st.tabs(["📝 주문등록", "👑 승인대기", "🚚 배송업무", "📊 전체현황"])

    # --- 1. 주문 등록 (모든 직원) ---
    with tab1:
        with st.expander("신규 주문 입력", expanded=True):
            client = st.selectbox("거래처", ["A 인쇄소", "B 문화사", "C 패키지", "기타"])
            spec = st.select_slider("규격", options=["0.15mm", "0.30mm", "무현상"])
            count = st.number_input("수량(박스)", min_value=1, value=10)
            if st.button("🚀 주문 전송", use_container_width=True):
                new_order = {
                    '주문일시': datetime.now().strftime("%m/%d %H:%M"),
                    '업체명': client, '규격': spec, '수량': count,
                    '주문자': st.session_state.user_name,
                    '상태': '승인대기', '승인자': '-', '배송담당': '-'
                }
                st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
                save_data(st.session_state.orders)
                st.success("접수 완료! 사장님 승인을 기다립니다.")

    # --- 2. 승인 관리 (관리자 전용) ---
    with tab2:
        if st.session_state.user_role == "관리자":
            pending = st.session_state.orders[st.session_state.orders['상태'] == '승인대기']
            if not pending.empty:
                for idx, row in pending.iterrows():
                    with st.container(border=True):
                        st.subheader(f"📍 {row['업체명']}")
                        st.write(f"{row['규격']} / {row['수량']}박스 (요청: {row['주문자']})")
                        if st.button("✅ 주문 승인하기", key=f"admin_app_{idx}", use_container_width=True):
                            st.session_state.orders.at[idx, '상태'] = '배송대기'
                            st.session_state.orders.at[idx, '승인자'] = st.session_state.user_name
                            save_data(st.session_state.orders)
                            st.rerun()
            else:
                st.info("새로 들어온 주문이 없습니다.")
        else:
            st.warning("🔒 이 사장님 전용 메뉴입니다.")

    # --- 3. 배송 업무 (배송 직원용) ---
    with tab3:
        st.subheader("🚚 현재 배송 가능 목록")
        # 승인이 완료된 '배송대기' 주문들
        delivery_pending = st.session_state.orders[st.session_state.orders['상태'] == '배송대기']
        
        if not delivery_pending.empty:
            for idx, row in delivery_pending.iterrows():
                with st.container(border=True):
                    st.write(f"**[배송요청]** {row['업체명']} ({row['규격']} {row['수량']}박스)")
                    if st.button(f"🙋‍♂️ 내가 배송하기", key=f"del_take_{idx}", use_container_width=True):
                        st.session_state.orders.at[idx, '상태'] = '배송중'
                        st.session_state.orders.at[idx, '배송담당'] = st.session_state.user_name
                        save_data(st.session_state.orders)
                        st.rerun()
        
        st.divider()
        st.subheader("📦 나의 배송중 목록")
        # 내가 선택한 '배송중' 주문들
        my_delivery = st.session_state.orders[
            (st.session_state.orders['상태'] == '배송중') & 
            (st.session_state.orders['배송담당'] == st.session_state.user_name)
        ]
        if not my_delivery.empty:
            for idx, row in my_delivery.iterrows():
                with st.container(border=True):
                    st.write(f"🏠 {row['업체명']}로 이동 중...")
                    if st.button("🏁 배송 완료 처리", key=f"del_fin_{idx}", use_container_width=True):
                        st.session_state.orders.at[idx, '상태'] = '배송완료'
                        save_data(st.session_state.orders)
                        st.rerun()
        else:
            st.caption("선택한 배송 건이 없습니다.")

    # --- 4. 전체 현황 (카드 리스트) ---
    with tab4:
        recent = st.session_state.orders.iloc[::-1].head(15)
        for idx, row in recent.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['상태']}** | {row['업체명']}")
                st.caption(f"{row['규격']} {row['수량']}박스 / 배송:{row['배송담당']}")

# 실행 제어
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login", layout="centered")
    login_screen()
else:
    st.set_page_config(page_title="Full In Key", layout="wide")
    main_system()
