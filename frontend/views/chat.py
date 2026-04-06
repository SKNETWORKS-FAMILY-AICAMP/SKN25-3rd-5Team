import streamlit as st
import requests
import os
import uuid  # 세션 ID 생성을 위해 필요
from dotenv import load_dotenv

load_dotenv()

def render():
    st.title("여행챗봇")
    st.caption("AI travel assistant (RAG 기반)")
    st.divider()

    # [수정 없음] 기존 세션 ID 로직 (없으면 생성)
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # [기존 틀 유지] 메시지 기록 초기화 (사용자님이 작성하신 문구 그대로)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": """
                안녕하세요 😊
                
                **맞춤 여행 추천 챗봇**이에요!
                우리 DB의 실제 관광 데이터를 바탕으로 답변해 드립니다.

                어떤 여행을 계획하고 계신가요?
                예를 들어 이렇게 말해주시면 좋아요:

                - "서울에서 2시간 내로 갈 수 있는 데이트 코스 추천해줘"
                - "반려동물과 함께 갈 수 있는 강릉 카페 알려줘"
                - "휠체어로 이용 가능한 제주도 관광지 추천해줘"

                조건을 알려주시면 딱 맞게 추천해드릴게요 ✈️"""
            }
        ]

    # 기존 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("메세지를 입력해주세요."):
        # 1. 화면에 사용자 메시지 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. 백엔드 API를 통해 RAG 답변 가져오기
        with st.chat_message("assistant"):
            with st.spinner("최적의 여행 데이터를 검색 중입니다..."):
                try:
                    # [데이터 보완] 백엔드에서 에러 나지 않도록 필수값 포함
                    payload = {
                        "page_type": "chat",
                        "question": prompt,
                        "session_id": st.session_state.session_id,
                        "chat_history": st.session_state.messages[:-1]
                    }

                    # 백엔드 호출
                    response = requests.post(
                        "http://backend:8000/ask", 
                        json=payload, 
                        timeout=120
                    )

                    if response.status_code == 200:
                        answer = response.json().get("answer", "답변을 가져오지 못했습니다.")
                        st.markdown(answer)
                        # 대화 기록 저장
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error(f"백엔드 오류: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"서버에 연결할 수 없습니다: {e}")