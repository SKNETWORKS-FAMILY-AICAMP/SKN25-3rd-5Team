import streamlit as st
import requests

def render():
    st.title("🎯 맞춤 여행지 가이드")
    st.subheader("데이터 분석을 통해 당신에게 꼭 맞는 여행지를 찾아드려요.")
    st.divider()

    # 1. 입력 폼 구성 (llm.py의 추론 로직에 필요한 데이터 수집)
    with st.form("recommend_filter_form"):
        st.write("📋 **사용자 성향 및 여행 조건을 선택해주세요**")
        
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("성별", ["남성", "여성"])
            age_group = st.selectbox("연령대", ["20대", "30대", "40대", "50대 이상"])
            sido = st.selectbox("지역 선택", ["서울", "경기", "강원", "제주", "부산", "경북", "전남"])
        
        with col2:
            companion = st.selectbox("동행자", ["혼자", "연인", "친구", "가족(아이 동반)", "가족(부모님 동반)"])
            purpose = st.multiselect("여행 목적", ["맛집 탐방", "힐링/휴식", "액티비티", "역사/문화", "자연 감상"], default=["힐링/휴식"])
            pet_friendly = st.radio("반려동물 동반 여부", ["예", "아니오"], index=1)

        submitted = st.form_submit_button("나에게 맞는 여행지 추천받기")

    # 2. 버튼 클릭 시 백엔드 호출
    if submitted:
        # llm.py의 [Step 1] 분석 로직이 잘 작동하도록 상세 정보를 문장으로 조합합니다.
        filter_question = (
            f"사용자 정보: {age_group} {gender}, "
            f"지역: {sido}, 목적: {', '.join(purpose)}, "
            f"동행자: {companion}, 반려동물 동반: {pet_friendly}"
        )

        with st.spinner("사용자 성향 데이터를 바탕으로 여행지를 매칭 중입니다..."):
            try:
                # [중요] page_type을 llm.py와 동일하게 'guide'로 설정합니다.
                response = requests.post(
                    "http://backend:8000/ask",
                    json={
                        "page_type": "guide", 
                        "question": filter_question
                    },
                    timeout=120
                )

                if response.status_code == 200:
                    answer = response.json().get("answer", "추천 결과가 없습니다.")
                    st.success("🎉 분석 결과, 다음 장소들을 추천해 드립니다!")
                    st.markdown("---")
                    st.markdown(answer) # LLM이 설명하는 추천 사유와 title이 출력됩니다.
                else:
                    st.error(f"추천 서비스 오류 (Status: {response.status_code})")
            
            except Exception as e:
                st.error(f"백엔드 서버 연결 실패: {str(e)}")