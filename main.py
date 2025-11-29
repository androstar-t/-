import streamlit as st
import math

# 페이지 기본 설정
st.set_page_config(page_title="나만의 수학 계산기", page_icon="🧮")

# 제목 및 설명
st.title("🧮 파이썬 수학 계산기")
st.markdown("사칙연산부터 지수, 로그까지 간편하게 계산하세요.")
st.divider()

# 사이드바에서 연산 모드 선택
operation = st.selectbox(
    "연산 종류를 선택하세요",
    [
        "덧셈 (+)", 
        "뺄셈 (-)", 
        "곱셈 (*)", 
        "나눗셈 (/)", 
        "나머지 연산 (Modulo)", 
        "거듭제곱 (Power)", 
        "로그 연산 (Logarithm)"
    ]
)

# 입력 인터페이스 (2개의 숫자를 받음)
col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input("첫 번째 숫자 (a)", value=0.0, step=1.0, format="%.2f")

with col2:
    # 로그 연산일 경우 두 번째 숫자는 '밑(Base)'이 됩니다.
    label_num2 = "두 번째 숫자 (b)"
    if "로그" in operation:
        label_num2 = "밑 (Base, b)"
    num2 = st.number_input(label_num2, value=0.0, step=1.0, format="%.2f")

# 계산 실행 버튼
if st.button("계산하기", type="primary"):
    result = 0
    equation = ""
    
    try:
        # 연산 로직
        if "덧셈" in operation:
            result = num1 + num2
            equation = f"{num1} + {num2}"
            
        elif "뺄셈" in operation:
            result = num1 - num2
            equation = f"{num1} - {num2}"
            
        elif "곱셈" in operation:
            result = num1 * num2
            equation = f"{num1} \\times {num2}"
            
        elif "나눗셈" in operation:
            if num2 == 0:
                st.error("오류: 0으로 나눌 수 없습니다.")
                st.stop()
            result = num1 / num2
            equation = f"{num1} \\div {num2}"
            
        elif "나머지" in operation:
            if num2 == 0:
                st.error("오류: 0으로 나눌 수 없습니다.")
                st.stop()
            result = num1 % num2
            equation = f"{num1} \\pmod {{{num2}}}"
            
        elif "거듭제곱" in operation:
            result = math.pow(num1, num2)
            equation = f"{num1}^{{{num2}}}"
            
        elif "로그" in operation:
            # 로그의 진수 조건(>0)과 밑 조건(>0, !=1) 확인
            if num1 <= 0:
                st.error("오류: 진수(첫 번째 숫자)는 0보다 커야 합니다.")
                st.stop()
            if num2 <= 0 or num2 == 1:
                st.error("오류: 밑(두 번째 숫자)은 0보다 크고 1이 아니어야 합니다.")
                st.stop()
            
            result = math.log(num1, num2)
            equation = f"\\log_{{{num2}}}({num1})"

        # 결과 출력 (LaTeX 수식 활용)
        st.success("계산 성공!")
        st.markdown(f"### 결과: $${equation} = {result:.4f}$$")
        
    except Exception as e:
        st.error(f"계산 중 오류가 발생했습니다: {e}")

# 바닥글
st.markdown("---")
st.caption("Created with Python & Streamlit")
