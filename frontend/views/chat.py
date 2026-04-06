import streamlit as st
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def render():

    st.title("여행챗봇")
    st.caption("AI travel assistant")
    st.divider()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o-mini"

    if "messages" not in st.session_state:
        st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
            
            안녕하세요 😊
             
            맞춤 여행 추천 챗봇이에요!

            어떤 여행을 계획하고 계신가요?
            예를 들어 이렇게 말해주시면 좋아요:

            - "서울에서 2시간 내로 갈 수 있는 데이트 코스 추천해줘"
            - "혼자 힐링 여행 갈 곳 알려줘"
            - "뚜벅이로 갈 수 있는 여행지 추천해줘"

            조건을 알려주시면 딱 맞게 추천해드릴게요 ✈️"""
        }
    ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("메세지를 입력해주세요."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

