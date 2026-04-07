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

# 세션 관리
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'orders' not in st.session_state:
    st.session_state.orders = load_data()

# --- [로그인 화면] ---
def login_screen():
    st.title("🔑 Full In Key")
    st.caption("스마트 주문 관리 시스템")
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
    # 사이드바를 모바일에서도 보기 편하게 최소화
    with st.sidebar:
        st.title("메뉴")
        st.write(f"👤 **{st.session_state.user_name}** ({st.session_state.user_role})")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.title("📦 Full In Key 주문")
    
    # 탭 메뉴로 화면 분할 (모바일에서 넘겨보기 편함)
    tab1, tab2, tab3 = st.tabs(["📝 주문등록", "🔔 승인관리", "📊 전체현황"])

    # --- TAB 1: 주문 등록 ---
    with tab1:
        with st.expander("신규 주문 입력하기", expanded=True):
            client = st.selectbox("거래처 선택", ["A 인쇄소", "B 문화사", "C 패키지", "기타"])
            spec = st.select_slider("판재 규격", options=["0.15mm", "0.30mm", "무현상"])
            count = st.number_input("수량(박스)", min_value=1, value=10, step=5)
            
            if st.button("🚀 주문 전송", use_container_width=True):
                new_order = {
                    '주문일시': datetime.now().strftime("%m/%d %H:%M"),
                    '업체명': client, '규격': spec, '수량': count,
                    '주문자': st.session_state.user_name,
                    '상태': '대기', '승인자': '-', '배송담당': '-'
                }
                st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
                save_data(st.session_state.orders)
                st.success("주문이 완료되었습니다!")

    # --- TAB 2: 승인 관리 ---
    with tab2:
        if st.session_state.user_role == "관리자":
            pending = st.session_state.orders[st.session_state.orders['상태'] == '대기']
            if not pending.empty:
                for idx, row in pending.iterrows():
                    # 모바일 최적화: 카드 스타일 레이아웃
                    with st.container(border=True):
                        st.subheader(f"📍 {row['업체명']}")
                        st.write(f"**규격:** {row['규격']} / **수량:** {row['수량']}박스")
                        st.caption(f"요청: {row['주문자']} ({row['주문일시']})")
                        
                        d_man = st.selectbox("배송자", ["김기사", "이대리", "외부용달"], key=f"d_{idx}")
                        
                        col_a, col_b = st.columns(2)
                        if col_a.button("✅ 승인", key=f"app_{idx}", use_container_width=True):
                            st.session_state.orders.at[idx, '상태'] = '완료'
                            st.session_state.orders.at[idx, '승인자'] = st.session_state.user_name
                            st.session_state.orders.at[idx, '배송담당'] = d_man
                            save_data(st.session_state.orders)
                            st.rerun()
                        if col_b.button("❌ 반려", key=f"rej_{idx}", use_container_width=True):
                            st.session_state.orders.at[idx, '상태'] = '반려'
                            save_data(st.session_state.orders)
                            st.rerun()
            else:
                st.info("대기 중인 주문이 없습니다.")
        else:
            st.warning("관리자 권한이 필요합니다.")

    # --- TAB 3: 현황 보기 ---
    with tab3:
        # 모바일에서는 표를 작게 보여주고 다운로드 버튼 제공
        st.write("최근 주문 10건")
        st.dataframe(st.session_state.orders.iloc[::-1].head(10), use_container_width=True)
        
        csv = st.session_state.orders.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📩 전체 내역 엑셀 저장", csv, "orders.csv", use_container_width=True)

# 실행
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login", layout="centered")
    login_screen()
else:
    st.set_page_config(page_title="Full In Key", layout="wide")
    main_system()