import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- [설정 1. 사용자 DB] ---
USER_DB = {
    "admin": ["fullin123", "이사장", "관리자"],
    "staff1": ["1111", "김철수 기사", "직원"],
    "staff2": ["2222", "박영희 대리", "직원"]
}

# --- [설정 2. 거래처 상세 정보] ---
CLIENT_INFO = {
    "A 인쇄소": {"주소": "경기도 파주시 문발로 123", "담당자": "강본부장", "연락처": "010-1234-5678"},
    "B 문화사": {"주소": "서울시 중구 을지로 45", "담당자": "이실장", "연락처": "010-9876-5432"},
    "C 패키지": {"주소": "인천시 서구 가좌동 78", "담당자": "최과장", "연락처": "010-5555-4444"},
    "기타": {"주소": "직접입력 필요", "담당자": "확인요망", "연락처": "000-0000-0000"}
}

DB_FILE = "fullinkey_orders_final_v2.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['주문일시', '업체명', '주소', '담당자', '연락처', '규격', '수량', '주문자', '상태', '승인자', '배송담당'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'orders' not in st.session_state:
    st.session_state.orders = load_data()

# --- [로그인 화면] ---
def login_screen():
    st.title("🔑 Full In Key 로그인")
    user_id = st.text_input("아이디")
    user_pw = st.text_input("비밀번호", type="password")
    if st.button("로그인", use_container_width=True):
        if user_id in USER_DB and USER_DB[user_id][0] == user_pw:
            st.session_state.logged_in = True
            st.session_state.user_name = USER_DB[user_id][1]
            st.session_state.user_role = USER_DB[user_id][2]
            st.rerun()
        else:
            st.error("정보가 일치하지 않습니다.")

# --- [메인 시스템] ---
def main_system():
    with st.sidebar:
        st.title("메뉴")
        st.write(f"👤 **{st.session_state.user_name}**")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 주문등록", "👑 승인대기", "🚚 배송업무", "📊 현황"])

    # --- 1. 주문 등록 ---
    with tab1:
        st.subheader("새 주문 넣기")
        client_name = st.selectbox("거래처 선택", list(CLIENT_INFO.keys()))
        info = CLIENT_INFO[client_name]
        st.info(f"🏠 {info['주소']}\n📞 담당: {info['담당자']} ({info['연락처']})")
        spec = st.select_slider("규격 선택", options=["0.15mm", "0.30mm", "무현상"])
        count = st.number_input("수량(박스)", min_value=1, value=10)
        if st.button("🚀 주문 전송", use_container_width=True, type="primary"):
            new_order = {
                '주문일시': datetime.now().strftime("%m/%d %H:%M"),
                '업체명': client_name, '주소': info['주소'], '담당자': info['담당자'], '연락처': info['연락처'],
                '규격': spec, '수량': count, '주문자': st.session_state.user_name,
                '상태': '승인대기', '승인자': '-', '배송담당': '-'
            }
            st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
            save_data(st.session_state.orders)
            st.success("접수 완료!")

    # --- 2. 승인 대기 ---
    with tab2:
        if st.session_state.user_role == "관리자":
            pending = st.session_state.orders[st.session_state.orders['상태'] == '승인대기']
            if not pending.empty:
                for idx, row in pending.iterrows():
                    with st.container(border=True):
                        st.write(f"**[{row['업체명']}]** {row['규격']} / {row['수량']}박스")
                        if st.button("✅ 주문 승인", key=f"app_{idx}", use_container_width=True):
                            st.session_state.orders.at[idx, '상태'] = '배송대기'
                            st.session_state.orders.at[idx, '승인자'] = st.session_state.user_name
                            save_data(st.session_state.orders)
                            st.rerun()
            else:
                st.info("대기 주문이 없습니다.")
        else:
            st.warning("🔒 관리자(이사장) 전용 메뉴입니다.")

    # --- 3. 배송 업무 ---
    with tab3:
        st.subheader("📦 배송 가능 목록")
        wait_list = st.session_state.orders[st.session_state.orders['상태'] == '배송대기']
        for idx, row in wait_list.iterrows():
            with st.container(border=True):
                st.write(f"📍 **{row['업체명']}** ({row['규격']} {row['수량']}박스)")
                if st.button("🙋‍♂️ 내가 배송하기", key=f"take_{idx}", use_container_width=True):
                    st.session_state.orders.at[idx, '상태'] = '배송중'
                    st.session_state.orders.at[idx, '배송담당'] = st.session_state.user_name
                    save_data(st.session_state.orders)
                    st.rerun()
        
        st.divider()
        st.subheader("🚚 나의 배송 현황")
        my_list = st.session_state.orders[(st.session_state.orders['상태'] == '배송중') & (st.session_state.orders['배송담당'] == st.session_state.user_name)]
        for idx, row in my_list.iterrows():
            with st.container(border=True):
                st.markdown(f"### {row['업체명']}")
                st.write(f"🏠 {row['주소']}")
                c1, c2 = st.columns(2)
                c1.link_button("📞 전화", f"tel:{row['연락처']}", use_container_width=True)
                map_url = f"https://map.kakao.com/link/search/{urllib.parse.quote(row['주소'])}"
                c2.link_button("🗺️ 길찾기", map_url, use_container_width=True)
                if st.button("🏁 배송 완료 처리", key=f"done_{idx}", use_container_width=True, type="primary"):
                    st.session_state.orders.at[idx, '상태'] = '배송완료'
                    save_data(st.session_state.orders)
                    st.rerun()

    # --- 4. 현황 보기 ---
    with tab4:
        recent = st.session_state.orders.iloc[::-1].head(15)
        for idx, row in recent.iterrows():
            with st.container(border=True):
                st.write(f"**{row['상태']}** | {row['업체명']} ({row['주문일시']})")
                st.caption(f"{row['규격']} {row['수량']}박스 / 배송담당: {row['배송담당']}")

# --- 실행 ---
if not st.session_state.logged_in:
    st.set_page_config(page_title="Login", layout="centered")
    login_screen()
else:
    st.set_page_config(page_title="Full In Key", layout="wide")
    main_system()
