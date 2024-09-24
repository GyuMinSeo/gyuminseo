import streamlit as st
import os
import json
import datetime
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials, storage

# Streamlit secrets에서 Firebase 설정 정보를 가져옵니다.
firebase_creds = {
    "type": st.secrets["firebase"]["type"],
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
}


# Firebase 초기화가 이미 되었는지 확인
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'minseo-dd5fe.appspot.com'  # 실제 Firebase 프로젝트의 Storage 버킷 이름 입력
    })


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
load_css("style.css")

# Firebase Storage에서 이미지 URL을 가져오는 함수
def get_image_url_from_firebase(image_name):
    client = storage.Client()
    bucket = client.get_bucket('your-bucket-name')  # Firebase Storage 버킷 이름
    blob = bucket.blob(f'uploaded_images/{image_name}')
    
    # 이미지의 다운로드 URL 생성
    url = blob.generate_signed_url(expiration=datetime.timedelta(hours=1))  # 1시간 동안 유효한 URL 생성
    return url

# Firebase Storage에 이미지를 업로드하는 함수 (버킷 이름 명시)
def upload_image_to_firebase(image):
    bucket = firebase_admin.storage.bucket('minseo-dd5fe.appspot.com')  # Firebase Storage 버킷 이름 명시
    blob = bucket.blob(f'uploaded_images/{image.name}')  # 이미지 경로 설정
    
    # 이미지를 Firebase Storage에 업로드
    blob.upload_from_file(image, content_type=image.type)
    
    # 업로드한 이미지의 공개 URL 가져오기
    image_url = blob.generate_signed_url(expiration=datetime.timedelta(hours=1))  # 1시간 동안 유효한 URL 생성
    return image_url



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

# 게시물 저장 함수 수정 (Firestore에 저장, Firebase Storage에 이미지 저장)
def save_post(title, date, content, images, likes=0):
    post_ref = db.collection("posts")
    post_data = {
        "title": title,
        "date": date.isoformat(),
        "content": content,
        "images": [image.name for image in images],  # 이미지는 Firebase Storage에 저장하고 이름만 저장
        "likes": likes
    }
    post_ref.add(post_data)

    # 이미지를 Firebase Storage에 저장
    for image in images:
        upload_image_to_firebase(image)
        
# 게시물 불러오기 함수 수정 (Firestore에서 불러오기)
def load_posts():
    post_ref = db.collection("posts")
    posts = []
    for doc in post_ref.stream():
        posts.append(doc.to_dict())
    posts.sort(key=lambda post: post['date'], reverse=True)
    return posts

# 좋아요 수 업데이트 함수 수정
def update_likes(post_title, new_likes):
    post_ref = db.collection("posts")
    for doc in post_ref.stream():
        if doc.to_dict()["title"] == post_title:
            post_ref.document(doc.id).update({"likes": new_likes})
            break

# Firebase Storage에서 이미지를 삭제하는 함수
def delete_image_from_firebase(image_name):
    client = storage.Client()
    bucket = client.get_bucket('your-bucket-name')  # Firebase Storage 버킷 이름
    blob = bucket.blob(f'uploaded_images/{image_name}')
    blob.delete()

# 게시물 삭제 함수 (Firestore와 Firebase Storage)
def delete_post(title):
    """게시물을 Firestore와 Firebase Storage에서 삭제하는 함수"""
    # Firestore에서 게시물 찾기
    posts_ref = db.collection("posts")
    post_docs = posts_ref.where("title", "==", title).stream()

    # 해당 게시물을 삭제
    for doc in post_docs:
        post_data = doc.to_dict()
        # Firestore에서 문서 삭제
        doc.reference.delete()

        # 게시물에 포함된 이미지 삭제
        post_images = post_data.get("images", [])
        for image_name in post_images:
            delete_image_from_firebase(image_name)

# 댓글 저장 함수 (Firestore에 저장)
def save_comment(post_title, comment):
    post_ref = db.collection("posts").where("title", "==", post_title).stream()
    
    for post in post_ref:
        comment_data = {
            "comment": comment,
            "date": datetime.datetime.now().isoformat()
        }
        # Firestore에서 해당 게시물의 서브컬렉션 'comments'에 댓글 저장
        post.reference.collection("comments").add(comment_data)

# 댓글 불러오기 함수 (Firestore에서 불러오기)
def load_comments(post_title):
    post_ref = db.collection("posts").where("title", "==", post_title).stream()
    
    comments = []
    for post in post_ref:
        comments_ref = post.reference.collection("comments").stream()
        for comment in comments_ref:
            comments.append(comment.to_dict())
    return comments

# 타임라인 이벤트 저장 함수 (Firestore에 저장)
def save_timeline(events):
    timeline_ref = db.collection("timeline")
    
    # 모든 이벤트를 Firestore에 저장 (덮어쓰기를 방지하려면 고유한 ID를 사용해야 함)
    for event in events:
        timeline_ref.add(event)

# 타임라인 이벤트 불러오기 함수 (Firestore에서 불러오기)
def load_timeline():
    timeline_ref = db.collection("timeline")
    events = []
    for doc in timeline_ref.stream():
        events.append(doc.to_dict())
    
    return events

