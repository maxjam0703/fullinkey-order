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
# 실제 주소와 연락처로 수정해서 사용하세요!
CLIENT_INFO = {
    "A 인쇄소": {"주소": "경기도 파주시 문발로 123", "담당자": "강본부장", "연락처": "010-1234-5678"},
    "B 문화사": {"주소": "서울시 중구 을지로 45", "담당자": "이실장", "연락처": "010-9876-5432"},
    "C 패키지": {"주소": "인천시 서구 가좌동 78", "담당자": "최과장", "연락처": "010-5555-4444"},
    "기타": {"주소": "직접입력", "담당자": "확인필요", "연락처": "000-0000-0000"}
}

DB_FILE = "fullinkey_orders_v2.csv" # 데이터 구조가 바뀌므로 파일명을 살짝 변경합니다.

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

# --- [메인 시스템 시작] ---
def main_system():
    st.title("📦 Full In Key 주문관리")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 주문등록", "👑 승인대기", "🚚 배송업무", "📊 전체현황"])

    # --- 1. 주문 등록 ---
    with tab1:
        with st.expander("신규 주문 입력", expanded=True):
            client_name = st.selectbox("거래처 선택", list(CLIENT_INFO.keys()))
            
            # 선택한 거래처 정보 미리보기
            info = CLIENT_INFO[client_name]
            st.caption(f"📍 주소: {info['주소']} | 👤 담당: {info['담당자']} | 📞 {info['연락처']}")
            
            spec = st.select_slider("규격", options=["0.15mm", "0.30mm", "무현상"])
            count = st.number_input("수량(박스)", min_value=1, value=10)
            
            if st.button("🚀 주문 전송", use_container_width=True):
                new_order = {
                    '주문일시': datetime.now().strftime("%m/%d %H:%M"),
                    '업체명': client_name,
                    '주소': info['주소'],
                    '담당자': info['담당자'],
                    '연락처': info['연락처'],
                    '규격': spec, '수량': count,
                    '주문자': st.session_state.user_name,
                    '상태': '승인대기', '승인자': '-', '배송담당': '-'
                }
                st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
                save_data(st.session_state.orders)
                st.success(f"{client_name} 주문 접수 완료!")

    # --- 3. 배송 업무 (기사용 모바일 최적화) ---
    with tab3:
        st.subheader("🚚 배송지 정보 확인")
        delivery_list = st.session_state.orders[st.session_state.orders['상태'].isin(['배송대기', '배송중'])]
        
        if not delivery_list.empty:
            for idx, row in delivery_list.iterrows():
                with st.container(border=True):
                    # 상단 업체명 및 상태
                    st.markdown(f"### {row['업체명']} ({row['상태']})")
                    st.write(f"📦 **품목:** {row['규격']} / {row['수량']}박스")
                    
                    # 상세 배송 정보 (중요!)
                    st.info(f"📍 **주소:** {row['주소']}\n\n👤 **수령인:** {row['담당자']} ({row['연락처']})")
                    
                    # 모바일 편의 기능 버튼
                    col1, col2 = st.columns(2)
                    
                    # 전화 걸기 버튼 (tel: 링크 이용)
                    phone_url = f"tel:{row['연락처']}"
                    col1.link_button("📞 전화걸기", phone_url, use_container_width=True)
                    
                    # 길찾기 버튼 (카카오맵 연결)
                    map_url = f"https://map.kakao.com/link/search/{urllib.parse.quote(row['주소'])}"
                    col2.link_button("🗺️ 길찾기", map_url, use_container_width=True)

                    # 상태 변경 버튼
                    if row['상태'] == '배송대기':
                        if st.button(f"🙋‍♂️ 배송 시작", key=f"start_{idx}", use_container_width=True):
                            st.session_state.orders.at[idx, '상태'] = '배송중'
                            st.session_state.orders.at[idx, '배송담당'] = st.session_state.user_name
                            save_data(st.session_state.orders)
                            st.rerun()
                    elif row['상태'] == '배송중' and row['배송담당'] == st.session_state.user_name:
                        if st.button("🏁 배송 완료", key=f"fin_{idx}", use_container_width=True, type="primary"):
                            st.session_state.orders.at[idx, '상태'] = '배송완료'
                            save_data(st.session_state.orders)
                            st.rerun()
        else:
            st.info("현재 처리할 배송 건이 없습니다.")

    # (나머지 로그인/메인 실행 코드는 이전과 동일)
