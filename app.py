import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 설정 및 데이터 경로
USER_DB = {"admin": ["fullin123", "이사장", "관리자"], "staff1": ["1111", "김기사", "직원"]}
CLIENTS = {"A 인쇄소": "경기 파주", "B 문화사": "서울 을지로", "기타": "직접입력"}
ORDER_FILE = "orders_v20.csv"
STOCK_FILE = "stock_v20.csv"

def load_data():
    cols = ['일시', '업체', '규격', '수량', '상태', '담당', '완료시간']
    orders = pd.read_csv(ORDER_FILE) if os.path.exists(ORDER_FILE) else pd.DataFrame(columns=cols)
    if '완료시간' not in orders.columns:
        orders['완료시간'] = '-'
    stock = pd.read_csv(STOCK_FILE) if os.path.exists(STOCK_FILE) else pd.DataFrame({'규격': ["0.15mm", "0.30mm", "무현상"], '현재고': [500, 500, 500]})
    return orders, stock

def save_data(orders, stock):
    orders.to_csv(ORDER_FILE, index=False, encoding='utf-8-sig')
    stock.to_csv(STOCK_FILE, index=False, encoding='utf-8-sig')

# 2. 디자인
def apply_style():
    st.markdown("""<style>
    .stApp {background:#f8f9fa}
    [data-testid='stSidebar'] .stMarkdown h1 {background:#003366;color:white;padding:25px!important;border-radius:12px;font-size:22px}
    .stTabs [data-baseweb='tab'] {height:65px;padding:0 35px!important;background:white;border-radius:10px;margin-right:10px;border:1px solid #ddd}
    .stTabs [aria-selected='true'] {background:#003366!important;color:white!important;font-weight:bold}
    .stMetric {background:white; padding:20px; border-radius:15px; border:1px solid #eee}
    </style>""", unsafe_allow_html=True)

# 3. 메인 로직
def main():
    st.set_page_config(page_title="Fullinkey", layout="wide")
    apply_style()
    
    if 'login' not in st.session_state: st.session_state.login = False

    if not st.session_state.login:
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.title("🔑 Fullinkey 로그인")
            uid = st.text_input("아이디")
            upw = st.text_input("비밀번호", type="password")
            if st.button("접속하기", use_container_width=True, type="primary"):
                if uid in USER_DB and USER_DB[uid][0] == upw:
                    st.session_state.login, st.session_state.un, st.session_state.ur = True, USER_DB[uid][1], USER_DB[uid][2]
                    st.rerun()
                else: st.error("정보가 틀립니다.")
        return

    with st.sidebar:
        st.title("Fullinkey")
        st.write(f"👤 **{st.session_state.un}**님 ({st.session_state.ur})")
        if st.button("🔴 로그아웃", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    orders, stock = load_data()
    t1, t2, t3, t4, t5, t6 = st.tabs(["📝 주문등록", "👑 승인관리", "🚚 배송업무", "📦 재고현황", "📊 전체이력", "📈 분석현황"])

    with t1: # 주문 등록
        st.subheader("신규 주문")
        name = st.selectbox("업체", list(CLIENTS.keys()))
        sp = st.selectbox("규격", stock['규격'].tolist())
        cur_s = stock[stock['규격']==sp]['현재고'].values[0]
        st.write(f"현재고: **{cur_s}** 박스")
        qt = st.number_input("수량", min_value=1, max_value=int(cur_s), value=10)
        if st.button("주문 전송", type="primary", use_container_width=True):
            new = {'일시':datetime.now().strftime("%m/%d %H:%M"),'업체':name,'규격':sp,'수량':qt,'상태':'대기','담당':'-','완료시간':'-'}
            orders = pd.concat([orders, pd.DataFrame([new])], ignore_index=True)
            stock.loc[stock['규격']==sp, '현재고'] -= qt
            save_data(orders, stock); st.success("주문 완료!"); st.rerun()

    with t2: # 승인 관리
        st.subheader("승인 대기")
        wait = orders[orders['상태']=='대기']
        if len(wait) == 0: st.write("✅ 대기 중인 주문이 없습니다.")
        for i, r in wait.iterrows():
            with st.container(border=True):
                st.write(f"**{r['업체']}** | {r['규격']} {r['수량']}박스")
                if st.session_state.ur == "관리자":
                    if st.button(f"승인하기", key=f"ap_{i}", use_container_width=True):
                        orders.at[i,'상태']='배송전'; save_data(orders, stock); st.rerun()
                else: st.caption("🕒 승인 대기 중...")

    with t3: # 배송 업무
        st.subheader("배송 진행 상황")
        ready = orders[orders['상태']=='배송전']
        if len(ready) > 0:
            st.write("📦 **배송 준비 중**")
            for i, r in ready.iterrows():
                with st.container(border=True):
                    st.write(f"**{r['업체']}** ({r['규격']})")
                    if st.button("배송 출발", key=f"go_{i}", use_container_width=True):
                        orders.at[i,'상태']='중'; orders.at[i,'담당']=st.session_state.un
                        save_data(orders, stock); st.rerun()
        st.divider()
        ing = orders[orders['상태']=='중']
        if len(ing) > 0:
            st.write("🚚 **현재 배송 중**")
            for i, r in ing.iterrows():
                with st.container(border=True):
                    st.write(f"📍 **{r['업체']}** (담당: {r['담당']})")
                    if st.session_state.un == r['담당'] or st.session_state.ur == "관리자":
                        if st.button("완료 처리", key=f"fi_{i}", type="primary", use_container_width=True):
                            orders.at[i,'상태']='완료'
                            orders.at[i,'완료시간']=datetime.now().strftime("%m/%d %H:%M")
                            save_data(orders, stock); st.rerun()
                    else: st.caption(f"✅ {r['담당']}님이 배송 중입니다.")

    with t4: # 재고 현황
        st.subheader("실시간 재고")
        cols = st.columns(3)
        for i, row in stock.iterrows():
            cols[i].metric(row['규격'], f"{row['현재고']} 박스")
        if st.session_state.ur == "관리자":
            st.divider()
            e_sp = st.selectbox("조정 규격", stock['규격'].tolist())
            n_v = st.number_input("수량 수정", value=int(stock[stock['규격']==e_sp]['현재고'].values[0]))
            if st.button("재고 수정 반영"):
                stock.loc[stock['규격']==e_sp, '현재고'] = n_v
                save_data(orders, stock); st.success("수정됨"); st.rerun()

    with t5: # 전체 이력
        st.subheader("전체 주문 및 배송 이력")
        st.dataframe(orders.iloc[::-1], use_container_width=True)

    with t6: # 분석 현황 (불필요한 라벨 제거)
        st.subheader("업체별 주문 수량 분석")
        if len(orders) > 0:
            chart_data = orders.groupby('업체')['수량'].sum().reset_index()
            # y-axis 라벨(업체)을 빈 문자열로 처리하여 제거
            st.bar_chart(data=chart_data, x='업체', y='수량', color="#003366", horizontal=True, x_label="", y_label="")
            
            st.divider()
            st.subheader("규격별 주문 비중")
            spec_data = orders.groupby('규격')['수량'].sum().reset_index()
            # y-axis 라벨(규격)을 빈 문자열로 처리하여 제거
            st.bar_chart(data=spec_data, x='규격', y='수량', horizontal=True, x_label="", y_label="")
        else:
            st.info("데이터가 충분하지 않습니다.")

if __name__ == "__main__":
    main()
