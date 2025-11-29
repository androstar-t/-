import streamlit as st
import math
import numpy as np
from fractions import Fraction
import matplotlib.pyplot as plt # 그래프를 그리기 위한 라이브러리 추가

# -----------------------------------------------------------------------------
# [Helper Function] 분수를 LaTeX 문자열로 변환
# -----------------------------------------------------------------------------
def to_latex_frac(val):
    if isinstance(val, float):
        frac = Fraction(val).limit_denominator(100000)
    else:
        frac = Fraction(val)
        
    if frac.denominator == 1:
        return str(frac.numerator)
    elif frac.numerator == 0:
        return "0"
    else:
        sign = "-" if frac.numerator < 0 else ""
        num = abs(frac.numerator)
        return f"{sign}\\frac{{{num}}}{{{frac.denominator}}}"

# -----------------------------------------------------------------------------
# 메인 앱 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="수학 & 정적분 계산기", page_icon="∫")

# Matplotlib 한글 폰트 설정 (스트림릿 클라우드 환경 호환)
# 참고: 로컬 환경에서는 별도 폰트 설정이 필요할 수 있습니다.
plt.rcParams['axes.unicode_minus'] = False

st.title("🧮 수학 & 정적분 계산기")
st.markdown("결과를 **분수**로 계산하고 **그래프**로 시각화합니다.")
st.divider()

operation = st.selectbox(
    "원하는 기능을 선택하세요",
    [
        "기본 연산 (사칙연산/지수/로그)",
        "이차함수 정적분 (Definite Integral)"
    ]
)

# ---------------------------------------------------------
# 1. 이차함수 정적분 모드 (그래프 추가)
# ---------------------------------------------------------
if operation == "이차함수 정적분 (Definite Integral)":
    
    st.subheader("∫ 이차함수 정적분 계산 및 시각화")
    st.markdown(r"함수식: $f(x) = ax^2 + bx + c$")
    st.info("💡 계수와 적분 범위는 정수만 입력 가능합니다.")
    
    # 입력부
    col1, col2, col3 = st.columns(3)
    with col1: a = st.number_input("a (x²의 계수)", value=1, step=1)
    with col2: b = st.number_input("b (x의 계수)", value=0, step=1)
    with col3: c = st.number_input("c (상수항)", value=-1, step=1) # 예시를 위해 기본값 변경
        
    rc1, rc2 = st.columns(2)
    with rc1: x_start = st.number_input("적분 시작점 (x₁)", value=-2, step=1)
    with rc2: x_end = st.number_input("적분 끝점 (x₂)", value=2, step=1)
    
    use_abs = st.checkbox("절댓값 포함 계산 (|f(x)|)", value=True, help="체크하면 그래프와 x축 사이의 실제 넓이를 계산하고 그립니다.")

    if st.button("적분 계산 및 그래프 그리기", type="primary"):
        
        # 부정적분 함수
        def integral_func_frac(x, a, b, c):
            return Fraction(a, 3)*(x**3) + Fraction(b, 2)*(x**2) + c*x

        poly_str_base = f"{a}x^2 + {b}x + {c}".replace("+-", "- ").replace("+ -", "- ")
        final_val = 0
        eq_display = ""
        steps_log = []

        # === [계산 로직] 절댓값 모드 ===
        if use_abs:
            st.write("🔍 절댓값 계산을 위해 구간을 분석합니다.")
            # 근 찾기 및 구간 나누기 (이전 코드와 동일)
            if abs(a) < 1e-9: roots = [-c/b] if abs(b) > 1e-9 else []
            else: roots = np.roots([a, b, c])
            
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
            steps_log.append("구간별 계산 내역 (절댓값 적용):")
            
            for i in range(len(points) - 1):
                p_s, p_e = points[i], points[i+1]
                val_end = integral_func_frac(p_e, a, b, c)
                val_start = integral_func_frac(p_s, a, b, c)
                seg_res = val_end - val_start
                # float 근사 후 분수 변환
                if isinstance(seg_res, float): seg_res = Fraction(seg_res).limit_denominator(100000)
                area = abs(seg_res)
                total_area += area
                steps_log.append(f"- 구간 [{p_s:.2f}, {p_e:.2f}] 넓이: ${to_latex_frac(area)}$")

            final_val = total_area
            eq_display = f"\\int_{{{x_start}}}^{{{x_end}}} |{poly_str_base}| \\,dx"

        # === [계산 로직] 일반 모드 ===
        else:
            res_end = integral_func_frac(x_end, a, b, c)
            res_start = integral_func_frac(x_start, a, b, c)
            final_val = res_end - res_start
            eq_display = f"\\int_{{{x_start}}}^{{{x_end}}} ({poly_str_base}) \\,dx"
            steps_log.append(f"정적분 계산 (부호 포함):")

        # ---------------------------------------------------------
        # [시각화 로직] Matplotlib 그래프 그리기
        # ---------------------------------------------------------
        st.subheader("📊 그래프 시각화")
        
        # 그래프 데이터 생성
        # 적분 범위보다 조금 더 넓게 X축 설정
        range_span = max(abs(x_end - x_start), 2.0)
        x_buff = range_span * 0.25
        x_plot = np.linspace(min(x_start, x_end) - x_buff, max(x_start, x_end) + x_buff, 500)
        y_orig = a * x_plot**2 + b * x_plot + c
        
        # 실제 적분을 수행할 채우기 영역 데이터
        x_fill = np.linspace(min(x_start, x_end), max(x_start, x_end), 300)
        y_fill_orig = a * x_fill**2 + b * x_fill + c

        # 캔버스 생성
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # 공통 요소: X축, Y축, 격자, 시작/끝선
        ax.axhline(0, color='black', linewidth=1.0)
        ax.axvline(0, color='black', linewidth=1.0)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.axvline(x_start, color='r', linestyle='--', label=f'Start ($x={x_start}$)')
        ax.axvline(x_end, color='g', linestyle='--', label=f'End ($x={x_end}$)')

        if use_abs:
            # --- 절댓값 그래프 모드 ---
            y_abs = np.abs(y_orig)
            # 원래 함수 (점선 회색)
            ax.plot(x_plot, y_orig, 'k--', alpha=0.4, label=f"$f(x)$ Original")
            # 절댓값 함수 (실선 파랑)
            ax.plot(x_plot, y_abs, 'b-', linewidth=2, label=f"$|f(x)|$")
            # 면적 채우기 (파란색)
            ax.fill_between(x_fill, np.abs(y_fill_orig), color='dodgerblue', alpha=0.4, label="Area (넓이)")
            ax.set_title("이차함수 절댓값 정적분 (Total Area)")
        else:
            # --- 일반 정적분 모드 ---
            # 함수 (실선 파랑)
            ax.plot(x_plot, y_orig, 'b-', linewidth=2, label=f"$f(x)$")
            # 양수 면적 (파랑) / 음수 면적 (빨강) 채우기
            ax.fill_between(x_fill, y_fill_orig, where=(y_fill_orig >= 0), color='dodgerblue', alpha=0.4, interpolate=True, label="Positive Area (+)")
            ax.fill_between(x_fill, y_fill_orig, where=(y_fill_orig < 0), color='salmon', alpha=0.4, interpolate=True, label="Negative Area (-)")
            ax.set_title("일반 정적분 (Signed Area)")
            
        ax.legend()
        # 스트림릿에 그래프 표시
        st.pyplot(fig)

        # ---------------------------------------------------------
        # 결과 출력
        # ---------------------------------------------------------
        st.success("계산 완료!")
        final_latex = to_latex_frac(final_val)
        st.markdown(f"### 결과: $${eq_display} = {final_latex}$$")
        
        with st.expander("계산 과정 상세 보기"):
            if use_abs:
                st.write(f"**x축 교차점 (범위 내):** {[round(r, 2) for r in valid_roots]}")
            for log in steps_log:
                st.write(log)
            st.write("---")
            st.caption(f"최종 값 (소수점): {final_val:.4f}")

