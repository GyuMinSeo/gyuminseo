import streamlit as st
import os
import json
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화가 이미 되었는지 확인
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/gyuminseo/gyuminseo/minseo-dd5fe-firebase-adminsdk-1vays-3faccecc75.json")
    firebase_admin.initialize_app(cred)

# Firestore 클라이언트 생성
db = firestore.client()



# 페이지 제목과 설명
st.set_page_config(page_title="민서와 규민's Lovely Homepage", layout="wide")

# 페이지 상태 초기화 (최상단에 위치)
if 'page' not in st.session_state:
    st.session_state.page = 'home'  # 기본 페이지는 'home'으로 설정
if 'post_page' not in st.session_state:
    st.session_state.post_page = 'main'  # 게시물 페이지 기본값은 'main'
if 'wishlist_page' not in st.session_state:
    st.session_state.wishlist_page = 'main'  # 위시리스트 페이지 기본값은 'main'

# CSS 파일 불러오기 함수
def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# CSS 파일 불러오기
load_css("C:/gyuminseo/gyuminseo/style.css")

# 위시리스트 저장 파일 경로
WISHLIST_FILE = "wishlist_items.json"
# 위시리스트 저장 함수 수정 (Firestore에 저장)
def save_wishlist_item(item, completed=False):
    wishlist_ref = db.collection("wishlist")
    wishlist_ref.add({"item": item, "completed": completed})

# 위시리스트 불러오기 함수 수정 (Firestore에서 불러오기)
def load_wishlist_items():
    wishlist_ref = db.collection("wishlist")
    wishlist_items = []
    for doc in wishlist_ref.stream():
        wishlist_items.append(doc.to_dict())
    return wishlist_items

# 위시리스트 상태 변경 함수 수정 (Firestore에서 업데이트)
def toggle_wishlist_item_status(item_name):
    wishlist_ref = db.collection("wishlist")
    for doc in wishlist_ref.stream():
        if doc.to_dict()["item"] == item_name:
            new_status = not doc.to_dict()["completed"]
            wishlist_ref.document(doc.id).update({"completed": new_status})
            break

# 위시리스트 삭제 함수 수정 (Firestore에서 삭제)
def delete_wishlist_item(item_name):
    wishlist_ref = db.collection("wishlist")
    for doc in wishlist_ref.stream():
        if doc.to_dict()["item"] == item_name:
            wishlist_ref.document(doc.id).delete()
            break

# 이미지 및 게시물 저장 디렉토리 설정
POSTS_DIR = "posts"
os.makedirs(POSTS_DIR, exist_ok=True)
IMAGE_DIR = "uploaded_images"
os.makedirs(IMAGE_DIR, exist_ok=True)
# 게시물 저장 함수에 좋아요 수 추가
def save_post(title, date, content, images, likes=0):
    """게시물을 저장하는 함수"""
    post_data = {
        "title": title,
        "date": date.isoformat(),
        "content": content,
        "images": [image.name for image in images],
        "likes": likes  # 좋아요 수 추가
    }

    post_file = os.path.join(POSTS_DIR, f"{title}.json")
    with open(post_file, "w", encoding="utf-8") as f:
        json.dump(post_data, f, ensure_ascii=False, indent=4)

    # 이미지를 저장
    for image in images:
        image_path = os.path.join(IMAGE_DIR, image.name)
        with open(image_path, "wb") as f:
            f.write(image.getbuffer())

# 좋아요 저장 함수
def update_likes(post_title, new_likes):
    post_file = os.path.join(POSTS_DIR, f"{post_title}.json")
    if os.path.exists(post_file):
        with open(post_file, "r", encoding="utf-8") as f:
            post = json.load(f)
        post['likes'] = new_likes
        with open(post_file, "w", encoding="utf-8") as f:
            json.dump(post, f, ensure_ascii=False, indent=4)


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

# 댓글 저장 파일 경로 설정
COMMENTS_DIR = "comments"
os.makedirs(COMMENTS_DIR, exist_ok=True)

