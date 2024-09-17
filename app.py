import streamlit as st

# 페이지 제목과 설명
st.set_page_config(page_title="Vincent's Simple Homepage", layout="wide")

# 제목과 간단한 소개
st.title("Welcome to Vincent's Homepage!")
st.write("This is a simple homepage built with Streamlit.")

# 이미지 추가 (이미지 파일 경로를 사용하거나 URL로 삽입 가능)
st.image("https://via.placeholder.com/800x300.png?text=Vincent's+Website", use_column_width=True)

# 섹션 1: About Me
st.header("About Me")
st.write("""
Hi, I'm Vincent! I am currently working on creating some exciting projects using HTML and Little Man Computer (LMC).
This page is built to showcase some personal and collaborative projects, and share memories.
""")

# 섹션 2: Recent Projects
st.header("Recent Projects")
st.write("""
- **Little Man Computer (LMC) Simulation:** Working on simulating memory and operations.
- **Personal HTML Website:** Crafting a personal website to showcase blog posts and personal projects.
- **Couple Memory Website:** A creative platform for documenting shared memories with a loved one.
""")

# 섹션 3: Contactdd
st.header("Contact Me")
st.write("Feel free to reach out at: [vincent@example.com](mailto:vincent@example.com)")

# 푸터
st.write("---")
st.write("© 2024 Vincent - All Rights Reserved")

