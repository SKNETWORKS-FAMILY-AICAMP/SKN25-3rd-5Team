import streamlit as st
import sys
import os

# 현재 파일 기준 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# frontend 폴더를 import 경로에 추가
sys.path.append(BASE_DIR)

class App:
    def __init__(self):
        st.set_page_config(page_title="Tripick", layout="wide")

        # CSS 
        with open(os.path.join(BASE_DIR, "style.css")) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        # 상태
        if "page" not in st.session_state:
            st.session_state.page = "about"

    def go(self, page):
        st.session_state.page = page

    def render_nav(self):
        col1, col2, col3, col4, col5= st.columns([2,1,1,1,1])

        with col1:
            st.image(os.path.join(BASE_DIR, "assets/logo.png"), width=250)

        with col2:
            if st.button("여행 찾기"):
                self.go("category")

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
            from views import about
            about.render()

        elif page == "category":
            from views import category
            category.render()

        elif page == "chat":
            from views import chat
            chat.render()

        elif page == "plan":
            from views import plan
            plan.render()


if __name__ == "__main__":
    App().run()