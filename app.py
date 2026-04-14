이사장님, 역시 관리에 베테랑이시네요! 카테고리(탭) 이름 옆에 **빨간색 느낌표(!)**나 숫자를 표시해 두면, 사장님이 일일이 눌러보지 않아도 "아, 지금 승인할 게 몇 건 있구나" 하고 즉시 알 수 있어 훨씬 효율적입니다.

보내주신 탭 메뉴 이미지를 바탕으로, **'승인 대기 건수'**나 '배송 대기 건수', 그리고 **'재고 부족 알림'**이 실시간으로 숫자로 나타나도록 코드를 업그레이드했습니다.

이번에도 아래 전체 코드를 복사해서 app.py에 덮어씌워 주세요.

Python
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 설정 및 데이터 경로
USER_DB = {"admin": ["fullin123", "이사장", "관리자"], "staff1": ["1111", "김기사", "직원"]}
CLIENTS = {"A 인쇄소": "경기 파주", "B 문화사": "서울 을지로", "기타": "직접입력"}
ORDER_FILE = "orders_v24.csv"
STOCK_FILE = "stock_v24.csv"

def load_data():
    cols = ['일시', '업체', '규격', '수량', '상태', '담당', '완료시간']
    orders = pd.read_csv(ORDER_FILE) if os.path.exists(ORDER_FILE) else pd.DataFrame(columns=cols)
    if '완료시간' not in orders.columns:
        orders['완료시간'] = '-'
    
    if os.path.exists(STOCK_FILE):
        stock = pd.read_csv(STOCK_FILE)
        if '안전재고' not in stock.columns:
            stock['안전재고'] = 100
    else:
        stock = pd.DataFrame({
            '규격': ["0.15mm", "0.30mm", "무현상"],
            '현재고': [500, 500, 500],
            '안전재고': [100, 100, 50]
        })
    return orders, stock

def save_data(orders, stock):
    orders.to_csv(ORDER_FILE, index=False, encoding='utf-8-sig')
    stock.to_csv(STOCK_FILE, index=False, encoding='utf-8-sig')

# 2. 디자인
def apply_style():
    st.markdown("""<style>
    .stApp {background:#f8f9fa}
    [data-testid='stSidebar'] .stMarkdown h1 {background:#003366;color:white;padding:25px!important;border-radius:12px;font-size:22px}
    /* 탭 디자인 수정 */
    .stTabs [data-baseweb='tab'] {
        height:65px;
        padding:0 20px!important;
        background:white;
        border-radius:10px;
        margin-right:10px;
        border:1px solid #ddd;
    }
    .stTabs [aria-selected='true'] {background:#003366!important;color:white!important;font-weight:bold}
    .stMetric {background:white; padding:20px; border-radius:15px; border:1px solid #eee}
    .low-stock-alert {background-color:#ff4b4b; color:white; padding:15px; border-radius:10px; margin-bottom:15px; font-weight:bold; border-left:10px solid #8B0000}
    /* 숫자 뱃지 스타일 */
    .badge {background:#ff4b4b; color:white; padding:2px 7px; border-radius:10px; font-size:12px; margin-left:5px; font-weight:bold}
    </style>""", unsafe_allow_html=True)

