import streamlit as st
import datetime

# 페이지 제목과 설명
st.set_page_config(page_title="민서와 규민's Simple Homepage", layout="wide")

# 페이지 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# 페이지 이동 함수
def go_to_page(page):
    st.session_state.page = page

# 메인 페이지 구현
if st.session_state.page == 'home':
    # 제목과 간단한 소개
    st.title("Welcome to 민서와 규민's Homepage!")
    st.write("This is a simple homepage built with Streamlit.")
    
    # 이미지 추가
    st.image("https://via.placeholder.com/800x300.png?text=민서와 규민's+Website", use_column_width=True)
    
    # 섹션 1: About Me
    st.header("About Me")
    st.write("""
    Hi, I'm 민서와 규민! I am currently working on creating some exciting projects using HTML and Little Man Computer (LMC).
    This page is built to showcase some personal and collaborative projects, and share memories.
    """)

    # 섹션 2: Recent Projects
    st.header("Recent Projects")
    st.write("""
    - **Little Man Computer (LMC) Simulation:** Working on simulating memory and operations.
    - **Personal HTML Website:** Crafting a personal website to showcase blog posts and personal projects.
    - **Couple Memory Website:** A creative platform for documenting shared memories with a loved one.
    """)

    # 사용자로부터 사진 업로드 받기
    st.header("Upload a Photo")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    # 이미지 업로드 시 표시
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # '기념일' 페이지로 이동하는 버튼
    if st.button('Go to Anniversary Page'):
        go_to_page('anniversary')

    # 섹션 3: Contact
    st.header("Contact Me")
    st.write("Feel free to reach out at: [민서와 규민@example.com](mailto:민서와 규민@example.com)")
    
    # 푸터
    st.write("---")
    st.write("© 2024 민서와 규민 - All Rights Reserved")

# '기념일' 페이지
elif st.session_state.page == 'anniversary':
    st.title("Anniversary Page")
    st.write("This is where you can track your special anniversaries.")
    
    # 달력 기능: 기념일 날짜 선택
    selected_date = st.date_input(
        "Select your anniversary date",
        datetime.date.today()
    )
    
    st.write(f"Your selected anniversary date is: {selected_date}")

    # 다시 홈 페이지로 이동하는 버튼
    if st.button('Go to Home Page'):
        go_to_page('home')