# 댓글 저장 함수
def save_comment(post_title, comment):
    comments_file = os.path.join(COMMENTS_DIR, f"{post_title}_comments.json")
    comments = []
    if os.path.exists(comments_file):
        with open(comments_file, "r", encoding="utf-8") as f:
            comments = json.load(f)
    comments.append({"comment": comment, "date": datetime.datetime.now().isoformat()})
    with open(comments_file, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)

# 댓글 불러오기 함수
def load_comments(post_title):
    comments_file = os.path.join(COMMENTS_DIR, f"{post_title}_comments.json")
    if os.path.exists(comments_file):
        with open(comments_file, "r", encoding="utf-8") as f:
            return json.load(f)
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



# 다이어리 저장 파일 경로 설정
DIARY_DIR = "diaries"
os.makedirs(DIARY_DIR, exist_ok=True)

# 다이어리 저장 함수
def save_diary(title, date, content):
    """다이어리를 저장하는 함수"""
    diary_data = {
        "title": title,
        "date": date.isoformat(),
        "content": content
    }
    diary_file = os.path.join(DIARY_DIR, f"{date.isoformat()}_{title}.json")
    with open(diary_file, "w", encoding="utf-8") as f:
        json.dump(diary_data, f, ensure_ascii=False, indent=4)

# 다이어리 불러오기 함수
def load_diaries():
    """저장된 다이어리들을 불러오는 함수 (시간 순으로 정렬)"""
    diaries = []
    for diary_file in os.listdir(DIARY_DIR):
        if diary_file.endswith(".json"):
            with open(os.path.join(DIARY_DIR, diary_file), "r", encoding="utf-8") as f:
                diaries.append(json.load(f))
    
    # 날짜를 기준으로 내림차순 정렬 (최신 다이어리가 위로 오게)
    diaries.sort(key=lambda diary: diary['date'], reverse=True)
    return diaries

# 다이어리 삭제 함수
def delete_diary(title, date):
    """다이어리를 삭제하는 함수"""
    diary_file = os.path.join(DIARY_DIR, f"{date}_{title}.json")
    if os.path.exists(diary_file):
        os.remove(diary_file)




# 사이드바 메뉴 생성
st.sidebar.title("우리의 발자취")
menu = st.sidebar.radio("Go to", ["Home", "타임라인", "기념일", "사진첩", "스토리", "다이어리", "위시리스트"])

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
elif menu == "다이어리":
    st.session_state.page = 'diary'
elif menu == "위시리스트":
    st.session_state.page = 'wishlist'

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

    # 게시물 세부 페이지 수정
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

        # 좋아요 버튼 및 좋아요 수 표시
        st.write(f"좋아요: {selected_post.get('likes', 0)}")
        if st.button("좋아요"):
            new_likes = selected_post.get('likes', 0) + 1
            update_likes(selected_post["title"], new_likes)
            st.success("좋아요를 눌렀습니다.")
            st.session_state.selected_post['likes'] = new_likes
            st.rerun()  # 즉시 페이지 갱신

        # 댓글 입력 및 저장
        st.subheader("댓글")
        comment = st.text_area("댓글을 입력하세요")
        if st.button("댓글 달기"):
            if comment:
                save_comment(selected_post["title"], comment)
                st.success("댓글이 저장되었습니다.")
                st.rerun()

        # 저장된 댓글 불러오기
        comments = load_comments(selected_post["title"])
        for comment_data in comments:
            st.write(f"{comment_data['date']}: {comment_data['comment']}")

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

