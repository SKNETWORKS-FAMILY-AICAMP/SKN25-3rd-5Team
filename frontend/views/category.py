import streamlit as st
import requests

def render():
    st.title("맞춤형 여행지 추천")
    st.write("설정한 조건에 맞춰 최적의 여행 추천지를 보여줍니다.")
    st.divider()

    # 필터 
    col1, col2 = st.columns(2)

    with col1:
        destination = st.selectbox("목적지 선택", [
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
        "관광지",
        "음식점",
        "숙박",
        "문화시설",
        "레포츠",
        "쇼핑",
        "축제/공연/행사"
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
            "destination": destination,
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

        results = data["results"]["items"]

        def get_source_label(source):
            if source == "pet":
                return "🐶 반려동물 가능"
            elif source == "barrier_free":
                return "♿ 무장애 여행지"
            else:
                return "📍 일반 관광지"
            
        # 출력 값
        if len(results) == 0:
            st.warning("조건에 맞는 여행지가 없습니다 😢")
        else:
            for item in results:
                st.markdown(f"""
                ### 📍 {item['title']}

                📍 **지역**  
                {item['region']}

                🏷 **유형**  
                {item.get('tag', '추천')}

                {get_source_label(item['source'])}

                💡 **추천 이유**  
                {item['description']}
                """)
                st.divider()
        
    