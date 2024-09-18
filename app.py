import streamlit as st
import os
import json
import datetime

# 페이지 제목과 설명
st.set_page_config(page_title="민서와 규민's Lovely Homepage", layout="wide")

# 페이지 상태 초기화 (최상단에 위치)
if 'page' not in st.session_state:
    st.session_state.page = 'home'  # 기본 페이지는 'home'으로 설정
if 'post_page' not in st.session_state:
    st.session_state.post_page = 'main'  # 게시물 페이지 기본값은 'main'

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

# 게시물 저장 함수
def save_post(title, date, content, images):
    """게시물을 저장하는 함수"""
    post_data = {
        "title": title,
        "date": date.isoformat(),
        "content": content,
        "images": [image.name for image in images]
    }

    post_file = os.path.join(POSTS_DIR, f"{title}.json")
    with open(post_file, "w", encoding="utf-8") as f:
        json.dump(post_data, f, ensure_ascii=False, indent=4)

    # 이미지를 저장
    for image in images:
        image_path = os.path.join(IMAGE_DIR, image.name)
        with open(image_path, "wb") as f:
            f.write(image.getbuffer())

# 게시물 불러오기 함수 (시간 순으로 정렬)
def load_posts():
    """저장된 게시물들을 불러오는 함수 (시간 순으로 정렬)"""
    posts = []
    for post_file in os.listdir(POSTS_DIR):
        if post_file.endswith(".json"):
            with open(os.path.join(POSTS_DIR, post_file), "r", encoding="utf-8") as f:
                posts.append(json.load(f))
    
    # 날짜를 기준으로 내림차순 정렬 (최신 게시물이 위로 오게)
    posts.sort(key=lambda post: post['date'], reverse=True)
    return posts

# 게시물 삭제 함수
def delete_post(title):
    """게시물을 삭제하는 함수"""
    post_file = os.path.join(POSTS_DIR, f"{title}.json")
    if os.path.exists(post_file):
        os.remove(post_file)
    
    # 게시물과 관련된 이미지도 삭제
    post_images = load_post_images(title)
    for image in post_images:
        image_path = os.path.join(IMAGE_DIR, image)
        if os.path.exists(image_path):
            os.remove(image_path)

# 게시물에 포함된 이미지 불러오기 함수
def load_post_images(title):
    post_file = os.path.join(POSTS_DIR, f"{title}.json")
    if os.path.exists(post_file):
        with open(post_file, "r", encoding="utf-8") as f:
            post = json.load(f)
        return post.get("images", [])
    return []

TIMELINE_FILE = "timeline_events.json"

# 타임라인 이벤트 저장 함수
def save_timeline(events):
    with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)

# 타임라인 이벤트 불러오기 함수
def load_timeline():
    if os.path.exists(TIMELINE_FILE):
        with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []  # 파일이 없을 경우 빈 리스트 반환




# 사이드바 메뉴 생성
st.sidebar.title("우리의 발자취")
menu = st.sidebar.radio("Go to", ["Home", "타임라인", "기념일", "사진첩", "스토리"])

# 사이드바에서 선택된 메뉴에 따라 페이지 상태 업데이트
if menu == "Home":
    st.session_state.page = 'home'
elif menu == "타임라인":
    st.session_state.page = 'timeline'
elif menu == "기념일":
    st.session_state.page = 'anniversary'
elif menu == "사진첩":
    st.session_state.page = 'photo'
elif menu == "스토리":
    st.session_state.page = '게시물'

