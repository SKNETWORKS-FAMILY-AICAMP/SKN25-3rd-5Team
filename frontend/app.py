import streamlit as st
import requests

st.title("Mini Project 3")
st.write("Streamlit Frontend + FastAPI Backend + PostgreSQL")

if st.button("백엔드 확인"):
    try:
        res = requests.get("http://backend:8000/")
        st.json(res.json())
    except Exception as e:
        st.error(f"백엔드 연결 실패: {e}")

if st.button("DB 확인"):
    try:
        res = requests.get("http://backend:8000/db-check")
        st.json(res.json())
    except Exception as e:
        st.error(f"DB 확인 실패: {e}")