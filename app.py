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
        st.subheader("📊 주문 기록 (최근 10건)")
        
        # 최신순으로 10개만 가져오기
        recent_orders = st.session_state.orders.iloc[::-1].head(10)
        
        if not recent_orders.empty:
            for idx, row in recent_orders.iterrows():
                # 상태에 따라 다른 색상 이모지 표시
                status_emoji = "⏳" if row['상태'] == '대기' else "✅" if row['상태'] == '완료' else "❌"
                
                # 모바일용 카드 레이아웃
                with st.container(border=True):
                    # 제목줄: 상태와 업체명
                    st.markdown(f"### {status_emoji} {row['업체명']}")
                    
                    # 상세 내용 (한 줄에 2개씩)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**규격:** {row['규격']}")
                        st.write(f"**수량:** {row['수량']}박스")
                    with c2:
                        st.write(f"**주문자:** {row['주문자']}")
                        st.write(f"**배송:** {row['배송담당']}")
                    
                    # 날짜 (작게 표시)
                    st.caption(f"📅 주문일시: {row['주문일시']}")
        else:
            st.info("기록된 주문이 없습니다.")

        st.divider()
        # 엑셀 다운로드는 여전히 버튼으로 제공 (필요할 때 PC에서 받기용)
        csv = st.session_state.orders.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📩 전체 내역 엑셀 다운로드", csv, "orders.csv", use_container_width=True)

# 실행
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login", layout="centered")
    login_screen()
else:
    st.set_page_config(page_title="Full In Key", layout="wide")
    main_system()