# 홈 페이지
if st.session_state.page == 'home':
    st.markdown('<h1 class="main-title">Welcome to 민서와 규민\'s Homepage!</h1>', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/800x300.png?text=민서와 규민's+Website", use_column_width=True)

# 타임라인 페이지 (이벤트 보기 및 추가/삭제 가능)
elif st.session_state.page == 'timeline':
    st.header("TimeLine")

    # 타임라인 이벤트 불러오기
    events = load_timeline()

    # 타임라인 이벤트 출력
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    
    for event in events:
        st.markdown(f'''
        <div class="timeline-item">
            <div class="date">{event["date"]}</div>
            <div class="event">{event["event"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 추가 및 삭제 버튼
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("이벤트 추가", key="add_button"):
            st.session_state.timeline_mode = 'add'
            st.rerun()

    with col2:
        if st.button("이벤트 삭제", key="delete_button"):
            st.session_state.timeline_mode = 'delete'
            st.rerun()

    # 이벤트 추가 모드
    if 'timeline_mode' in st.session_state and st.session_state.timeline_mode == 'add':
        st.subheader("새로운 이벤트 추가하기")
        new_event_date = st.date_input("날짜를 선택하세요", datetime.date.today())
        new_event_name = st.text_input("이벤트를 입력하세요")

        if st.button("이벤트 저장", key="save_button"):
            if new_event_name:
                # 새로운 이벤트 추가
                new_event = {"date": new_event_date.isoformat(), "event": new_event_name}
                events.append(new_event)
                events.sort(key=lambda x: x["date"])  # 날짜순 정렬
                save_timeline(events)
                st.success("새로운 이벤트가 추가되었습니다!")
                st.session_state.timeline_mode = None
                st.rerun()
            else:
                st.error("이벤트 이름을 입력하세요.")

        # 취소 버튼
        if st.button("취소", key="cancel_add_button"):
            st.session_state.timeline_mode = None
            st.rerun()

    # 이벤트 삭제 모드
    if 'timeline_mode' in st.session_state and st.session_state.timeline_mode == 'delete':
        st.subheader("이벤트 삭제하기")
        if events:
            delete_event_name = st.selectbox("삭제할 이벤트를 선택하세요", [event["event"] for event in events])

            if st.button("이벤트 삭제", key="confirm_delete_button"):
                events = [event for event in events if event["event"] != delete_event_name]
                save_timeline(events)
                st.success(f"{delete_event_name} 이벤트가 삭제되었습니다!")
                st.session_state.timeline_mode = None
                st.rerun()

        else:
            st.write("삭제할 이벤트가 없습니다.")

        # 취소 버튼
        if st.button("취소", key="cancel_delete_button"):
            st.session_state.timeline_mode = None
            st.rerun()

# 기념일 페이지
elif st.session_state.page == 'anniversary':
    st.title("Anniversary Page")
    
    starting_date = datetime.date(2024, 8, 28)
    minseo_birthday = datetime.date(2003, 10, 7)
    gyumin_birthday = datetime.date(2001, 11, 29)

    today = datetime.date.today()

    days_difference = (today - starting_date).days
    days_difference2 = days_difference + 1
    st.write(f"{starting_date}로부터 {days_difference2}일이 지났습니다 (D+{days_difference2}).")

    def days_until_birthday(birthday):
        next_birthday = birthday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    days_until_minseo_birthday = days_until_birthday(minseo_birthday)
    st.write(f"민서의 생일까지 {days_until_minseo_birthday}일 남았습니다.")
    days_until_gyumin_birthday = days_until_birthday(gyumin_birthday)
    st.write(f"규민의 생일까지 {days_until_gyumin_birthday}일 남았습니다.")

# 사진첩 페이지
elif st.session_state.page == 'photo':
    st.header("Upload a Photo")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_path = os.path.join(IMAGE_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(file_path, use_column_width=True)
        st.success(f"Image saved to {file_path}")

# 게시물 페이지
elif st.session_state.page == '게시물':
    
    if st.session_state.post_page == 'main':
        st.header("게시물 목록")
        st.write("저장된 게시물들을 확인할 수 있습니다.")

        # 저장된 게시물 목록 표시
        posts = load_posts()
        for i, post in enumerate(posts):
            if st.button(post["title"]):  # 버튼을 클릭하면 해당 게시물로 이동
                # 선택된 게시물 정보를 세션에 저장
                st.session_state.selected_post = post  
                st.session_state.post_page = 'detail'  # 세부 페이지로 이동
                st.rerun()  # 즉시 페이지 갱신

        # 게시물 업로드 버튼
        if st.button("게시물 업로드"):
            st.session_state.post_page = 'upload'
            st.rerun()  # 즉시 페이지 갱신

    # 게시물 작성 페이지
    elif st.session_state.post_page == 'upload':
        st.header("게시물 작성하기")

        # 게시물 입력 폼
        post_title = st.text_input("제목을 입력하세요")
        post_date = st.date_input("날짜를 선택하세요", datetime.date.today())
        post_content = st.text_area("내용을 입력하세요")
        post_images = st.file_uploader("사진을 선택하세요", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        if st.button("게시물 저장"):
            if post_title and post_content:
                save_post(post_title, post_date, post_content, post_images)
                st.success("게시물이 성공적으로 저장되었습니다!")
                st.session_state.post_page = 'main'  # 저장 후 다시 메인 페이지로 이동
                st.rerun()  # 즉시 페이지 갱신
            else:
                st.error("제목과 내용을 모두 입력해야 합니다.")

        # 돌아가기 버튼
        if st.button("돌아가기"):
            st.session_state.post_page = 'main'
            st.rerun()  # 즉시 페이지 갱신

    # 게시물 세부 페이지
    elif st.session_state.post_page == 'detail':
        st.header("게시물 상세 보기")

        # 선택된 게시물 로드
        selected_post = st.session_state.selected_post  # 세션에서 선택된 게시물 가져오기

        # 게시물 세부 정보 표시
        st.subheader(selected_post["title"])
        st.write(f"날짜: {selected_post['date']}")
        st.write(selected_post["content"])
        for image in selected_post["images"]:
            image_path = os.path.join(IMAGE_DIR, image)
            st.image(image_path, use_column_width=True)

        # 돌아가기 버튼
        if st.button("돌아가기"):
            st.session_state.post_page = 'main'
            st.rerun()  # 즉시 페이지 갱신

        # 삭제 버튼
        if st.button("게시물 삭제"):
            delete_post(selected_post["title"])  # 게시물 삭제
            st.success("게시물이 성공적으로 삭제되었습니다.")
            st.session_state.post_page = 'main'
            st.rerun()  # 즉시 페이지 갱신


# 푸터
st.markdown('<p class="footer">© 2024 민서와 규민 - All Rights Reserved</p>', unsafe_allow_html=True)
