# ==============================================
# 함수 정의: 연도별 세계인구 분석 기능 (수정됨)
# ==============================================
def run_world_population_analysis():
    st.header("🌍 연도별 세계 인구 분석")
    st.markdown("루트 폴더의 CSV 파일을 기반으로 연도별 세계 인구 분포를 지도에 시각화합니다.")

    # 1. 데이터 로드
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'world_population.csv')

    try:
        # 데이터 읽기
        df = pd.read_csv(file_path)
        
        # [중요 오류 수정] 컬럼 이름의 앞뒤 공백 제거 (예: " iso_alpha" -> "iso_alpha")
        df.columns = df.columns.str.strip()
        
        # 필수 컬럼 확인
        required_cols = ["iso_alpha", "year", "population", "country"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"CSV 파일에 다음 컬럼이 없습니다: {missing_cols}")
            st.write(f"현재 인식된 컬럼명: {list(df.columns)}")
            return

    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다. 루트 폴더에 'world_population.csv'가 있는지 확인하세요.\n경로: {file_path}")
        return
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return

    # 2. 연도 선택
    available_years = sorted(df['year'].unique(), reverse=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_year = st.selectbox("분석할 연도를 선택하세요:", available_years)

    # 3. 데이터 필터링
    filtered_df = df[df['year'] == selected_year].copy()
    
    if filtered_df.empty:
        st.warning(f"{selected_year}년도에 해당하는 데이터가 없습니다.")
        return

    st.subheader(f"📅 {selected_year}년 세계 인구 현황")

    # 인구 구간 설정 함수
    def categorize_population(pop):
        if pop < 10_000_000: return '< 1천만'
        elif pop < 50_000_000: return '1천만 - 5천만'
        elif pop < 100_000_000: return '5천만 - 1억'
        elif pop < 500_000_000: return '1억 - 5억'
        else: return '> 5억'

    filtered_df['Population_Bracket'] = filtered_df['population'].apply(categorize_population)

    # 범례 순서
    bracket_order = ['< 1천만', '1천만 - 5천만', '5천만 - 1억', '1억 - 5억', '> 5억']
    filtered_df['Population_Bracket'] = pd.Categorical(
        filtered_df['Population_Bracket'], categories=bracket_order, ordered=True
    )

    # 색상 맵
    color_discrete_map = {
        '< 1천만': '#ffffd4',
        '1천만 - 5천만': '#fed98e',
        '5천만 - 1억': '#fe9929',
        '1억 - 5억': '#d95f0e',
        '> 5억': '#993404'
    }

    # 지도 그리기 (여기가 113번 라인 부근)
    try:
        fig = px.choropleth(
            filtered_df,
            locations="iso_alpha",         # CSV에 이 이름의 컬럼이 꼭 있어야 함
            color="Population_Bracket",
            hover_name="country",
            hover_data={"population": ":,"},
            color_discrete_map=color_discrete_map,
            category_orders={"Population_Bracket": bracket_order},
            projection="natural earth",
            title=f"{selected_year}년 국가별 인구 규모"
        )
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"지도 생성 중 오류 발생: {e}")
        st.write("CSV 파일의 'iso_alpha' 컬럼 데이터가 올바른지 확인해주세요.")

    with st.expander("데이터 상세 보기"):
        st.dataframe(filtered_df)
