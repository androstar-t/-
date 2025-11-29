import streamlit as st
import math
import numpy as np # 근 찾기를 위해 numpy 추가

# 페이지 설정
st.set_page_config(page_title="수학 & 정적분 계산기", page_icon="∫")

st.title("🧮 수학 & 정적분 계산기")
st.markdown("이차함수의 계수와 적분 범위를 **정수**로 입력하여 계산합니다.")
st.divider()

# 메인 메뉴 (연산 종류 선택)
operation = st.selectbox(
    "원하는 기능을 선택하세요",
    [
        "기본 연산 (사칙연산/지수/로그)",
        "이차함수 정적분 (Definite Integral)"
    ]
)

# ---------------------------------------------------------
# 1. 이차함수 정적분 모드 (절댓값 기능 추가)
# ---------------------------------------------------------
if operation == "이차함수 정적분 (Definite Integral)":
    
    st.subheader("∫ 이차함수 정적분 계산")
    st.markdown(r"함수식: $f(x) = ax^2 + bx + c$")
    st.info("💡 계수와 적분 범위는 정수만 입력 가능합니다.")
    
    # 입력 1: 이차함수 계수
    st.markdown("**1. 계수 입력 (정수)**")
    col1, col2, col3 = st.columns(3)
    with col1:
        a = st.number_input("a (x²의 계수)", value=1, step=1)
    with col2:
        b = st.number_input("b (x의 계수)", value=0, step=1)
    with col3:
        c = st.number_input("c (상수항)", value=0, step=1)
        
    # 입력 2: 적분 범위 및 옵션
    st.markdown("**2. 적분 범위 및 옵션**")
    range_col1, range_col2 = st.columns(2)
    with range_col1:
        x_start = st.number_input("적분 시작점 (x₁)", value=0, step=1)
    with range_col2:
        x_end = st.number_input("적분 끝점 (x₂)", value=5, step=1)
    
    # [새로운 기능] 절댓값 체크박스
    use_abs = st.checkbox("절댓값 포함 계산 (|f(x)|)", value=False, help="체크하면 그래프와 x축 사이의 '넓이'를 계산합니다.")

    # 계산 버튼
    if st.button("적분 계산하기", type="primary"):
        
        # 부정적분 함수 정의 F(x)
        def integral_func(x, a_val, b_val, c_val):
            return (a_val / 3.0) * (x ** 3) + (b_val / 2.0) * (x ** 2) + (c_val * x)

        poly_str_base = f"{a}x^2 + {b}x + {c}".replace("+-", "- ").replace("+ -", "- ")
        final_result = 0
        equation_display = ""
        steps_log = []

        if use_abs:
            # === 절댓값 계산 로직 ===
            st.write("🔍 절댓값 계산을 위해 구간을 나눕니다.")
            
            # 1. 근 찾기 (f(x)=0 이 되는 x값)
            # a가 0인 경우(일차함수) numpy 오류 방지 처리
            if abs(a) < 1e-9: 
                roots = [-c/b] if abs(b) > 1e-9 else []
            else:
                roots = np.roots([a, b, c])
            
            # 2. 적분 범위 내에 있는 실근만 필터링
            valid_roots = []
            for r in roots:
                if np.isreal(r): # 실근인지 확인
                    r_real = np.real(r)
                    # 시작점과 끝점 사이에 있는 근만 선택 (경계값 제외)
                    if min(x_start, x_end) < r_real < max(x_start, x_end):
                        valid_roots.append(r_real)
            valid_roots.sort()

            # 3. 적분 구간 나누기 points = [시작, 근1, 근2, ..., 끝]
            points = [x_start] + valid_roots + [x_end]
            # x_start가 x_end보다 클 경우를 대비해 정렬
            points.sort() 
            
            # 4. 각 구간별 정적분 후 절댓값 합산
            total_area = 0
            steps_log.append("구간별 계산 내역:")
            for i in range(len(points) - 1):
                p_start, p_end = points[i], points[i+1]
                # 해당 구간의 일반 정적분 값 계산
                segment_integral = integral_func(p_end, a, b, c) - integral_func(p_start, a, b, c)
                # 그 값의 절댓값을 총합에 더함
                total_area += abs(segment_integral)
                steps_log.append(f"- 구간 [{p_start:.2f}, {p_end:.2f}] 정적분: {segment_integral:.4f} → 넓이(절댓값): {abs(segment_integral):.4f}")

            final_result = total_area
            # 절댓값 기호(| |) 추가
            equation_display = f"\\int_{{{x_start}}}^{{{x_end}}} |{poly_str_base}| \\,dx"

        else:
            # === 기본 정적분 계산 로직 (기존과 동일) ===
            result_end = integral_func(x_end, a, b, c)
            result_start = integral_func(x_start, a, b, c)
            final_result = result_end - result_start
            equation_display = f"\\int_{{{x_start}}}^{{{x_end}}} ({poly_str_base}) \\,dx"
            steps_log.append(f"F({x_end}) = {result_end:.4f}")
            steps_log.append(f"F({x_start}) = {result_start:.4f}")
            steps_log.append(f"최종 계산: {result_end:.4f} - {result_start:.4f}")

        # === 결과 출력 (공통) ===
        st.success("계산 완료!")
        st.markdown(f"""
        ### 결과
        $$
        {equation_display} = {final_result:.4f}
        $$
        """)
        
        with st.expander("계산 과정 상세 보기"):
            if use_abs:
                st.write(f"**필요한 근 (범위 내 x절편):** {[round(r, 2) for r in valid_roots]}")
                st.write(f"**나뉜 구간:** {[round(p, 2) for p in points]}")
                for log in steps_log:
                    st.write(log)
                st.info("절댓값 적분은 그래프가 x축과 만나는 점을 기준으로 구간을 나누어, 각 구간 정적분 값의 절댓값을 합산합니다.")
            else:
                st.write("부정적분 함수 $F(x) = \\frac{a}{3}x^3 + \\frac{b}{2}x^2 + cx$")
                for log in steps_log:
                    st.write(log)

