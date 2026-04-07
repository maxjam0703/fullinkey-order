import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# 1. 기본 설정 (사용자, 거래처, 파일명)
USER_DB = {"admin": ["fullin123", "이사장", "관리자"], "staff1": ["1111", "김기사", "직원"]}
CLIENTS = {"A 인쇄소": "경기 파주", "B 문화사": "서울 을지로", "기타": "직접입력"}
ORDER_FILE = "fullin_orders_v11.csv"
STOCK_FILE = "fullin_stock_v11.csv"

# 2. 데이터 관리 함수
def load_data():
    orders = pd.read_csv(ORDER_FILE) if os.path.exists(ORDER_FILE) else pd.DataFrame(columns=['일시','업체','규격','수량','상태','담당'])
    # 재고 데이터가 없으면 초기값(각 500박스) 생성
    if os.path.exists(STOCK_FILE):
        stock = pd.read_csv(STOCK_FILE)
    else:
        stock = pd.DataFrame({'규격': ["0.15mm", "0.30mm", "무현상"], '현재고': [500, 500, 500]})
    return orders, stock

def save_data(orders, stock):
    orders.to_csv(ORDER_FILE, index=False, encoding='utf-8-sig')
    stock.to_csv(STOCK_FILE, index=False, encoding='utf-8-sig')

# 3. 디자인 (파란 박스 여백 및 스타일)
def apply_style():
    st.markdown("""<style>
    .stApp {background:#f8f9fa}
    [data-testid='stSidebar'] .stMarkdown h1 {background:#003366;color:white;padding:25px!important;border-radius:12px;font-size:22px}
    /* 탭 안쪽 여백 대폭 강화 */
    .stTabs [data-baseweb='tab'] {height:60px;padding:0 35px!important;background:white;border-radius:10px;margin-right:8px;border:1px solid #ddd}
    .stTabs [aria-selected='true'] {background:#003366!important;color:white!important;font-weight:bold;border:none}
    .stMetric {background:white; padding:20px; border-radius:15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05)}
    </style>""", unsafe_allow_html=True)

# 4. 메인 로직
def main():
    st.set_page_config(page_title="Fullinkey System", layout="wide")
    apply_style()
    
    if 'login' not in st.session_state: st.session_state.login = False
    if not st.session_state.login:
        st.title("🔑 Fullinkey 로그인")
        uid, upw = st.text_input("아이디"), st.text_input("비밀번호", type="password")
        if st.button("접속하기", use_container_width=True, type="primary"):
            if uid in USER_DB and USER_DB[uid][0] == upw:
                st.session_state.login, st.session_state.un, st.session_state.ur = True, USER_DB[uid][1], USER_DB[uid][2]
                st.rerun()
        return

    with st.sidebar:
        st.title("Fullinkey")
        st.write(f"👤 **{st.session_state.un}**님 접속 중")
        if st.button("로그아웃", use_container_width=True): st.session_state.login=False; st.rerun()

    orders, stock = load_data()
    t1, t2, t3, t4, t5 = st.tabs(["📝 주문등록", "👑 승인관리", "🚚 배송업무", "📦 재고현황", "📊 전체이력"])

    with t1: # 주문 등록 (재고 차감 로직 포함)
        st.subheader("신규 주문 작성")
        name = st.selectbox("거래처 선택", list(CLIENTS.keys()))
        sp = st.selectbox("규격 선택", stock['규격'].tolist())
        current_s = stock[stock['규격']==sp]['현재고'].values[0]
        st.write(f"💡 현재고: **{current_s}** 박스")
        qt = st.number_input("주문 수량", min_value=1, max_value=int(current_s), value=10)
        
        if st.button("🚀 주문 전송", type="primary", use_container_width=True):
            # 주문 저장
            new = {'일시':datetime.now().strftime("%m/%d %H:%M"),'업체':name,'규격':sp,'수량':qt,'상태':'대기','담당':'-'}
            orders = pd.concat([orders, pd.DataFrame([new])], ignore_index=True)
            # 재고 차감
            stock.loc[stock['규격']==sp, '현재고'] -= qt
            save_data(orders, stock); st.success(f"{name} 주문 완료! 재고가 업데이트되었습니다."); st.rerun()

    with t2: # 승인 관리
        if st.session_state.ur == "관리자":
            wait = orders[orders['상태']=='대기']
            for i, r in wait.iterrows():
                with st.container(border=True):
                    st.write(f"**{r['업체']}** | {r['규격']} {r['수량']}박스")
                    if st.button(f"승인하기", key=f"a{i}", use_container_width=True):
                        orders.at[i,'상태']='배송전'; save_data(orders, stock); st.rerun()
        else: st.info("관리자 권한이 필요합니다.")

    with t3: # 배송 업무
        ready = orders[orders['상태']=='배송전']
        for i, r in ready.iterrows():
            with st.container(border=True):
                st.write(f"🚚 {r['업체']} ({r['규격']})")
                if st.button("배송 시작", key=f"g{i}", use_container_width=True):
                    orders.at[i,'상태']='중'; orders.at[i,'담당']=st.session_state.un
                    save_data(orders, stock); st.rerun()
        st.divider()
        ing = orders[(orders['상태']=='중') & (orders['담당']==st.session_state.un)]
        for i, r in ing.iterrows():
            with st.container(border=True):
                st.write(f"📍 {r['업체']} 배송 중"); c1, c2 = st.columns(2)
                if c1.button("🏁 완료", key=f"f{i}", type="primary", use_container_width=True):
                    orders.at[i,'상태']='완료'; save_data(orders, stock); st.rerun()
                c2.button("📞 연락처 확인", on_click=lambda: st.toast("연락처: 010-XXXX-XXXX"))

    with t4: # 재고 현황 (새로 추가됨)
        st.subheader("실시간 재고 현황")
        cols = st.columns(3)
        for i, row in stock.iterrows():
            with cols[i]:
                st.metric(label=row['규격'], value=f"{row['현재고']} 박스")
        st.divider()
        st.write("🛠️ **재고 수동 조정 (관리자)**")
        if st.session_state.ur == "관리자":
            edit_sp = st.selectbox("수정할 규격", stock['규격'].tolist(), key="edit_sp")
            new_val = st.number_input("조정할 수량", value=int(stock[stock['규격']==edit_sp]['현재고'].values[0]))
            if st.button("재고 반영"):
                stock.loc[stock['규격']==edit_sp, '현재고'] = new_val
                save_data(orders, stock); st.success("재고가 수정되었습니다."); st.rerun()

    with t5: # 전체 이력
        st.subheader("전체 주문 처리 현황")
        st.dataframe(orders.iloc[::-1], use_container_width=True)

if __name__ == "__main__":
    main()
