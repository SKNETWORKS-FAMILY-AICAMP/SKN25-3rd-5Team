import streamlit as st
import requests  # 백엔드 호출을 위해 추가

def render():
    # 3. 메인 화면 구성
    st.title("여행 플래너")
    st.write("설정한 조건에 맞춰 최적의 여행 경로를 설계합니다.")
    st.markdown("---")

    # 1행: 출발지 / 목적지
    col1, col2 = st.columns(2)
    with col1:
        departure = st.text_input("출발지", placeholder="출발지를 입력하세요")
    with col2:
        destination = st.text_input("목적지", placeholder="목적지를 입력하세요")

    # 2행: 여행 유형 / 이동 수단 / 출발 시간 슬라이더
    col3, col4, col5 = st.columns([1, 1, 2])

    with col3:
        travel_type = st.selectbox(
            "여행 유형",
            ["휴양", "액티비티", "맛집 탐방", "문화유산 관람", "쇼핑"],
            index=None,
            placeholder="유형을 선택하세요"
        )

    with col4:
        transportation = st.selectbox(
            "이동 수단",
            ["항공", "철도", "버스", "자가용", "도보"],
            index=None,
            placeholder="수단을 선택하세요"
        )

    with col5:
        departure_hour = st.slider(
            "출발 시간",
            min_value=0,
            max_value=23,
            value=9,
            step=1,
            format="%d시"
        )
        period = "오전" if departure_hour < 12 else "오후"
        disp_h = departure_hour if departure_hour <= 12 else departure_hour - 12
        disp_h = 12 if disp_h == 0 else disp_h
        st.caption(f"✔ {period} {disp_h}시 ({departure_hour:02d}:00)")

    # 일정 생성 버튼
    st.write("")
    _, center, _ = st.columns([2, 1, 2])
    with center:
        generate_btn = st.button("일정 생성", use_container_width=True)

    # 결과 출력
    if generate_btn:
        if not (departure and destination and travel_type and transportation):
            st.error("모든 조건을 설정해야 일정이 생성됩니다.")
        else:
            # --- 백엔드 연결 로직 시작 ---
            # llm.py의 프롬프트가 잘 분석할 수 있도록 질문 문장을 구성합니다.
            plan_question = (
                f"출발지: {departure}, 목적지: {destination}, "
                f"테마: {travel_type}, 이동수단: {transportation}, "
                f"출발시간: {departure_hour}시"
            )

            with st.spinner("데이터 기반 최적의 경로를 설계 중입니다..."):
                try:
                    # 백엔드 호출 (page_type을 'plan'으로 전송)
                    response = requests.post(
                        "http://backend:8000/ask",
                        json={
                            "page_type": "plan", 
                            "question": plan_question
                        },
                        timeout=120  # 일정 생성은 시간이 좀 걸릴 수 있으므로 타임아웃 넉넉히 설정
                    )

                    if response.status_code == 200:
                        ai_plan = response.json().get("answer", "일정을 생성할 수 없습니다.")
                        
                        st.markdown("---")
                        st.markdown('<p class="result-header">📍나의 맞춤 여행 플랜</p>', unsafe_allow_html=True)
                        st.markdown(f"**[ {departure} ]** 에서 **[ {destination} ]** (으)로 떠나는 일정을 확인하세요.")
                        st.write("")

                        # 상단 요약 박스 (기존 디자인 유지)
                        res_col1, res_col2, res_col3 = st.columns(3)
                        with res_col1:
                            st.markdown(f'<div class="custom-result-box"><span class="result-label">이동 수단</span>{transportation} 이용</div>', unsafe_allow_html=True)
                        with res_col2:
                            st.markdown(f'<div class="custom-result-box"><span class="result-label">출발 시간</span>{period} {disp_h}시 출발</div>', unsafe_allow_html=True)
                        with res_col3:
                            st.markdown(f'<div class="custom-result-box"><span class="result-label">선택 테마</span>{travel_type} 중심 일정</div>', unsafe_allow_html=True)

                        # AI가 생성한 상세 일정 출력
                        st.info("📍 **상세 일정 타임라인**")
                        st.markdown(ai_plan) # 텍스트 영역보다 마크다운이 읽기 편해서 변경했습니다.

                    else:
                        st.error("백엔드 서버에서 일정을 가져오지 못했습니다.")
                
                except Exception as e:
                    st.error(f"연결 에러: {str(e)}")