# 3. 메인 로직
def main():
    st.set_page_config(page_title="Fullinkey Smart ERP", layout="wide")
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

    # --- 이슈 카운트 계산 ---
    wait_count = len(orders[orders['상태']=='대기'])      # 승인 대기 건수
    ship_count = len(orders[orders['상태']=='배송전'])   # 배송 준비 건수
    low_stock_items = stock[stock['현재고'] <= stock['안전재고']]
    low_stock_count = len(low_stock_items)              # 재고 부족 품목 수

    # 상단 재고 경고 알림 (전역 알림)
    if low_stock_count > 0:
        for _, item in low_stock_items.iterrows():
            st.markdown(f"<div class='low-stock-alert'>⚠️ [재고 부족 경고] {item['규격']} 판재가 안전 기준선 미달! (현재: {item['현재고']} / 기준: {item['안전재고']})</div>", unsafe_allow_html=True)

    # --- 탭 이름 정의 (이슈 건수 포함) ---
    t1_label = "📝 주문등록"
    t2_label = f"👑 승인관리 ({wait_count})" if wait_count > 0 else "👑 승인관리"
    t3_label = f"🚚 배송업무 ({ship_count})" if ship_count > 0 else "🚚 배송업무"
    t4_label = f"📦 재고현황 (!)" if low_stock_count > 0 else "📦 재고현황"
    t5_label = "📊 전체이력"
    t6_label = "📈 분석현황"
    t7_label = f"🚢 수입발주 ({low_stock_count})" if low_stock_count > 0 else "🚢 수입발주"

    t1, t2, t3, t4, t5, t6, t7 = st.tabs([t1_label, t2_label, t3_label, t4_label, t5_label, t6_label, t7_label])

    with t1:
        st.subheader("신규 주문 등록")
        name = st.selectbox("업체 선택", list(CLIENTS.keys()))
        sp = st.selectbox("판재 규격", stock['규격'].tolist())
        cur_s = stock[stock['규격']==sp]['현재고'].values[0]
        st.write(f"현재고: **{cur_s}** 박스")
        qt = st.number_input("주문 수량", min_value=1, max_value=int(cur_s) if cur_s > 0 else 1, value=min(10, int(cur_s)) if cur_s > 0 else 0)
        
        if st.button("주문 전송", type="primary", use_container_width=True):
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            new = {'일시':now_str, '업체':name, '규격':sp, '수량':qt, '상태':'대기', '담당':'-', '완료시간':'-'}
            orders = pd.concat([orders, pd.DataFrame([new])], ignore_index=True)
            stock.loc[stock['규격']==sp, '현재고'] -= qt
            save_data(orders, stock); st.success(f"주문 완료! ({now_str})"); st.rerun()
        
        st.divider()
        st.subheader("내가 등록한 대기 주문 (취소 가능)")
        my_wait = orders[orders['상태']=='대기']
        if len(my_wait) > 0:
            for i, r in my_wait.iterrows():
                with st.container(border=True):
                    c_a, c_b = st.columns([4, 1])
                    c_a.write(f"🕒 {r['일시']} | {r['업체']} | {r['규격']} {r['수량']}박스")
                    if c_b.button("취소", key=f"cnl_{i}"):
                        stock.loc[stock['규격']==r['규격'], '현재고'] += r['수량']
                        orders = orders.drop(i)
                        save_data(orders, stock); st.rerun()

    with t2:
        st.subheader(f"승인 대기 주문: {wait_count}건")
        wait = orders[orders['상태']=='대기']
        if len(wait) == 0: st.write("✅ 승인할 내역이 없습니다.")
        for i, r in wait.iterrows():
            with st.container(border=True):
                st.write(f"🕒 {r['일시']} | **{r['업체']}** | {r['규격']} {r['수량']}박스")
                if st.session_state.ur == "관리자":
                    if st.button(f"주문 승인", key=f"ap_{i}", use_container_width=True):
                        orders.at[i,'상태']='배송전'; save_data(orders, stock); st.rerun()

    with t3:
        st.subheader(f"배송/출고 관리: {ship_count}건")
        ready = orders[orders['상태']=='배송전']
        if len(ready) > 0:
            st.write("📦 **배송 대기 중**")
            for i, r in ready.iterrows():
                with st.container(border=True):
                    st.write(f"📍 {r['업체']} ({r['규격']} - {r['수량']}박스)")
                    if st.button("배송 출발", key=f"go_{i}", use_container_width=True):
                        orders.at[i,'상태']='중'; orders.at[i,'담당']=st.session_state.un
                        save_data(orders, stock); st.rerun()
        st.divider()
        ing = orders[orders['상태']=='중']
        if len(ing) > 0:
            st.write("🚚 **배송 진행 중**")
            for i, r in ing.iterrows():
                with st.container(border=True):
                    st.write(f"📍 **{r['업체']}** (담당: {r['담당']})")
                    if st.session_state.un == r['담당'] or st.session_state.ur == "관리자":
                        if st.button("배송 완료 처리", key=f"fi_{i}", type="primary", use_container_width=True):
                            orders.at[i,'상태']='완료'
                            orders.at[i,'완료시간']=datetime.now().strftime("%Y-%m-%d %H:%M")
                            save_data(orders, stock); st.rerun()

    with t4:
        st.subheader("실시간 재고 현황")
        cols = st.columns(len(stock))
        for i, row in stock.iterrows():
            status = "normal" if row['현재고'] > row['안전재고'] else "inverse"
            cols[i].metric(row['규격'], f"{row['현재고']} 박스", f"기준: {row['안전재고']}", delta_color=status)
        
        if st.session_state.ur == "관리자":
            st.divider()
            st.write("⚙️ **재고/안전재고 수치 조정**")
            sel_sp = st.selectbox("품목 선택", stock['규격'].tolist())
            c1, c2 = st.columns(2)
            n_stk = c1.number_input("현재고 수정", value=int(stock[stock['규격']==sel_sp]['현재고'].values[0]))
            n_min = c2.number_input("안전재고 수정", value=int(stock[stock['규격']==sel_sp]['안전재고'].values[0]))
            if st.button("설정 저장", use_container_width=True):
                stock.loc[stock['규격']==sel_sp, '현재고'] = n_stk
                stock.loc[stock['규격']==sel_sp, '안전재고'] = n_min
                save_data(orders, stock); st.rerun()

    with t5:
        st.subheader("전체 주문 및 배송 이력")
        st.dataframe(orders.iloc[::-1], use_container_width=True)

    with t6:
        st.subheader("업체별 주문 통계")
        if len(orders) > 0:
            chart_data = orders.groupby('업체')['수량'].sum().reset_index()
            st.bar_chart(data=chart_data, x='업체', y='수량', color="#003366", horizontal=True, x_label="", y_label="")

    with t7:
        st.subheader("🚢 해외 수입 발주 시스템")
        if low_stock_count > 0:
            for _, item in low_stock_items.iterrows():
                with st.container(border=True):
                    st.write(f"**품목:** {item['규격']} CTP Plate")
                    p_qty = st.number_input(f"{item['규격']} 발주 수량", min_value=1, value=500, key=f"p_{item['규격']}")
                    if st.button(f"{item['규격']} 발주서 생성", key=f"b_{item['규격']}"):
                        st.code(f"TO: Supplier\nITEM: {item['규격']}\nQTY: {p_qty}\nDATE: {datetime.now().strftime('%Y-%m-%d')}")
        else: st.success("현재 모든 규격의 재고가 충분합니다.")

if __name__ == "__main__":
    main()
