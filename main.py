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
    st.markdown("업로드된 CSV 파일(`world_population.csv`)을 분석하여 연도별 변화를 시각화합니다.")

    # [1] 데이터 로드
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'world_population.csv')

    try:
        df = pd.read_csv(file_path)
        
        # 컬럼명 앞뒤 공백 제거
        df.columns = df.columns.str.strip()
        
        # 파일 구조 확인 (업로드된 파일 형식인지 체크)
        if 'CCA3' not in df.columns or '2022 Population' not in df.columns:
            st.error("CSV 파일 형식이 예상과 다릅니다. 'CCA3' 및 'YYYY Population' 컬럼이 필요합니다.")
            st.write(f"현재 데이터 컬럼: {list(df.columns)}")
            return

    except FileNotFoundError:
        st.error(f"❌ 파일을 찾을 수 없습니다.\n경로: {file_path}")
        return
    except Exception as e:
        st.error(f"❌ 데이터 로드 오류: {e}")
        return

    # [2] 데이터 전처리 (Wide -> Long 변환)
    # 업로드된 파일은 연도가 컬럼으로 되어 있으므로, 이를 행(Row)으로 변환해야 그래프를 그리기 좋습니다.
    
    # 1. 연도별 인구 컬럼만 찾기 (예: "2022 Population")
    year_columns = [col for col in df.columns if 'Population' in col and col[0].isdigit()]
    
    # 2. pd.melt를 사용하여 재구조화 (Unpivot)
    # id_vars: 고정할 컬럼 (국가명, 국가코드, 대륙)
    df_melted = df.melt(
        id_vars=['Country/Territory', 'CCA3', 'Continent'], 
        value_vars=year_columns,
        var_name='Year_Column', 
        value_name='Population'
    )
    
    # 3. '2022 Population' 문자열에서 '2022' 숫자만 추출하여 'Year' 컬럼 생성
    df_melted['Year'] = df_melted['Year_Column'].str.split().str[0].astype(int)

    # [3] 사용자 입력 (연도 선택)
    available_years = sorted(df_melted['Year'].unique(), reverse=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_year = st.selectbox("분석할 연도를 선택하세요:", available_years)

    # [4] 선택된 연도 데이터 필터링
    filtered_df = df_melted[df_melted['Year'] == selected_year].copy()

    st.subheader(f"📅 {selected_year}년 세계 인구 현황")

    # [5] 인구 구간(Bin) 설정 로직
    def categorize_population(pop):
        if pop < 10_000_000: return '< 1천만'
        elif pop < 50_000_000: return '1천만 - 5천만'
        elif pop < 100_000_000: return '5천만 - 1억'
        elif pop < 500_000_000: return '1억 - 5억'
        else: return '> 5억'

    filtered_df['Population_Bracket'] = filtered_df['Population'].apply(categorize_population)

    # 범례 순서 정렬
    bracket_order = ['< 1천만', '1천만 - 5천만', '5천만 - 1억', '1억 - 5억', '> 5억']
    filtered_df['Population_Bracket'] = pd.Categorical(
        filtered_df['Population_Bracket'], categories=bracket_order, ordered=True
    )

    # [6] 지도 시각화 (Plotly Express)
    color_map = {
        '< 1천만': '#ffffd4',      # 연한 노랑
        '1천만 - 5천만': '#fed98e', # 연한 주황
        '5천만 - 1억': '#fe9929',   # 중간 주황
        '1억 - 5억': '#d95f0e',     # 진한 주황
        '> 5억': '#993404'        # 갈색/진한 빨강
    }

    fig = px.choropleth(
        filtered_df,
        locations="CCA3",              # 업로드된 파일의 국가 코드 컬럼명
        color="Population_Bracket",
        hover_name="Country/Territory", # 업로드된 파일의 국가명 컬럼명
        hover_data={"Population": ":,"},
        color_discrete_map=color_map,
        category_orders={"Population_Bracket": bracket_order},
        projection="natural earth",
        title=f"{selected_year}년 국가별 인구 규모"
    )
    
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=600)
    st.plotly_chart(fig, use_container_width=True)

    #
