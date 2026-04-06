import streamlit as st
import requests

def render():

    st.title("맞춤형 여행지 추천")
    st.write("설정한 조건에 맞춰 최적의 여행 추천지를 보여줍니다.")
    st.divider()

    # 필터 (예시 입력 -> 수정 예정)
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
        purpose = st.selectbox("여행 목적", [
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

    col3, col4 = st.columns(2)

    with col3:
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

    with col4:
        companion = st.multiselect("동행자 유형", [
            "단독(혼자)",
            "친구",
            "연인",
            "배우자",
            "부모",
            "자녀",
            "형제/자매",
            "조부모",
            "손자/손녀",
            "직장동료",
            "학교 단체",
            "친목 단체/모임",
            "반려동물",
            "기타"
        ])

    col5, col6 = st.columns(2)


    with col5:
        duration = st.slider("최대 이동 시간(시간)", 1, 24, 5)

    with col6:
        st.markdown("<br>", unsafe_allow_html=True)
        search = st.button("🔍 검색", use_container_width=True)

    # API 호출
    if search:

        payload = {
            "departure": departure,
            "purpose": purpose,
            "transportation": transportation,
            "companion": companion,
            "duration": duration
        }

        res = requests.post(
            "http://backend:8000/recommend",
            json=payload
        )

        data = res.json()

        results = data.get("results", [])

        st.write(f"Showing {len(results)} results")

        if len(results) == 0:
            st.warning("조건에 맞는 여행지가 없습니다 😢")
        else:
            for row in results:
                col1, col2 = st.columns([2,1])

                with col1:
                    st.markdown(f"""
                    ### 📍 {row['title']}
                    - 지역: {row['sido']}
                    - 유형: {row['type']}
                    """)