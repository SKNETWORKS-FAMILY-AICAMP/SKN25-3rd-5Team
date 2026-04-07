import streamlit as st
import requests

def render():
    # 3. 메인 화면 구성
    st.title("여행 플래너")
    st.write("설정한 조건에 맞춰 최적의 여행 경로를 설계합니다.")
    st.markdown("---")

    # 1행: 출발지 / 목적지
    col1, col2 = st.columns(2)
    with col1:
        departure = st.selectbox("출발지 선택", [
            "서울특별시",
            "부산광역시",
            "대구광역시",
            "인천광역시",
            "광주광역시",
            "대전광역시",
            "울산광역시",
            "세종특별자치시",
            "경기도",
            "강원특별자치도",
            "충청북도",
            "충청남도",
            "전북특별자치도",
            "전라남도",
            "경상북도",
            "경상남도",
            "제주특별자치도"
        ])
    with col2:
        destination = st.selectbox("도착지 선택", [
            "서울특별시",
            "부산광역시",
            "대구광역시",
            "인천광역시",
            "광주광역시",
            "대전광역시",
            "울산광역시",
            "세종특별자치시",
            "경기도",
            "강원특별자치도",
            "충청북도",
            "충청남도",
            "전북특별자치도",
            "전라남도",
            "경상북도",
            "경상남도",
            "제주특별자치도"
        ])

    # 2행: 여행 유형 / 이동 수단 / 출발 시간 슬라이더 — 균등 3열
    col3, col4, col5 = st.columns([1, 1, 2])

    with col3:
        travel_type = st.selectbox("여행 유형", [
        "가족/친지 방문",
        "교육/체험 프로그램",
        "교육/훈련/연수",
        "드라마 촬영지 방문",
        "문화예술/전시 관람",
        "스포츠 경기관람",
        "시티투어",
        "야외 스포츠/레포츠",
        "역사 유적지 방문",
        "온천/스파",
        "유흥/오락",
        "자연 및 풍경감상",
        "종교/성지순례",
        "지역 축제/이벤트",
        "카지노/경마 등",
        "테마파크/동식물원",
        "회의참가/시찰",
        "휴식/휴양",
        "쇼핑",
        "음식관광",
        "기타"
    ])

    with col4:
        transportation = st.selectbox("이동 수단", [
            "차량대여/렌트",
            "선박/해상 교통",
            "[정기] 고속/시외/시내버스",
            "자전거",
            "철도",
            "지하철",
            "도보",
            "택시",
            "항공기",
            "[부정기] 전세/관광버스",
            "자가용",
            "기타"
        ])

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

    # 일정 생성 버튼 — 중앙
    st.write("")
    _, center, _ = st.columns([2, 1, 2])
    with center:
        generate_btn = st.button("일정 생성", use_container_width=True)

    # 결과 출력
    if generate_btn:
        if not (departure and destination and travel_type and transportation):
            st.error("모든 조건을 설정해야 일정이 생성됩니다.")
        else:

            payload = {
                "departure": departure,
                "destination": destination,
                "travel_type": travel_type,
                "transportation": transportation,
                "departure_time": departure_hour
            }

            #  로딩 UI
            with st.spinner("AI가 여행 일정을 생성 중입니다... ✈️"):

                try:
                    res = requests.post(
                        "http://backend:8000/plan",
                        json=payload
                    )

                    if res.status_code != 200:
                        st.error("서버 오류가 발생했습니다.")
                        return

                    data = res.json()
                    plan_text = data.get("result", "일정 생성 실패")

                except Exception as e:
                    st.error(f"연결 실패: {e}")
                    return

            # 결과 UI
            st.markdown("---")
            st.markdown('<p class="result-header">📍 나의 맞춤 여행 플랜</p>', unsafe_allow_html=True)

            st.markdown(f"""
            **[ {departure} ] → [ {destination} ] 여행 일정**
            """)

            # 요약 카드
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                    <div class="custom-result-box">
                        <span class="result-label">🚗 이동 수단</span><br>
                        {transportation}
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="custom-result-box">
                        <span class="result-label">🕒 출발 시간</span><br>
                        {period} {disp_h}시 ({departure_hour:02d}:00)
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class="custom-result-box">
                        <span class="result-label">🎯 여행 유형</span><br>
                        {travel_type}
                    </div>
                """, unsafe_allow_html=True)

            # 일정 출력
            st.markdown("### 🗺 상세 일정")

            st.text_area(
                label="",
                value=plan_text,
                height=300
            )