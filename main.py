import streamlit as st
import math
import numpy as np
from fractions import Fraction

# -----------------------------------------------------------------------------
# [Helper Function] 분수를 LaTeX 문자열로 변환하는 함수
# 예: Fraction(1, 2) -> "\frac{1}{2}", Fraction(3, 1) -> "3"
# -----------------------------------------------------------------------------
def to_latex_frac(val):
    # 실수형(float)이 들어오면 분수로 근사 변환
    if isinstance(val, float):
        # 분모가 너무 커지지 않도록 제한 (예: 0.3333... -> 1/3)
        frac = Fraction(val).limit_denominator(10000)
    else:
        frac = Fraction(val)
        
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        # 음수 부호 처리 (보기 좋게 앞으로 빼기)
        sign = "-" if frac.numerator < 0 else ""
        num = abs(frac.numerator)
        return f"{sign}\\frac{{{num}}}{{{frac.denominator}}}"

# -----------------------------------------------------------------------------
# 메인 앱 코드
# -----------------------------------------------------------------------------
st.set_page_config(page_title="수학 & 정적분 계산기", page_icon="∫")

st.title("🧮 수학 & 정적분 계산기")
st.markdown("결과를 **분수**로 정확하게 계산하여 보여줍니다.")
st.divider()

operation = st.selectbox(
    "원하는 기능을 선택하세요",
    [
        "기본 연산 (사칙연산/지수/로그)",
        "이차함수 정적분 (Definite Integral)"
    ]
)

# ---------------------------------------------------------
# 1. 이차함수 정적분 모드 (분수 지원)
# ---------------------------------------------------------
if operation == "이차함수 정적분 (Definite Integral)":
    
    st.subheader("∫ 이차함수 정적분 계산")
    st.markdown(r"함수식: $f(x) = ax^2 + bx + c$")
    st.info("💡 계수와 적분 범위는 정수만 입력 가능합니다.")
    
    # 계수 입력
    st.markdown("**1. 계수 입력 (정수)**")
    col1, col2, col3 = st.columns(3)
    with col1: a = st.number_input("a (x²의 계수)", value=1, step=1)
    with col2: b = st.number_input("b (x의 계수)", value=0, step=1)
    with col3: c = st.number_input("c (상수항)", value=0, step=1)
        
    # 범위 입력
    st.markdown("**2. 적분 범위 및 옵션**")
    rc1, rc2 = st.columns(2)
    with rc1: x_start = st.number_input("적분 시작점 (x₁)", value=0, step=1)
    with rc2: x_end = st.number_input("적분 끝점 (x₂)", value=5, step=1)
    
    use_abs = st.checkbox("절댓값 포함 계산 (|f(x)|)", value=False)

    if st.button("적분 계산하기", type="primary"):
        
        # 부정적분 함수 (Fraction 사용으로 정확도 유지)
        def integral_func_frac(x, a, b, c):
            # (a/3)x^3 + (b/2)x^2 + cx
            # Fraction을 사용하여 부동소수점 오차 제거
            term1 = Fraction(a, 3) * (x ** 3)
            term2 = Fraction(b, 2) * (x ** 2)
            term3 = c * x
            return term1 + term2 + term3

        poly_str_base = f"{a}x^2 + {b}x + {c}".replace("+-", "- ").replace("+ -", "- ")
        final_val = 0
        eq_display = ""
        steps_log = []

        # === 절댓값 모드 ===
        if use_abs:
            st.write("🔍 절댓값 계산을 위해 구간을 분석합니다.")
            
            # 근 찾기 (numpy 사용)
            if abs(a) < 1e-9: 
                roots = [-c/b] if abs(b) > 1e-9 else []
            else:
                roots = np.roots([a, b, c])
            
            # 범위 내 실근 필터링
            valid_roots = []
            for r in roots:
                if np.isreal(r):
                    r_real = np.real(r)
                    if min(x_start, x_end) < r_real < max(x_start, x_end):
                        valid_roots.append(r_real)
            valid_roots.sort()

            points = [x_start] + valid_roots + [x_end]
            points.sort() 
            
            total_area = 0
            steps_log.append("구간별 계산 내역:")
            
            for i in range(len(points) - 1):
                p_s, p_e = points[i], points[i+1]
                
                # 구간 계산 (여기는 근이 실수일 수 있으므로 float 계산 후 분수 변환)
                # 근이 무리수일 경우 완벽한 분수 표현은 어렵지만 근사치로 표현
                val_end = integral_func_frac(p_e, a, b, c) # float가 섞일 수 있음
                val_start = integral_func_frac(p_s, a, b, c)
                seg_res = val_end - val_start
                
                # float -> Fraction 변환 (근사)
                if isinstance(seg_res, float):
                    seg_res = Fraction(seg_res).limit_denominator(100000)
                
                area = abs(seg_res)
                total_area += area
                
                steps_log.append(f"- 구간 [{p_s:.2f}, {p_e:.2f}] 넓이: ${to_latex_frac(area)}$")

            final_val = total_area
            eq_display = f"\\int_{{{x_start}}}^{{{x_end}}} |{poly_str_base}| \\,dx"

        # === 일반 정적분 모드 ===
        else:
            # 입력값이 모두 정수이므로 결과는 무조건 유리수(Fraction)
            res_end = integral_func_frac(x_end, a, b, c)
            res_start = integral_func_frac(x_start, a, b, c)
            final_val = res_end - res_start
            
            eq_display = f"\\int_{{{x_start}}}^{{{x_end}}} ({poly_str_base}) \\,dx"
            steps_log.append(f"$F({x_end}) = {to_latex_frac(res_end)}$")
            steps_log.append(f"$F({x_start}) = {to_latex_frac(res_start)}$")

        # 결과 출력
        st.success("계산 완료!")
        
        # 최종 결과를 LaTeX 분수로 변환
        final_latex = to_latex_frac(final_val)
        
        st.markdown(f"""
        ### 결과
        $$
        {eq_display} = {final_latex}
        $$
        """)
        
        with st.expander("계산 과정 상세 보기"):
            if use_abs:
                st.write(f"**범위 내 근:** {[round(r, 2) for r in valid_roots]}")
            else:
                st.write("부정적분 함수:")
                # 계수도 분수로 표현
                fa = to_latex_frac(Fraction(a, 3))
                fb = to_latex_frac(Fraction(b, 2))
                st.latex(f"F(x) = {fa}x^3 + {fb}x^2 + {c}x")
            
            for log in steps_log:
                st.write(log)