# ---------------------------------------------------------
# 2. 기본 연산 모드 (이전과 동일)
# ---------------------------------------------------------
else:
    st.subheader("🧮 사칙연산 및 공학용 계산")
    sub_calc_type = st.selectbox("연산 종류", ["덧셈", "뺄셈", "곱셈", "나눗셈", "나머지", "거듭제곱", "로그"])
    c1, c2 = st.columns(2)
    with c1: n1 = st.number_input("첫 번째 숫자", value=0.0)
    with c2: n2 = st.number_input("두 번째 숫자", value=0.0)
        
    if st.button("계산하기", type="primary"):
        res = 0; eq = ""
        try:
            # ... (기본 연산 로직 생략 - 이전 코드와 동일하게 사용하세요) ...
            if sub_calc_type == "덧셈": res = n1 + n2; eq = f"{n1} + {n2}"
            elif sub_calc_type == "뺄셈": res = n1 - n2; eq = f"{n1} - {n2}"
            elif sub_calc_type == "곱셈": res = n1 * n2; eq = f"{n1} \\times {n2}"
            elif sub_calc_type == "나눗셈":
                if n2==0: st.error("0 불가능"); st.stop()
                res = n1 / n2; eq = f"{n1} \\div {n2}"
            elif sub_calc_type == "나머지": res = n1 % n2; eq = f"{n1} \\pmod {{{n2}}}"
            elif sub_calc_type == "거듭제곱": res = math.pow(n1, n2); eq = f"{n1}^{{{n2}}}"
            elif sub_calc_type == "로그": res = math.log(n1, n2); eq = f"\\log_{{{n2}}}({n1})"

            res_latex = to_latex_frac(res)
            st.success(f"결과: {res_latex} (소수점: {res:.4f})")
            st.latex(f"{eq} = {res_latex}")
        except Exception as e:
            st.error(f"오류: {e}")
