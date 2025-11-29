import streamlit as st
import math

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
# 1. 이차함수 정적분 모드 (입력값 정수 변경)
# ---------------------------------------------------------
if operation == "이차함수 정적분 (Definite Integral)":
    
    

[Image of geometric interpretation of definite integral area under curve]


    st.subheader("∫ 이차함수 정적분 계산")
    st.markdown(r"함수식: $f(x) = ax^2 + bx + c$")
    st.info("💡 계수와 적분 범위는 정수만 입력 가능합니다.")
    
    # 입력 1: 이차함수 계수 (a, b, c) -> 정수 입력(value=1, step=1)
    st.markdown("**1. 계수 입력 (정수)**")
    col1, col2, col3 = st.columns(3)
    with col1:
        a = st.number_input("a (x²의 계수)", value=1, step=1)
    with col2:
        b = st.number_input("b (x의 계수)", value=0, step=1)
    with col3:
        c = st.number_input("c (상수항)", value=0, step=1)
        
    # 입력 2: 적분 범위 (시작, 끝) -> 정수 입력
    st.markdown("**2. 적분 범위 입력 (정수)**")
    range_col1, range_col2 = st.columns(2)
    with range_col1:
        x_start = st.number_input("적분 시작점 (x₁)", value=0, step=1)
    with range_col2:
        x_end = st.number_input("적분 끝점 (x₂)", value=5, step=1)

    # 계산 버튼
    if st.button("적분 계산하기", type="primary"):
        # 적분 함수 정의
        def integral_func(x, a, b, c):
            return (a / 3) * (x ** 3) + (b / 2) * (x ** 2) + (c * x)

        # 정적분 계산: F(end) - F(start)
        result_end = integral_func(x_end, a, b, c)
        result_start = integral_func(x_start, a, b, c)
        final_result = result_end - result_start
        
        # 수식 문자열 생성
        poly_str = f"{a}x^2 + {b}x + {c}".replace("+-", "- ").replace("+ -", "- ")
        
        st.success("계산 완료!")
        st.markdown(f"""
        ### 결과
        $$
        \\int_{{{x_start}}}^{{{x_end}}} ({poly_str}) \\,dx = {final_result:.4f}
        $$
        """)
        
        with st.expander("계산 과정 상세 보기"):
            st.write("부정적분 함수:")
            st.latex(r"F(x) = \frac{" + str(a) + r"}{3}x^3 + \frac{" + str(b) + r"}{2}x^2 + " + str(c) + "x")
            
            st.markdown(f"**1. 구간 끝점 대입 ($x = {x_end}$):**")
            st.latex(f"F({x_end}) = {result_end:.4f}")
            
            st.markdown(f"**2. 구간 시작점 대입 ($x = {x_start}$):**")
            st.latex(f"F({x_start}) = {result_start:.4f}")
            
            st.markdown("**3. 최종 계산:**")
            st.latex(f"{result_end:.4f} - {result_start:.4f} = {final_result:.4f}")

# ---------------------------------------------------------
# 2. 기본 연산 모드 (실수 지원 유지)
# ---------------------------------------------------------
else:
    st.subheader("🧮 사칙연산 및 공학용 계산")
    
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
            if sub_calc_type == "덧셈":
                res = num1 + num2; eq = f"{num1} + {num2}"
            elif sub_calc_type == "뺄셈":
                res = num1 - num2; eq = f"{num1} - {num2}"
            elif sub_calc_type == "곱셈":
                res = num1 * num2; eq = f"{num1} \\times {num2}"
            elif sub_calc_type == "나눗셈":
                if num2==0: st.error("0으로 나눌 수 없음"); st.stop()
                res = num1 / num2; eq = f"{num1} \\div {num2}"
            elif sub_calc_type == "나머지":
                if num2==0: st.error("0으로 나눌 수 없음"); st.stop()
                res = num1 % num2; eq = f"{num1} \\pmod {{{num2}}}"
            elif sub_calc_type == "거듭제곱":
                res = math.pow(num1, num2); eq = f"{num1}^{{{num2}}}"
            elif sub_calc_type == "로그":
                if num1<=0 or num2<=0 or num2==1: st.error("로그 범위 오류"); st.stop()
                res = math.log(num1, num2); eq = f"\\log_{{{num2}}}({num1})"
                
            st.success(f"결과: {res:.4f}")
            st.latex(f"{eq} = {res:.4f}")
        except Exception as e:
            st.error(f"오류: {e}")
