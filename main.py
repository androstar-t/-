import streamlit as st
import pandas as pd
import plotly.express as px
import os # 경로 설정을 위해 추가

# 페이지 기본 설정
st.set_page_config(
    page_title="데이터 분석 앱",
    page_icon="📊",
    layout="wide"
)

# ==============================================
# 함수 정의: 연도별 세계인구 분석 기능
# ==============================================
def run_world_population_analysis():
    st.header("🌍 연도별 세계 인구 분석")
    st.markdown("루트 폴더의 CSV 파일을 기반으로 연도별 세계 인구 분포를 지도에 시각화합니다.")

    # 1. 데이터 로드 (경로 설정 강화)
    # 현재 실행 중인 파일(main.py)이 있는 폴더 경로를 찾습니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 루트 폴더에 있는 파일 경로를 생성합니다.
    file_path = os.path.join(current_dir, 'world_population.csv')

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다. 루트 폴더에 'world_population.csv' 파일이 있는지 확인해주세요.\n\n경로: {file_path}")
        return
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return

    # 2. 연도 선택 드랍박스 만들기
    available_years = sorted(df['year'].unique(), reverse=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_year = st.selectbox("분석할 연도를 선택하세요:", available_years)

    # 3. 선택한 연도로 데이터 필터링
    filtered_df = df[df['year'] == selected_year].copy()

    st.subheader(f"📅 {selected_year}년 세계 인구 현황")

    # ==============================================================================
    # 핵심 기능: 인구수 구간 설정 및 색상 매핑 로직
    # ==============================================================================
    
    def categorize_population(pop):
        if pop < 10_000_000: return '< 1천만'
        elif pop < 50_000_000: return '1천만 - 5천만'
        elif pop < 100_000_000: return '5천만 - 1억'
        elif pop < 500_000_000: return '1억 - 5억'
        else: return '> 5억'

    # 데이터프레임에 구간 컬럼 추가
    filtered_df['Population_Bracket'] = filtered_df['population'].apply(categorize_population)

    # 범례 순서 지정
    bracket_order = ['< 1천만', '1천만 - 5천만', '5천만 - 1억', '1억 - 5억', '> 5억']
    filtered_df['Population_Bracket'] = pd.Categorical(
        filtered_df['Population_Bracket'], categories=bracket_order, ordered=True
    )

    # ==============================================================================
    # 세계지도 시각화 (Plotly Express)
    # ==============================================================================
    # 구간별 색상 정의
    color_discrete_map = {
        '< 1천만': '#ffffd4',      # 연한 노랑
        '1천만 - 5천만': '#fed98e', # 연한 주황
        '5천만 - 1억': '#fe9929',   # 중간 주황
        '1억 - 5억': '#d95f0e',     # 진한 주황
        '> 5억': '#993404'        # 갈색/진한 빨강
    }

    fig = px.choropleth(
        filtered_df,
        locations="iso_alpha",
        color="Population_Bracket",
        hover_name="country",
        hover_data={"population": ":,"},
        color_discrete_map=color_discrete_map,
        category_orders={"Population_Bracket": bracket_order},
        projection="natural earth",
        title=f"{selected_year}년 국가별 인구 규모 (구간별 색상 구분)"
    )

    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=600)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"{selected_year}년 데이터 상세 보기"):
        st.dataframe(filtered_df[['country', 'year', 'population', 'Population_Bracket']].sort_values(by='population', ascending=False))


# ==============================================
# 메인 앱 구조 (사이드바)
# ==============================================
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
