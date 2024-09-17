import streamlit as st

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# 페이지 상태 변경 함수
def go_to_page(page_name):
    st.session_state.page = page_name
    st.experimental_rerun()  # 상태 변경 후 페이지 새로고침

if st.session_state.page == 'home':
    st.title("Home Page")
    
    if st.button("Go to App2"):
        go_to_page('app2')
    
elif st.session_state.page == 'app2':
    st.title("App2 Page")
    
    if st.button("Go back to Home"):
        go_to_page('home')
