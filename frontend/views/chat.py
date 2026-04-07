import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def render():
    st.title("여행챗봇")
    st.write("대화를 바탕으로 여행지 추천과 후속 계획을 도와줍니다.")
    st.divider()

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

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("메세지를 입력해주세요."):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        history = []
        for item in st.session_state.messages[:-1][-6:]:
            payload = {
                "role": item["role"],
                "content": item["content"]
            }
            if item["role"] == "assistant" and item.get("places"):
                payload["places"] = item["places"][:5]
            history.append(payload)

        with st.chat_message("assistant"):
            with st.spinner("최적의 여행 데이터를 검색 중입니다..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/chat",
                        json={
                            "message": prompt,
                            "history": history,
                            "limit": 5
                        },
                        timeout=120
                    )
                    res.raise_for_status()

                    data = res.json()
                    answer = data.get("answer", "답변을 가져오지 못했습니다.")
                    places = data.get("places", [])

                    st.markdown(answer)

                    assistant_message = {
                        "role": "assistant",
                        "content": answer,
                        "places": places,
                    }

                except Exception as e:
                    error_text = f"서버에 연결할 수 없습니다: {e}"
                    st.error(error_text)
                    assistant_message = {
                        "role": "assistant", 
                        "content": error_text
                    }

        st.session_state.messages.append(assistant_message)