# 다이어리 저장 함수 (Firestore에 저장)
def save_diary(title, date, content):
    """다이어리를 Firestore에 저장하는 함수"""
    diary_ref = db.collection("diaries")
    diary_data = {
        "title": title,
        "date": date.isoformat(),
        "content": content
    }
    diary_ref.add(diary_data)

# 다이어리 불러오기 함수 (Firestore에서 불러오기)
def load_diaries():
    """저장된 다이어리들을 Firestore에서 불러오는 함수 (시간 순으로 정렬)"""
    diary_ref = db.collection("diaries")
    diaries = []
    for doc in diary_ref.stream():
        diaries.append(doc.to_dict())
    
    # 날짜를 기준으로 내림차순 정렬 (최신 다이어리가 위로 오게)
    diaries.sort(key=lambda diary: diary['date'], reverse=True)
    return diaries

# 다이어리 삭제 함수 (Firestore에서 삭제)
def delete_diary(title, date):
    """다이어리를 Firestore에서 삭제하는 함수"""
    diary_ref = db.collection("diaries")
    
    # Firestore에서 해당 다이어리 문서를 찾아 삭제 (date는 이미 문자열로 저장된 상태로 가정)
    diary_docs = diary_ref.where("title", "==", title).where("date", "==", date).stream()
    for doc in diary_docs:
        doc.reference.delete()

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

st.markdown('''
<div class="stars"></div>  <!-- 별 배경 추가 -->
<div class="hearts-container">
    <div class="heart"></div>
    <div class="heart"></div>
    <div class="heart"></div>
    <div class="heart"></div>
    <div class="heart"></div>
</div>
''', unsafe_allow_html=True)


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
    st.markdown(f'<p class="anniversary-counter">{starting_date}로부터 {days_difference2}일이 지났습니다 (D+{days_difference2}).</p>', unsafe_allow_html=True)

    def days_until_birthday(birthday):
        next_birthday = birthday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    days_until_minseo_birthday = days_until_birthday(minseo_birthday)
    st.markdown(f'<p class="anniversary-description">민서의 생일까지 {days_until_minseo_birthday}일 남았습니다.</p>', unsafe_allow_html=True)
    days_until_gyumin_birthday = days_until_birthday(gyumin_birthday)
    st.markdown(f'<p class="anniversary-description">규민의 생일까지 {days_until_gyumin_birthday}일 남았습니다.</p>', unsafe_allow_html=True)

# 사진첩 페이지 (Firebase Storage에 이미지를 업로드하고 표시)
elif st.session_state.page == 'photo':
    st.header("Upload a Photo")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Firebase Storage에 이미지를 업로드하고 URL을 가져옴
        image_url = upload_image_to_firebase(uploaded_file)
        
        # 이미지를 화면에 표시
        st.image(image_url, use_column_width=True, caption="Uploaded Image")
        st.success(f"Image successfully uploaded!")

# 게시물 페이지
elif st.session_state.page == '게시물':
    
    # 게시물 목록에서 버튼에 고유한 키를 부여하여 중복 오류 해결
    if st.session_state.post_page == 'main':
        st.header("게시물 목록")
        st.write("저장된 게시물들을 확인할 수 있습니다.")

        # 저장된 게시물 목록 표시
        posts = load_posts()
        for i, post in enumerate(posts):
            # 각 버튼에 고유한 키를 부여 (제목과 인덱스를 결합)
            if st.button(post["title"], key=f"post_button_{i}"):  # 버튼을 클릭하면 해당 게시물로 이동
                # 선택된 게시물 정보를 세션에 저장
                st.session_state.selected_post = post  
                st.session_state.post_page = 'detail'  # 세부 페이지로 이동
                st.rerun()  # 즉시 페이지 갱신

        # 게시물 목록 아래에 게시물 업로드 버튼 추가
        if st.button("게시물 업로드", key="upload_post_button"):
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

    # 게시물 세부 페이지 (수정된 코드)
    elif st.session_state.post_page == 'detail':
        st.header("게시물 상세 보기")

        #  선택된 게시물 로드
        selected_post = st.session_state.selected_post  # 세션에서 선택된 게시물 가져오기

        # 게시물 세부 정보 표시 (Firebase Storage에서 이미지 URL을 불러옴)
        st.markdown(f'<h2 class="post-title">{selected_post["title"]}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p class="post-date">날짜: {selected_post["date"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="post-content">{selected_post["content"]}</div>', unsafe_allow_html=True)
    
        # Firebase Storage에서 이미지를 가져와 표시
        for image in selected_post["images"]:
            image_url = get_image_url_from_firebase(image)  # 이미지 URL 가져오기
            st.image(image_url, use_column_width=True, caption=image)  # Streamlit에서 이미지 표시

        # 좋아요 버튼 및 좋아요 수 표시
        st.markdown(f"<p>좋아요: {selected_post.get('likes', 0)}</p>", unsafe_allow_html=True)
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
            st.markdown(f'<div class="comment">{comment_data["date"]}: {comment_data["comment"]}</div>', unsafe_allow_html=True)

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
            st.rerun()



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
