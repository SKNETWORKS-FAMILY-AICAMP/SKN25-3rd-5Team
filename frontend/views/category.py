import streamlit as st
import pandas as pd

def render():

    st.title("맞춤형 여행지 추천")
    st.write("설정한 조건에 맞춰 최적의 여행 추천지를 보여줍니다.")
    st.divider()

    # 필터 (예시 입력 -> 수정 예정)
    col1, col2 = st.columns(2)

    with col1:
        departure = st.selectbox("출발지 선택", ["전체", "서울", "부산", "대구"])

    with col2:
        purpose = st.selectbox("여행 목적", ["전체", "힐링", "맛집", "액티비티"])

    col3, col4 = st.columns(2)

    with col3:
        transportation = st.selectbox("이동 수단", ["전체", "자가용", "대중교통"])

    with col4:
        companion = st.multiselect("동행자 유형", ["혼자", "친구", "연인", "가족"])

    col5, col6, col7 = st.columns(3)

    with col5:
        travel_type = st.multiselect("여행 유형", ["자연", "도시", "바다"])

    with col6:
        duration = st.slider("여행 시간 (시간)", 1, 24, 5)

    with col7:
        st.markdown("<br>", unsafe_allow_html=True)
        search = st.button("🔍 검색", use_container_width=True)

    # 더미 데이터 
    data = pd.DataFrame({
        "출발지": ["서울", "부산", "대구", "서울", "부산"],
        "여행지": ["강릉", "제주", "부산", "가평", "여수"],
        "목적": ["힐링", "맛집", "액티비티", "힐링", "맛집"],
        "이동수단": ["자가용", "비행기", "기차", "자가용", "기차"],
        "동행자": ["연인", "친구", "혼자", "가족", "연인"],
        "유형": ["자연", "바다", "도시", "자연", "바다"],
        "소요시간": [3, 2, 1, 4, 3]
    })

    filtered_df = data.copy()

    # 검색 버튼 클릭
    if search:

        if departure != "전체":
            filtered_df = filtered_df[filtered_df["출발지"] == departure]

        if purpose != "전체":
            filtered_df = filtered_df[filtered_df["목적"] == purpose]

        if transportation != "전체":
            filtered_df = filtered_df[filtered_df["이동수단"] == transportation]

        if companion:
            filtered_df = filtered_df[filtered_df["동행자"].isin(companion)]

        if travel_type:
            filtered_df = filtered_df[filtered_df["유형"].isin(travel_type)]

        filtered_df = filtered_df[filtered_df["소요시간"] <= duration]

    # 결과 개수 출력
    total = len(filtered_df)
    st.write(f"Showing {total} results")

    # 결과 출력 
    if total == 0:
        st.warning("조건에 맞는 여행지가 없습니다 😢")
    else:
        for i, row in filtered_df.iterrows():

            col1, col2 = st.columns([2,1])

            with col1:
                st.markdown(f"""
                ### 📍 {row['여행지']}
                - 출발지: {row['출발지']}
                - 유형: {row['유형']}
                - 목적: {row['목적']}
                - 소요시간: {row['소요시간']}시간
                """)

           