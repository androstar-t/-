import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 (무조건 맨 처음에 실행되어야 함)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="세계 인구 분석 앱",
    page_icon="🌏",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리 함수
# -----------------------------------------------------------------------------
@st.cache_data  # 데이터를 매번 다시 읽지 않도록 캐싱(속도 향상)
def load_and_process_data():
    # 현재 파일(main.py)이 있는 위치를 기준으로 CSV 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'world_population.csv')

    if not os.path.exists(file_path):
        return None, f"파일을 찾을 수 없습니다: {file_path}"

    try:
        df = pd.read_csv(file_path)
        # 컬럼명 앞뒤 공백 제거
        df.columns = df.columns.str.strip()
        
        # [데이터 구조 변경] Wide Format -> Long Format
        # "2022 Population", "2020 Population" 등의 컬럼을 찾습니다.
        year_cols = [c for c in df.columns if 'Population' in c and c[0].isdigit()]
        
        if not year_cols:
            return None, "인구 데이터 컬럼(예: 2022 Population)을 찾을 수 없습니다."

        # 데이터 재구조화 (Melt)
        # 고정할 컬럼: 국가코드(CCA3), 국가명(Country/Territory), 대륙(Continent)
        id_vars = ['CCA3', 'Country/Territory', 'Continent']
        # 만약 CSV에 이 컬럼들이 없으면 에러 방지를 위해 있는 것만 사용
        existing_ids = [c for c in id_vars if c in df.columns]
        
        df_melted = df.melt(
            id_vars=existing_ids, 
            value_vars=year_cols,
            var_name='Year_Column', 
            value_name='Population'
        )
        
        # "2022 Population" -> 2022 (정수형 연도 추출)
        df_melted['Year'] = df_melted['Year_Column'].str.extract(r'(\d{4})').astype(int)
        
        return df_melted, None

    except Exception as e:
        return None, str(e)

# -----------------------------------------------------------------------------
# 3. 화면 UI 구성
# -----------------------------------------------------------------------------
def main():
    # 사이드바 메뉴
    st.sidebar.title("메뉴")
    menu = st.sidebar.radio("이동할 페이지:", ["홈", "연도별 세계인구 분석"])

    # === [홈 페이지] ===
    if menu == "홈":
        st.title("🏠 세계 인구 데이터 분석 홈")
        st.markdown("""
        ### 환영합니다! 👋
        이 앱은 **세계 인구 데이터**를 시각적으로 분석하는 도구입니다.
        
        왼쪽 사이드바에서 **'연도별 세계인구 분석'**을 선택하면 
        지도를 통해 인구 분포를 확인할 수 있습니다.
        """)
        st.info("👈 왼쪽 메뉴를 클릭해보세요.")

    # === [분석 페이지] ===
    elif menu == "연도별 세계인구 분석":
        st.header("🌍 연도별 세계 인구 지도")
        
        # 데이터 로드 시도
        with st.spinner("데이터를 불러오는 중입니다..."):
            df, error_msg = load_and_process_data()
        
        # 에러 발생 시 처리
        if error_msg:
            st.error(f"❌ 오류 발생: {error_msg}")
            st.warning("프로젝트 폴더(루트)에 'world_population.csv' 파일이 있는지 확인해주세요.")
            return

        # 정상 로드 시 UI 표시
        # 1. 연도 선택
        year_list = sorted(df['Year'].unique(), reverse=True)
        selected_year = st.selectbox("📅 분석할 연도를 선택하세요", year_list)

        # 2. 데이터 필터링
        filtered_df = df[df['Year'] == selected_year].copy()

        # 3. 인구 구간 설정 (색상 구분용)
        def get_bracket(pop):
            if pop < 1_000_000: return '< 100만'
            elif pop < 10_000_000: return '100만 - 1천만'
            elif pop < 50_000_000: return '1천만 - 5천만'
            elif pop < 100_000_000: return '5천만 - 1억'
            elif pop < 500_000_000: return '1억 - 5억'
            else: return '> 5억'

        filtered_df['Range'] = filtered_df['Population'].apply(get_bracket)
        
        # 범례 순서 정렬
        bracket_order = ['< 100만', '100만 - 1천만', '1천만 - 5천만', '5천만 - 1억', '1억 - 5억', '> 5억']
        
        # 4. 지도 그리기
        color_map = {
            '< 100만': '#f7fcf5',
            '100만 - 1천만': '#e5f5e0',
            '1천만 - 5천만': '#a1d99b',
            '5천만 - 1억': '#41ab5d',
            '1억 - 5억': '#238b45',
            '> 5억': '#005a32'
        }

        fig = px.choropleth(
            filtered_df,
            locations="CCA3",            # 국가 코드
            color="Range",               # 색상 기준
            hover_name="Country/Territory",
            hover_data={"Population": ":,"},
            color_discrete_map=color_map,
            category_orders={"Range": bracket_order},
            projection="natural earth",
            title=f"{selected_year}년 인구 분포"
        )
        
        fig.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

        # 5. 데이터 표 확인
        with st.expander("📊 데이터 상세 보기"):
            st.dataframe(
                filtered_df[['Country/Territory', 'CCA3', 'Population', 'Range']]
                .sort_values(by='Population', ascending=False)
            )

# 앱 실행 진입점
if __name__ == "__main__":
    main()