# ---------------------------------------------------------
# 2. 기본 연산 모드 (기존 유지)
# ---------------------------------------------------------
else:
    st.subheader("🧮 사칙연산 및 공학용 계산")
    # (이전 코드와 동일하여 생략 없이 전체 포함)
    sub_calc_type = st.selectbox(
        "연산 종류",
        ["덧셈", "뺄셈", "곱셈", "나눗셈", "나머지", "거듭제곱", "로그"]
    )
    
    c1, c2 = st.columns(2)
    with c1:
        num1 = st.number_input("첫 번째 숫자 (a)", value=0.0, format="%.2f")
    with c2:
        label_num2 = "두 번째 숫자 (b)"
        if "로그" in sub_calc_type:
            label_num2 = "밑 (Base)"
        num2 = st.number_input(label_num2, value=0.0, format="%.2f")
        
    if st.button("계산하기", type="primary"):
        res = 0
        eq = ""
        try:
            if sub_calc_type == "덧셈": res = num1 + num2; eq = f"{num1} + {num2}"
            elif sub_calc_type == "뺄셈": res = num1 - num2; eq = f"{num1} - {num2}"
            elif sub_calc_type == "곱셈": res = num1 * num2; eq = f"{num1} \\times {num2}"
            elif sub_calc_type == "나눗셈":
                if num2==0: st.error("0으로 나눌 수 없음"); st.stop()
                res = num1 / num2; eq = f"{num1} \\div {num2}"
            elif sub_calc_type == "나머지":
                if num2==0: st.error("0으로 나눌 수 없음"); st.stop()
                res = num1 % num2; eq = f"{num1} \\pmod {{{num2}}}"
            elif sub_calc_type == "거듭제곱": res = math.pow(num1, num2); eq = f"{num1}^{{{num2}}}"
            elif sub_calc_type == "로그":
                if num1<=0 or num2<=0 or num2==1: st.error("로그 범위 오류"); st.stop()
                res = math.log(num1, num2); eq = f"\\log_{{{num2}}}({num1})"
                
            st.success(f"결과: {res:.4f}")
            st.latex(f"{eq} = {res:.4f}")
        except Exception as e:
            st.error(f"오류: {e}")
