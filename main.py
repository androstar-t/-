import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="세계 인구 분석 앱",
    page_icon="🌏",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. 데이터 로드 및 전처리
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_process_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'world_population.csv')

    if not os.path.exists(file_path):
        return None, f"파일을 찾을 수 없습니다: {file_path}"

    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        
        # 연도 컬럼 찾기 (YYYY Population)
        year_cols = [c for c in df.columns if 'Population' in c and c[0].isdigit()]
        if not year_cols:
            return None, "인구 데이터 컬럼을 찾을 수 없습니다."

        # Wide -> Long 변환
        id_vars = ['CCA3', 'Country/Territory', 'Continent']
        existing_ids = [c for c in id_vars if c in df.columns]
        
        df_melted = df.melt(
            id_vars=existing_ids, 
            value_vars=year_cols,
            var_name='Year_Column', 
            value_name='Population'
        )
        
        # 연도 정수 변환
        df_melted['Year'] = df_melted['Year_Column'].str.extract(r'(\d{4})').astype(int)
        
        return df_melted, None

    except Exception as e:
        return None, str(e)

# -----------------------------------------------------------------------------
# 3. 메인 앱 로직
# -----------------------------------------------------------------------------
def main():
    st.sidebar.title("메뉴")
    menu = st.sidebar.radio("이동할 페이지:", ["홈", "연도별 인구 증감 분석"])

    # === [홈] ===
    if menu == "홈":
        st.title("🏠 세계 인구 데이터 분석")
        st.markdown("""
        ### 인구 변화 시각화 도구
        왼쪽 메뉴에서 **'연도별 인구 증감 분석'**을 선택하세요.
        
        * 🔵 **파란색**: 인구가 **증가**한 국가
        * 🔴 **빨간색**: 인구가 **감소**한 국가
        * 색이 진할수록 변화폭이 큰 것을 의미합니다.
        """)
        st.info("👈 사이드바에서 메뉴를 선택해주세요.")

    # === [분석 페이지] ===
    elif menu == "연도별 인구 증감 분석":
        st.header("🌍 연도별 인구 증가율/감소율 지도")
        
        df, error_msg = load_and_process_data()
        if error_msg:
            st.error(error_msg)
            return

        # 1. 연도 선택
        year_list = sorted(df['Year'].unique(), reverse=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            # 가장 과거 데이터(1970)는 비교 대상이 없으므로 제외할 수도 있으나, 리스트에는 포함
            selected_year = st.selectbox("기준 연도를 선택하세요:", year_list)

        # 2. 비교 대상 연도 찾기 (선택한 연도보다 바로 앞선 과거 연도)
        # 예: 리스트가 [2022, 2020, 2015...] 일 때 2022 선택 시 2020과 비교
        try:
            current_idx = year_list.index(selected_year)
            if current_idx + 1 < len(year_list):
                prev_year = year_list[current_idx + 1]
            else:
                prev_year = None # 더 이상 과거 데이터가 없음
        except ValueError:
            prev_year = None

        if prev_year is None:
            st.warning(f"{selected_year}년은 가장 오래된 데이터이므로 이전 연도와 비교할 수 없습니다.")
            # 단순히 인구수만 보여주거나 빈 지도 표시
            return

        st.markdown(f"**{prev_year}년 대비 {selected_year}년의 인구 변화율**을 보여줍니다.")

        # 3. 데이터 계산 (증가율)
        # 현재 연도 데이터
        df_curr = df[df['Year'] == selected_year][['CCA3', 'Country/Territory', 'Population']].set_index('CCA3')
        # 과거 연도 데이터
        df_prev = df[df['Year'] == prev_year][['CCA3', 'Population']].set_index('CCA3')
        
        # 데이터 병합 및 계산
        # Growth Rate = (Current - Prev) / Prev * 100
        merged_df = df_curr.join(df_prev, lsuffix='_curr', rsuffix='_prev')
        merged_df['Growth_Rate'] = ((merged_df['Population_curr'] - merged_df['Population_prev']) / merged_df['Population_prev']) * 100
        merged_df = merged_df.reset_index() # CCA3를 다시 컬럼으로

        # 4. 지도 시각화 설정
        # 색상 범위 설정: 너무 극단적인 값(전쟁 등) 때문에 색이 묻히는 것을 방지하기 위해 범위를 제한(-2% ~ +2% 정도가 적당)
        # 하지만 여기서는 데이터 기반으로 자동 조정하되, 0을 중심으로 맞춥니다.
        
        fig = px.choropleth(
            merged_df,
            locations="CCA3",
            color="Growth_Rate",
            hover_name="Country/Territory",
            hover_data={
                "Growth_Rate": ":.2f",      # 소수점 2자리 표시
                "Population_curr": ":,",    # 현재 인구
                "Population_prev": ":,"     # 과거 인구
            },
            # RdBu 색상 스케일: Red(음수/감소) <-> White(0) <-> Blue(양수/증가)
            color_continuous_scale="RdBu",
            
            # 0을 기준으로 색상을 나눔 (이게 핵심!)
            color_continuous_midpoint=0,
            
            # 색상 진하기 범위 강제 지정 (예: -2% ~ 2% 사이에서 색 변화 최대화)
            # 이 범위를 벗어나면 가장 진한 색으로 표시됨. 시각적 구분이 잘 됨.
            range_color=[-2.5, 2.5], 
            
            projection="natural earth",
            title=f"{prev_year}년 ➡ {selected_year}년 인구 증감률 (%)",
            labels={'Growth_Rate': '증가율(%)', 'Population_curr': f'{selected_year} 인구'}
        )
        
        fig.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        # 5. 상세 데이터 표
        with st.expander("📊 국가별 증감률 데이터 보기"):
            st.dataframe(
                merged_df[['Country/Territory', 'Population_prev', 'Population_curr', 'Growth_Rate']]
                .sort_values(by='Growth_Rate', ascending=False)
                .style.format({
                    'Population_prev': '{:,}',
                    'Population_curr': '{:,}',
                    'Growth_Rate': '{:+.2f}%' # 부호 표시 (+, -)
                })
            )

if __name__ == "__main__":
    main()