# ---------------------------------------------------------
# 2. 기본 연산 모드 (간단한 분수 표현 적용)
# ---------------------------------------------------------
else:
    st.subheader("🧮 사칙연산 및 공학용 계산")
    
    sub_calc_type = st.selectbox("연산 종류", ["덧셈", "뺄셈", "곱셈", "나눗셈", "나머지", "거듭제곱", "로그"])
    c1, c2 = st.columns(2)
    with c1: n1 = st.number_input("첫 번째 숫자", value=0.0)
    with c2: n2 = st.number_input("두 번째 숫자", value=0.0)
        
    if st.button("계산하기", type="primary"):
        res = 0
        eq = ""
        try:
            if sub_calc_type == "덧셈": res = n1 + n2; eq = f"{n1} + {n2}"
            elif sub_calc_type == "뺄셈": res = n1 - n2; eq = f"{n1} - {n2}"
            elif sub_calc_type == "곱셈": res = n1 * n2; eq = f"{n1} \\times {n2}"
            elif sub_calc_type == "나눗셈":
                if n2==0: st.error("0 불가능"); st.stop()
                res = n1 / n2; eq = f"{n1} \\div {n2}"
            elif sub_calc_type == "나머지": res = n1 % n2; eq = f"{n1} \\pmod {{{n2}}}"
            elif sub_calc_type == "거듭제곱": res = math.pow(n1, n2); eq = f"{n1}^{{{n2}}}"
            elif sub_calc_type == "로그": res = math.log(n1, n2); eq = f"\\log_{{{n2}}}({n1})"
            
            # 결과 출력 (분수 변환 시도)
            res_latex = to_latex_frac(res)
            
            st.success(f"결과: {res_latex} (소수점: {res:.4f})")
            st.latex(f"{eq} = {res_latex}")
            
        except Exception as e:
            st.error(f"오류: {e}")