# 위시리스트 항목 출력 부분 수정
elif st.session_state.page == 'wishlist':
    if st.session_state.wishlist_page == 'main':
        st.header("Wishlist")
        
        # 기존 위시리스트 항목 보여주기
        st.subheader("위시리스트")
        wishlist_items = load_wishlist_items()
        
        if wishlist_items:
            for item in wishlist_items:
                if isinstance(item, dict):
                    item_display = f"~~{item['item']}~~" if item["completed"] else item["item"]
                    
                    # 세 개의 열을 생성하여 아이템 이름, 완료 버튼, 삭제 버튼 배치
                    col1, col2, col3 = st.columns([6, 2, 2])  # 각 열의 비율을 6:2:2로 설정
                    
                    with col1:
                        st.markdown(f"{item_display}", unsafe_allow_html=True)  # 아이템 표시
                        
                    with col2:
                        # 완료 상태 변경 버튼
                        if st.button(f"완료", key=f"complete_{item['item']}"):
                            toggle_wishlist_item_status(item["item"])  # 완료 상태 전환
                            st.success(f"'{item['item']}' 상태가 변경되었습니다.")
                            st.rerun()  # 즉시 페이지 갱신

                    with col3:
                        # 삭제 버튼 (아이템의 'item' 값으로 삭제)
                        if st.button(f"삭제", key=f"delete_{item['item']}"):
                            delete_wishlist_item(item["item"])  # item 대신 item["item"]으로 삭제
                            st.success(f"'{item['item']}'이(가) 삭제되었습니다.")
                            st.rerun()  # 즉시 페이지 갱신
                else:
                    st.error(f"잘못된 항목 형식: {item}")
        else:
            st.write("위시리스트가 비어 있습니다.")
        
        # 위시리스트 추가 버튼
        if st.button("위시리스트 추가"):
            st.session_state.wishlist_page = 'add'  # 'add' 페이지로 이동
            st.rerun()  # 즉시 페이지 갱신

    # 위시리스트 추가 페이지
    elif st.session_state.wishlist_page == 'add':
        st.header("위시리스트 항목 추가하기")
        
        wishlist_item = st.text_input("위시리스트에 추가할 아이템을 입력하세요")
        
        if st.button("추가"):
            if wishlist_item:
                save_wishlist_item(wishlist_item)  # 추가 시 완료 상태는 False로 저장
                st.success(f"'{wishlist_item}'이(가) 위시리스트에 추가되었습니다!")
                st.session_state.wishlist_page = 'main'  # 추가 후 다시 메인 페이지로 이동
                st.rerun()  # 즉시 페이지 갱신
            else:
                st.error("아이템 이름을 입력하세요.")

        # 취소 버튼
        if st.button("취소"):
            st.session_state.wishlist_page = 'main'
            st.rerun()  # 즉시 페이지 갱신








# 다이어리 페이지 구현
elif st.session_state.page == 'diary':
    st.header("Diary Page")

    # 저장된 다이어리 목록 보기
    diaries = load_diaries()
    
    if st.session_state.get('diary_mode') == 'main' or 'diary_mode' not in st.session_state:
        st.session_state.diary_mode = 'main'

    # 다이어리 메인 페이지 (목록 보기)
    if st.session_state.diary_mode == 'main':
        st.subheader("저장된 다이어리 목록")

        if diaries:
            for diary in diaries:
                with st.expander(f"{diary['title']}({diary['date']})"):
                    st.write(diary["content"])
                    if st.button(f"삭제", key=f"delete_{diary['date']}_{diary['title']}"):
                        delete_diary(diary['title'], diary['date'])
                        st.success(f"'{diary['title']}'이(가) 삭제되었습니다.")
                        st.rerun()
        else:
            st.write("저장된 다이어리가 없습니다.")
        
        # 다이어리 추가 버튼
        if st.button("다이어리 추가하기"):
            st.session_state.diary_mode = 'add'
            st.rerun()

    # 다이어리 작성 페이지
    elif st.session_state.diary_mode == 'add':
        st.subheader("새로운 다이어리 작성하기")
        
        diary_title = st.text_input("제목을 입력하세요")
        diary_date = st.date_input("날짜를 선택하세요", datetime.date.today())
        diary_content = st.text_area("내용을 입력하세요")

        if st.button("저장하기"):
            if diary_title and diary_content:
                save_diary(diary_title, diary_date, diary_content)
                st.success("다이어리가 저장되었습니다!")
                st.session_state.diary_mode = 'main'  # 저장 후 메인 페이지로 이동
                st.rerun()
            else:
                st.error("제목과 내용을 모두 입력해야 합니다.")

        if st.button("취소"):
            st.session_state.diary_mode = 'main'
            st.rerun()



# 푸터
st.markdown('<p class="footer">© 2024 민서와 규민 - All Rights Reserved</p>', unsafe_allow_html=True)
