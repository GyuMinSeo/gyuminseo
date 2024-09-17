import streamlit as st
import os
import datetime

# 페이지 제목과 설명
st.set_page_config(page_title="민서와 규민's Lovely Homepage", layout="wide")

# 페이지 상태 초기화 (최상단에 위치)
if 'page' not in st.session_state:
    st.session_state.page = 'home'  # 기본 페이지는 'home'로 설정
if 'post_detail' not in st.session_state:
    st.session_state.post_detail = None  # 기본적으로 상세 페이지는 None으로 설정

# CSS 파일 불러오기 함수
def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# CSS 파일 불러오기
load_css("style.css")

# 이미지 및 게시물 저장 디렉토리 설정
POSTS_DIR = "posts"
os.makedirs(POSTS_DIR, exist_ok=True)
IMAGE_DIR = "uploaded_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# 파일 경로 불러오기 함수
def get_uploaded_images():
    """저장된 이미지 파일 목록을 불러오는 함수"""
    return [f for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]

# 게시물 저장 함수
def save_post(title, date, content, images):
    post_dir = os.path.join(POSTS_DIR, title)
    os.makedirs(post_dir, exist_ok=True)
    
    # 게시물 내용 저장 (인코딩을 utf-8로 지정)
    with open(os.path.join(post_dir, "content.txt"), "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"Date: {date}\n")
        f.write(f"Content: {content}\n")
    
    # 이미지 저장
    for i, image in enumerate(images):
        image_path = os.path.join(post_dir, f"image_{i+1}.jpg")
        with open(image_path, "wb") as img_file:
            img_file.write(image.getbuffer())

# 게시물 불러오기 함수
def load_posts():
    posts = []
    for post_name in os.listdir(POSTS_DIR):
        post_dir = os.path.join(POSTS_DIR, post_name)
        if os.path.isdir(post_dir):
            # 게시물 내용 불러오기 (인코딩을 utf-8로 지정)
            with open(os.path.join(post_dir, "content.txt"), "r", encoding="utf-8") as f:
                post_data = f.readlines()
                title = post_data[0].split(": ")[1].strip()
                date = post_data[1].split(": ")[1].strip()
                content = post_data[2].split(": ")[1].strip()
            images = [os.path.join(post_dir, img) for img in os.listdir(post_dir) if img.endswith(".jpg")]
            posts.append({"title": title, "date": date, "content": content, "images": images})
    return posts

# 댓글 저장 파일 경로
COMMENTS_FILE = "comments.txt"

# 댓글 저장 함수
def save_comment(post_title, comment):
    with open(COMMENTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{post_title}: {comment}\n")

# 댓글 불러오기 함수
def load_comments():
    comments = {}
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    post_title, comment = line.strip().split(": ", 1)
                    if post_title in comments:
                        comments[post_title].append(comment)
                    else:
                        comments[post_title] = [comment]
                except ValueError:
                    continue
    return comments

# 페이지 이동 함수
def go_to_page(page):
    st.session_state.page = page
    st.rerun()

# 사이드바 메뉴 생성
st.sidebar.title("우리의 발자취")
menu = st.sidebar.radio("Go to", ["Home", "기념일", "사진첩", "게시물"])

# 사이드바에서 선택된 메뉴에 따라 페이지 상태 업데이트
if menu == "Home":
    st.session_state.page = 'home'
elif menu == "기념일":
    st.session_state.page = 'anniversary'
elif menu == "사진첩":
    st.session_state.page = 'photo'
elif menu == "게시물":
    st.session_state.page = '게시물'

# 페이지 렌더링 처리
if st.session_state.page == '게시물':
    # 게시물 목록 표시
    st.header("게시물 목록")
    
    # 게시물 업로드 페이지로 이동하는 버튼
    if st.button("게시물 업로드"):
        st.session_state.page = 'upload_post'  # 페이지 상태 변경
        st.rerun()  # 페이지 새로고침


    # 게시물 불러오기 및 표시
    posts = load_posts()
    comments = load_comments()

    for post in posts:
        # 게시물 제목을 클릭하면 세부 페이지로 이동
        if st.button(f"View {post['title']}", key=post['title']):
            st.session_state.post_detail = post['title']  # 클릭된 게시물 제목 저장
            st.session_state.page = 'post_detail'  # 페이지 상태 변경
            st.rerun()  # 페이지 새로고침


elif st.session_state.page == 'upload_post':
    # 게시물 업로드 페이지
    st.header("Post a New Memory")
    
    # 게시물 정보 입력
    title = st.text_input("Title")
    date = st.date_input("Date", datetime.date.today())
    content = st.text_area("Content")
    images = st.file_uploader("Choose images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

    if st.button("Submit Post"):
        save_post(title, date, content, images)
        st.success("Post saved!")
        st.session_state.page = '게시물'  # 페이지 상태 변경
        st.rerun()  # 페이지 새로고침


elif st.session_state.page == 'post_detail':
    # 세부 페이지 렌더링
    post_title = st.session_state.get('post_detail', None)
    posts = load_posts()  # 다시 불러오기
    comments = load_comments()  # 댓글 다시 불러오기

    if post_title:
        # 게시물 세부 내용 불러오기
        post = next((p for p in posts if p["title"] == post_title), None)
        if post:
            st.header(post["title"])
            st.write(f"Date: {post['date']}")
            st.write(post["content"])
            for img in post["images"]:
                st.image(img, use_column_width=True)
            
            # 댓글 표시
            if post_title in comments:
                st.write("Comments:")
                for comment in comments[post_title]:
                    st.write(f"- {comment}")
            
            # 댓글 입력 및 저장
            new_comment = st.text_input("Add a comment")
            if st.button("Submit Comment"):
                save_comment(post_title, new_comment)
                st.success("Comment added!")
                st.rerun()  # 페이지 새로고침

            # 뒤로가기 버튼
            if st.button("Back to posts"):
                del st.session_state['post_detail']  # 상세 페이지 상태 삭제
                st.session_state.page = '게시물'  # 페이지 상태 변경
                st.rerun()  # 페이지 새로고침

elif st.session_state.page == 'home':
    # 홈 페이지
    st.markdown('<h1 class="main-title">Welcome to 민서와 규민\'s Homepage!</h1>', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/800x300.png?text=민서와 규민's+Website", use_column_width=True)

elif st.session_state.page == 'anniversary':
    # 기념일 페이지
    st.title("Anniversary Page")
    
    # 시작일, 민서 생일, 규민 생일 설정
    starting_date = datetime.date(2024, 8, 28)
    minseo_birthday = datetime.date(2003, 10, 7)
    gyumin_birthday = datetime.date(2001, 11, 29)

    # 현재 날짜
    today = datetime.date.today()

    # D+일 계산
    days_difference = (today - starting_date).days
    days_difference2 = days_difference + 1
    st.write(f"{starting_date}로부터 {days_difference2}일이 지났습니다 (D+{days_difference2}).")

    # 생일까지 남은 날짜 계산
    def days_until_birthday(birthday):
        next_birthday = birthday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    # 민서 생일까지 남은 일수
    days_until_minseo_birthday = days_until_birthday(minseo_birthday)
    st.write(f"민서의 생일까지 {days_until_minseo_birthday}일 남았습니다.")

    # 규민 생일까지 남은 일수
    days_until_gyumin_birthday = days_until_birthday(gyumin_birthday)
    st.write(f"규민의 생일까지 {days_until_gyumin_birthday}일 남았습니다.")

elif st.session_state.page == 'photo':
    # 사진첩 페이지
    st.header("Upload a Photo")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_path = os.path.join(IMAGE_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(file_path, use_column_width=True)
        st.success(f"Image saved to {file_path}")

# 푸터
st.markdown('<p class="footer">© 2024 민서와 규민 - All Rights Reserved</p>', unsafe_allow_html=True)
