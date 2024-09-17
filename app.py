import streamlit as st

# 버튼 클릭 시 app2.py로 리디렉션하는 방법
if st.button('Go to App2'):
    st.write("""
        <meta http-equiv="refresh" content="0; url=app2.py">
    """, unsafe_allow_html=True)
