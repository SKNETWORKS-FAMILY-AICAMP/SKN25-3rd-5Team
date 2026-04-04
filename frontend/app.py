# import streamlit as st
# import requests

# st.title("Mini Project 3")
# st.write("Streamlit Frontend + FastAPI Backend + PostgreSQL")

# if st.button("백엔드 확인"):
#     try:
#         res = requests.get("http://backend:8000/")
#         st.json(res.json())
#     except Exception as e:
#         st.error(f"백엔드 연결 실패: {e}")

# if st.button("DB 확인"):
#     try:
#         res = requests.get("http://backend:8000/db-check")
#         st.json(res.json())
#     except Exception as e:
#         st.error(f"DB 확인 실패: {e}")

import streamlit as st


class App:
    def __init__(self):
        st.set_page_config(page_title="Tripick", layout="wide")

        # CSS 
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        # 상태
        if "page" not in st.session_state:
            st.session_state.page = "about"

    def go(self, page):
        st.session_state.page = page

    def render_nav(self):
        col1, col2, col3, col4, col5= st.columns([2,1,1,1,1])

        with col1:
            st.image("assets/logo.png", width=250)

        with col2:
            if st.button("여행 찾기"):
                self.go("home")

        with col3:
            if st.button("여행 챗봇"):
                self.go("chat")

        with col4:
            if st.button("일정 만들기"):
                self.go("plan")

        with col5:
            if st.button("서비스 소개"):
                self.go("about")


    def run(self):
        self.render_nav()

        page = st.session_state.page

        if page == "about":
            import views.about as about
            about.render()

        elif page == "home":
            st.write("여행 찾기")

        elif page == "chat":
            st.write("챗봇")

        elif page == "plan":
            st.write("일정")


if __name__ == "__main__":
    App().run()