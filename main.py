import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="데이터 분석 앱",
    page_icon="📊",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. 기능 함수 정의: 연도별 세계인구 분석
# -----------------------------------------------------------------------------
def run_world_population_analysis():
    st.header("🌍 연도별 세계 인구 분석")
    st.markdown("루트 폴더의 CSV 파일을 기반으로 연도별 세계 인구 분포를 지도에 시각화합니다.")

    # [1] 데이터 로드 (경로 및 컬럼 에러 방지 처리)
    # 현재 파일(main.py)이 있는 위치를 기준으로 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'world_population.csv')

    try:
        df = pd.read_csv(file_path)
        
        # ★ 중요: CSV 컬럼명 앞뒤 공백 제거 (에러 방지)
        df.columns = df.columns.str.strip()
        
        # 필수 컬럼 확인
        required_cols = ["iso_alpha", "year", "population", "country"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"❌ CSV 파일에 필수 컬럼이 없습니다: {missing}")
            st.write(f"현재 인식된 컬럼: {list(df.columns)}")
            return

    except FileNotFoundError:
        st.error(f"❌ 파일을 찾을 수 없습니다.\n경로: {file_path}")
        st.info("프로젝트 루트 폴더에 'world_population.csv' 파일을 넣어주세요.")
        return
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {e}")
        return

    # [2] 사용자 입력 (연도 선택)
    available_years = sorted(df['year'].unique(), reverse=True)
    
    col_input, col_space = st.columns([1, 3])
    with col_input:
        selected_year = st.selectbox("분석할 연도를 선택하세요:", available_years)

    # [3] 데이터 필터링
    filtered_df = df[df['year'] == selected_year].copy()
    
    if filtered_df.empty:
        st.warning("해당 연도의 데이터가 없습니다.")
        return

    st.subheader(f"📅 {selected_year}년 세계 인구 현황")

    # [4] 인구 구간(Bin) 설정 로직
    def categorize_population(pop):
        if pop < 10_000_000: return '< 1천만'
        elif pop < 50_000_000: return '1천만 - 5천만'
        elif pop < 100_000_000: return '5천만 - 1억'
        elif pop < 500_000_000: return '1억 - 5억'
        else: return '> 5억'

    filtered_df['Population_Bracket'] = filtered_df['population'].apply(categorize_population)

    # 범례 순서 정렬을 위한 카테고리화
    bracket_order = ['< 1천만', '1천만 - 5천만', '5천만 - 1억', '1억 - 5억', '> 5억']
    filtered_df['Population_Bracket'] = pd.Categorical(
        filtered_df['Population_Bracket'], categories=bracket_order, ordered=True
    )

    # [5] 지도 시각화 (Plotly Express)
    # 구간별 색상 지정
    color_map = {
        '< 1천만': '#ffffd4',      # 연한 노랑
        '1천만 - 5천만': '#fed98e', # 연한 주황
        '5천만 - 1억': '#fe9929',   # 중간 주황
        '1억 - 5억': '#d95f0e',     # 진한 주황
        '> 5억': '#993404'        # 갈색/진한 빨강
    }

    try:
        fig = px.choropleth(
            filtered_df,
            locations="iso_alpha",         # 국가 코드 (ISO 3자리)
            color="Population_Bracket",    # 색상 기준 (인구 구간)
            hover_name="country",          # 마우스 오버 시 국가명
            hover_data={"population": ":,"}, # 마우스 오버 시 인구수 (콤마 포맷)
            color_discrete_map=color_map,  # 커스텀 색상 적용
            category_orders={"Population_Bracket": bracket_order}, # 범례 순서
            projection="natural earth",    # 지도 투영법
            title=f"{selected_year}년 국가별 인구 규모"
        )
        
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"지도를 그리는 중 오류가 발생했습니다: {e}")
        st.write("CSV 파일의 'iso_alpha' 컬럼 데이터가 올바른 국가 코드인지 확인해주세요.")

    # [6] 데이터 표 보기
    with st.expander(f"{selected_year}년 데이터 상세 보기"):
        st.dataframe(
            filtered_df[['country', 'iso_alpha', 'population', 'Population_Bracket']]
            .sort_values(by='population', ascending=False)
        )


# -----------------------------------------------------------------------------
# 3. 메인 앱 구조 (사이드바 네비게이션)
# -----------------------------------------------------------------------------
st.sidebar.title("메뉴")
app_mode = st.sidebar.radio(
    "이동할 페이지를 선택하세요:",
    ["홈", "연도별 세계인구 분석"]
)

if app_mode == "홈":
    st.title("🏠 홈 페이지")
    st.write("왼쪽 사이드바에서 원하는 분석 기능을 선택해주세요.")
    st.info("👈 '연도별 세계인구 분석' 메뉴를 선택하면 지도를 볼 수 있습니다.")

elif app_mode == "연도별 세계인구 분석":
    run_world_population_analysis()
