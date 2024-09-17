import streamlit as st

# app2.py의 내용
st.title("Welcome to App 2")
st.write("This is another page (App 2). You have successfully redirected to this page.")

# 버튼을 눌러서 홈으로 돌아가기
if st.button('Go back to Home Page'):
    st.experimental_rerun()
