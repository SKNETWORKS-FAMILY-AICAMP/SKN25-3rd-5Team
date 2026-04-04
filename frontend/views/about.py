import streamlit as st

def render():

    # 제목
    st.markdown("""
    <div class="hero fade-up">
        <h1>
            사용자 맞춤형 
            <span>여행 추천 시스템</span>
        </h1>
        <p>
            당신의 시간과 여행 조건을 고려해<br>  
            가장 현실적이고 효율적인 여행을 추천합니다.<br>
            이제 계획부터 이동까지 한 번에 해결하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="start-center">
        <div class="start-btn">
            지금 여행 계획 시작하기 →
        </div>
    </div>
    """, unsafe_allow_html=True)


    # 카드 
    col1, col2, col3, col4 = st.columns(4)

    cards = [
        ("맞춤 추천", "사용자 조건 기반 여행지 추천"),
        ("대화형 인터페이스", "AI 챗봇으로 여행 관련 질문 실시간 응답"),
        ("빠른 추천", "즉시 여행지 제공"),
        ("1000+", "다양한 여행지 데이터")
    ]

    for col, (value, label) in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(f"""
            <div class="card">
                <h2>{value}</h2>
                <p>{label}</p>
            </div>
            """, unsafe_allow_html=True)