import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from youtube_api import (
    get_video_id,
    get_video_info,
    get_comments
)

from sentiment import analyze_sentiment
from wordcloud_util import create_wordcloud

# -----------------------------------
# 페이지 설정
# -----------------------------------

st.set_page_config(
    page_title="YouTube 댓글 분석기",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 YouTube 댓글 분석기")
st.caption("YouTube Data API를 이용하여 댓글을 분석합니다.")

# -----------------------------------
# 사이드바
# -----------------------------------

with st.sidebar:

    st.header("설정")

    api_key = st.text_input(
        "YouTube API Key",
        type="password"
    )

    video_url = st.text_input(
        "YouTube URL"
    )

    max_comments = st.slider(
        "수집할 댓글 수",
        min_value=100,
        max_value=5000,
        value=500,
        step=100
    )

    include_replies = st.checkbox(
        "답글 포함",
        value=False
    )

    analyze_btn = st.button(
        "댓글 분석 시작",
        use_container_width=True
    )

# -----------------------------------
# 안내
# -----------------------------------

if not analyze_btn:

    st.info("""
    사용 방법

    1. YouTube API Key 입력

    2. 영상 URL 입력

    3. 댓글 개수 선택

    4. 댓글 분석 시작 클릭
    """)

    st.stop()

# -----------------------------------
# 입력 확인
# -----------------------------------

if api_key == "":

    st.error("API Key를 입력하세요.")
    st.stop()

if video_url == "":

    st.error("YouTube URL을 입력하세요.")
    st.stop()

# -----------------------------------
# Video ID
# -----------------------------------

video_id = get_video_id(video_url)

if video_id is None:

    st.error("유효한 YouTube URL이 아닙니다.")
    st.stop()

# -----------------------------------
# 영상 출력
# -----------------------------------

st.video(video_url)

# -----------------------------------
# 영상 정보
# -----------------------------------

with st.spinner("영상 정보를 불러오는 중..."):

    video = get_video_info(
        api_key,
        video_id
    )

if video is None:

    st.error("영상 정보를 가져오지 못했습니다.")
    st.stop()

st.header(video["title"])

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "조회수",
    f"{video['viewCount']:,}"
)

col2.metric(
    "좋아요",
    f"{video['likeCount']:,}"
)

col3.metric(
    "댓글수",
    f"{video['commentCount']:,}"
)

col4.metric(
    "게시일",
    video["publishedAt"][:10]
)

st.divider()

# -----------------------------------
# 댓글 수집
# -----------------------------------

with st.spinner("댓글을 수집하는 중입니다..."):

    comments = get_comments(
        api_key=api_key,
        video_id=video_id,
        max_comments=max_comments,
        include_replies=include_replies
    )

if len(comments) == 0:

    st.warning("댓글이 없습니다.")
    st.stop()

df = pd.DataFrame(comments)

st.success(f"{len(df):,}개의 댓글을 수집했습니다.")

# -----------------------------------
# 데이터 전처리
# -----------------------------------

df["publishedAt"] = pd.to_datetime(df["publishedAt"])

df["date"] = df["publishedAt"].dt.date

df["hour"] = df["publishedAt"].dt.hour

df["likeCount"] = df["likeCount"].fillna(0)

df["text"] = df["text"].fillna("")

st.divider()

# -----------------------------------
# 감성분석
# -----------------------------------

with st.spinner("감성 분석 중..."):

    df["sentiment"] = analyze_sentiment(
        df["text"]
    )

# -----------------------------------
# 레이아웃
# -----------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 댓글 추이",
    "😊 감성 분석",
    "☁️ 워드클라우드",
    "💬 댓글",
    "📥 다운로드"
])

with tab1:

    st.subheader("📈 시간대별 댓글 작성 추이")

    hour_df = (
        df.groupby("hour")
        .size()
        .reset_index(name="count")
    )

    hour_df = hour_df.set_index("hour").reindex(range(24), fill_value=0).reset_index()

    fig_hour = px.line(
        hour_df,
        x="hour",
        y="count",
        markers=True,
        title="시간대별 댓글 수"
    )

    fig_hour.update_layout(
        xaxis_title="시간",
        yaxis_title="댓글 수",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_hour,
        use_container_width=True
    )

    st.divider()

    st.subheader("📅 날짜별 댓글 추이")

    day_df = (
        df.groupby("date")
        .size()
        .reset_index(name="count")
    )

    fig_day = px.bar(
        day_df,
        x="date",
        y="count",
        color="count",
        title="날짜별 댓글 수"
    )

    fig_day.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_day,
        use_container_width=True
    )

    st.divider()

    st.subheader("❤️ 좋아요 많은 댓글 TOP20")

    top_like = (
        df.sort_values(
            "likeCount",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        top_like[
            [
                "author",
                "likeCount",
                "publishedAt",
                "text"
            ]
        ],
        use_container_width=True,
        height=500
    )


# ============================================================
# TAB2 : 감성분석
# ============================================================

with tab2:

    st.subheader("😊 댓글 감성 분석")

    sentiment_count = (
        df["sentiment"]
        .value_counts()
        .reset_index()
    )

    sentiment_count.columns = [
        "sentiment",
        "count"
    ]

    col1, col2 = st.columns(2)

    with col1:

        fig_pie = px.pie(
            sentiment_count,
            values="count",
            names="sentiment",
            hole=0.45,
            color="sentiment",
            color_discrete_map={
                "긍정":"green",
                "중립":"gray",
                "부정":"red"
            }
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    with col2:

        fig_bar = px.bar(
            sentiment_count,
            x="sentiment",
            y="count",
            color="sentiment",
            color_discrete_map={
                "긍정":"green",
                "중립":"gray",
                "부정":"red"
            }
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    st.divider()

    st.subheader("감성 비율")

    total = len(df)

    positive = len(
        df[df.sentiment=="긍정"]
    )

    neutral = len(
        df[df.sentiment=="중립"]
    )

    negative = len(
        df[df.sentiment=="부정"]
    )

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "😊 긍정",
        f"{positive:,}",
        f"{positive/total*100:.1f}%"
    )

    c2.metric(
        "😐 중립",
        f"{neutral:,}",
        f"{neutral/total*100:.1f}%"
    )

    c3.metric(
        "😡 부정",
        f"{negative:,}",
        f"{negative/total*100:.1f}%"
    )


# ============================================================
# 키워드 TOP20
# ============================================================

    st.divider()

    st.subheader("🔥 많이 사용된 키워드")

    try:

        from collections import Counter
        from kiwipiepy import Kiwi

        kiwi = Kiwi()

        nouns = []

        for text in df["text"]:

            try:

                result = kiwi.tokenize(text)

                nouns.extend(
                    [
                        token.form
                        for token in result
                        if token.tag.startswith("N")
                        and len(token.form)>=2
                    ]
                )

            except:

                pass

        stopwords = {

            "영상",
            "진짜",
            "오늘",
            "그냥",
            "정말",
            "너무",
            "이번",
            "ㅋㅋ",
            "ㅎㅎ",
            "사람",
            "생각",
            "이거",
            "저거"
        }

        nouns = [
            n
            for n in nouns
            if n not in stopwords
        ]

        top_words = Counter(
            nouns
        ).most_common(20)

        keyword_df = pd.DataFrame(
            top_words,
            columns=[
                "키워드",
                "빈도"
            ]
        )

        fig_keyword = px.bar(
            keyword_df,
            x="빈도",
            y="키워드",
            orientation="h",
            color="빈도"
        )

        st.plotly_chart(
            fig_keyword,
            use_container_width=True
        )

    except Exception as e:

        st.warning(e)

  with tab3:

    st.subheader("☁️ 한글 워드클라우드")

    try:

        wc_image = create_wordcloud(df["text"])

        st.image(
            wc_image,
            use_container_width=True
        )

    except Exception as e:

        st.error(f"워드클라우드 생성 실패 : {e}")

    st.divider()

    st.subheader("댓글 길이 분포")

    df["length"] = df["text"].str.len()

    fig = px.histogram(
        df,
        x="length",
        nbins=40,
        color_discrete_sequence=["royalblue"]
    )

    fig.update_layout(
        xaxis_title="댓글 길이",
        yaxis_title="개수",
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB4 : 댓글 보기
# ============================================================

with tab4:

    st.subheader("💬 댓글 검색")

    keyword = st.text_input(
        "검색어 입력"
    )

    show_df = df.copy()

    if keyword:

        show_df = show_df[
            show_df["text"].str.contains(
                keyword,
                case=False,
                na=False
            )
        ]

    st.write(f"검색 결과 : {len(show_df):,}개")

    st.dataframe(
        show_df[
            [
                "author",
                "publishedAt",
                "likeCount",
                "sentiment",
                "text"
            ]
        ],
        use_container_width=True,
        height=600
    )


# ============================================================
# TAB5 : 다운로드
# ============================================================

with tab5:

    st.subheader("📥 데이터 다운로드")

    csv = show_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "CSV 다운로드",
        data=csv,
        file_name="youtube_comments.csv",
        mime="text/csv",
        use_container_width=True
    )

    import io

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        show_df.to_excel(
            writer,
            index=False,
            sheet_name="Comments"
        )

    st.download_button(
        "Excel 다운로드",
        data=output.getvalue(),
        file_name="youtube_comments.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    st.divider()

    st.subheader("📊 분석 요약")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "총 댓글",
            f"{len(df):,}"
        )

        st.metric(
            "평균 좋아요",
            f"{df['likeCount'].mean():.2f}"
        )

        st.metric(
            "평균 댓글 길이",
            f"{df['length'].mean():.1f}"
        )

    with c2:

        st.metric(
            "최대 좋아요",
            int(df["likeCount"].max())
        )

        st.metric(
            "최장 댓글",
            int(df["length"].max())
        )

        st.metric(
            "작성자 수",
            df["author"].nunique()
        )

    st.divider()

    st.success("✅ 분석이 완료되었습니다.")

import re
import pandas as pd


# -------------------------------------------------------
# 긍정 단어 사전
# -------------------------------------------------------

POSITIVE_WORDS = [

    "좋다",
    "좋아요",
    "최고",
    "대박",
    "멋지다",
    "멋있다",
    "재미있다",
    "재밌다",
    "감동",
    "행복",
    "사랑",
    "응원",
    "추천",
    "완벽",
    "훌륭",
    "잘한다",
    "잘해",
    "역시",
    "굿",
    "짱",
    "감사",
    "고맙",
    "웃기다",
    "웃겨",
    "신난다",
    "놀랍다",
    "대단",
    "예쁘다",
    "귀엽다",
    "좋은",
    "최고네요"

]


# -------------------------------------------------------
# 부정 단어 사전
# -------------------------------------------------------

NEGATIVE_WORDS = [

    "싫다",
    "별로",
    "최악",
    "나쁘다",
    "짜증",
    "화난다",
    "화나요",
    "실망",
    "실망이다",
    "재미없다",
    "노잼",
    "지루",
    "답답",
    "문제",
    "쓰레기",
    "망했다",
    "못한다",
    "이상하다",
    "별루",
    "싫어요",
    "불편",
    "비판",
    "욕",
    "최악이다"

]


# -------------------------------------------------------
# 이모지 및 특수문자 정리
# -------------------------------------------------------

def clean_text(text):

    if not isinstance(text, str):

        return ""

    text = re.sub(
        r"http\S+",
        "",
        text
    )

    text = re.sub(
        r"[^가-힣a-zA-Z0-9\s]",
        "",
        text
    )

    return text.lower()



# -------------------------------------------------------
# 단일 댓글 분석
# -------------------------------------------------------

def classify_sentiment(text):

    text = clean_text(text)

    if text == "":

        return "중립"


    positive = 0
    negative = 0


    for word in POSITIVE_WORDS:

        if word in text:

            positive += 1


    for word in NEGATIVE_WORDS:

        if word in text:

            negative += 1



    if positive > negative:

        return "긍정"


    elif negative > positive:

        return "부정"


    else:

        return "중립"



# -------------------------------------------------------
# DataFrame 컬럼 분석
# -------------------------------------------------------

def analyze_sentiment(text_series):

    """
    pandas Series 입력

    return:
    감성 결과 Series
    """

    results = []


    for text in text_series:

        results.append(
            classify_sentiment(text)
        )


    return pd.Series(
        results,
        index=text_series.index
    )



# -------------------------------------------------------
# 감성 점수 계산
# -------------------------------------------------------

def sentiment_score(text):

    """
    -1 부정
     0 중립
     1 긍정
    """

    result = classify_sentiment(text)


    if result == "긍정":

        return 1


    elif result == "부정":

        return -1


    return 0



# -------------------------------------------------------
# 통계 함수
# -------------------------------------------------------

def sentiment_summary(series):

    total = len(series)

    positive = (
        series == "긍정"
    ).sum()

    negative = (
        series == "부정"
    ).sum()

    neutral = (
        series == "중립"
    ).sum()


    return {

        "total": total,

        "positive": positive,

        "negative": negative,

        "neutral": neutral,

        "positive_rate":
            round(
                positive / total * 100,
                2
            )
            if total else 0,

        "negative_rate":
            round(
                negative / total * 100,
                2
            )
            if total else 0

    }



# -------------------------------------------------------
# 테스트
# -------------------------------------------------------

if __name__ == "__main__":


    test_comments = [

        "정말 최고입니다 너무 재미있어요",

        "별로네요 재미 없습니다",

        "그냥 볼만합니다"

    ]


    for comment in test_comments:

        print(
            comment,
            "=>",
            classify_sentiment(comment)
        )

import os
import re
from collections import Counter

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from kiwipiepy import Kiwi


# -------------------------------------------------------
# 한글 폰트 경로
# -------------------------------------------------------

FONT_PATH = os.path.join(
    "fonts",
    "NanumGothic.ttf"
)



# -------------------------------------------------------
# 불용어
# -------------------------------------------------------

STOPWORDS = {

    "영상",
    "댓글",
    "사람",
    "생각",
    "진짜",
    "정말",
    "너무",
    "오늘",
    "이번",
    "그냥",
    "내용",
    "부분",
    "때문",
    "정도",
    "하나",
    "가지",
    "모습",
    "느낌",
    "ㅋㅋ",
    "ㅎㅎ",
    "ㅠㅠ",
    "입니다",
    "합니다",
    "하세요",
    "있는",
    "없는",
    "하는",
    "되는",
    "같은",
    "제가",
    "저는",
    "여러분"

}



# -------------------------------------------------------
# 텍스트 정리
# -------------------------------------------------------

def clean_text(text):

    if not isinstance(text, str):

        return ""

    text = re.sub(
        r"http\S+",
        "",
        text
    )

    text = re.sub(
        r"[^가-힣\s]",
        "",
        text
    )

    return text



# -------------------------------------------------------
# 형태소 분석
# -------------------------------------------------------

def extract_keywords(
        texts,
        min_length=2
):

    kiwi = Kiwi()

    nouns = []


    for text in texts:

        text = clean_text(text)

        if text == "":

            continue


        try:

            tokens = kiwi.tokenize(text)


            for token in tokens:

                # 명사(NNG,NAG 등)
                if token.tag.startswith("N"):

                    word = token.form


                    if len(word) >= min_length:

                        if word not in STOPWORDS:

                            nouns.append(word)


        except Exception:

            continue


    return nouns



# -------------------------------------------------------
# 빈도 계산
# -------------------------------------------------------

def get_word_frequency(
        texts,
        top_n=100
):

    words = extract_keywords(
        texts
    )

    counter = Counter(words)


    return counter.most_common(top_n)



# -------------------------------------------------------
# 워드클라우드 생성
# -------------------------------------------------------

def create_wordcloud(
        texts,
        width=1000,
        height=600
):


    frequencies = dict(
        get_word_frequency(
            texts
        )
    )


    if len(frequencies) == 0:

        raise ValueError(
            "분석 가능한 단어가 없습니다."
        )


    if not os.path.exists(FONT_PATH):

        raise FileNotFoundError(
            "fonts/NanumGothic.ttf 파일이 필요합니다."
        )


    wc = WordCloud(

        font_path=FONT_PATH,

        width=width,

        height=height,

        background_color="white",

        max_words=100,

        colormap="viridis",

        prefer_horizontal=0.9

    )


    wc.generate_from_frequencies(
        frequencies
    )


    fig, ax = plt.subplots(
        figsize=(12,7)
    )


    ax.imshow(
        wc,
        interpolation="bilinear"
    )


    ax.axis(
        "off"
    )


    return fig



# -------------------------------------------------------
# TOP 키워드 반환
# -------------------------------------------------------

def get_top_keywords(
        texts,
        count=20
):

    return get_word_frequency(
        texts,
        top_n=count
    )



# -------------------------------------------------------
# 테스트
# -------------------------------------------------------

if __name__ == "__main__":


    sample = [

        "정말 재미있는 영상입니다",

        "최고의 콘텐츠 감사합니다",

        "영상 내용이 너무 좋아요",

        "다음 영상도 기대합니다"

    ]


    print(
        get_top_keywords(
            sample
        )
    )


    image = create_wordcloud(
        sample
    )


    plt.show()

import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# -------------------------------------------------------
# YouTube Service
# -------------------------------------------------------

def get_service(api_key: str):
    """
    YouTube API 서비스 생성
    """

    return build(
        "youtube",
        "v3",
        developerKey=api_key,
        cache_discovery=False
    )


# -------------------------------------------------------
# Video ID 추출
# -------------------------------------------------------

def get_video_id(url: str):
    """
    URL에서 Video ID 추출
    """

    patterns = [

        r"v=([a-zA-Z0-9_-]{11})",

        r"youtu\.be\/([a-zA-Z0-9_-]{11})",

        r"shorts\/([a-zA-Z0-9_-]{11})",

        r"embed\/([a-zA-Z0-9_-]{11})"
    ]

    for pattern in patterns:

        match = re.search(pattern, url)

        if match:

            return match.group(1)

    return None


# -------------------------------------------------------
# 영상 정보
# -------------------------------------------------------

def get_video_info(api_key, video_id):

    youtube = get_service(api_key)

    try:

        request = youtube.videos().list(

            part="snippet,statistics",

            id=video_id

        )

        response = request.execute()

        if len(response["items"]) == 0:

            return None

        item = response["items"][0]

        snippet = item["snippet"]

        stats = item["statistics"]

        return {

            "title":

                snippet.get("title", ""),

            "channel":

                snippet.get("channelTitle", ""),

            "publishedAt":

                snippet.get("publishedAt", ""),

            "viewCount":

                int(stats.get("viewCount", 0)),

            "likeCount":

                int(stats.get("likeCount", 0)),

            "commentCount":

                int(stats.get("commentCount", 0))

        }

    except HttpError:

        return None


# -------------------------------------------------------
# 댓글 수집
# -------------------------------------------------------

def get_comments(

        api_key,

        video_id,

        max_comments=500,

        include_replies=False

):

    youtube = get_service(api_key)

    comments = []

    next_page = None

    while True:

        if len(comments) >= max_comments:

            break

        try:

            request = youtube.commentThreads().list(

                part="snippet,replies",

                videoId=video_id,

                maxResults=100,

                pageToken=next_page,

                textFormat="plainText",

                order="time"

            )

            response = request.execute()

        except HttpError:

            break

        items = response.get("items", [])

        if len(items) == 0:

            break

        for item in items:

            top = item["snippet"]["topLevelComment"]["snippet"]

            comments.append({

                "author":

                    top.get("authorDisplayName", ""),

                "text":

                    top.get("textDisplay", ""),

                "likeCount":

                    top.get("likeCount", 0),

                "publishedAt":

                    top.get("publishedAt", ""),

                "updatedAt":

                    top.get("updatedAt", ""),

                "replyCount":

                    item["snippet"].get("totalReplyCount", 0),

                "isReply":

                    False

            })

            if len(comments) >= max_comments:

                break

            # 답글 포함 여부
            if include_replies:

                if "replies" in item:

                    reply_items = item["replies"]["comments"]

                    for reply in reply_items:

                        rs = reply["snippet"]

                        comments.append({

                            "author":

                                rs.get("authorDisplayName", ""),

                            "text":

                                rs.get("textDisplay", ""),

                            "likeCount":

                                rs.get("likeCount", 0),

                            "publishedAt":

                                rs.get("publishedAt", ""),

                            "updatedAt":

                                rs.get("updatedAt", ""),

                            "replyCount":

                                0,

                            "isReply":

                                True

                        })

                        if len(comments) >= max_comments:

                            break
                          next_page = response.get("nextPageToken")

        if not next_page:
            break

    # 최대 댓글 수 초과 시 잘라내기
    comments = comments[:max_comments]

    return comments


# -------------------------------------------------------
# 채널 정보 조회 (선택 기능)
# -------------------------------------------------------

def get_channel_info(api_key, channel_id):
    """
    채널 정보를 조회합니다.
    """

    youtube = get_service(api_key)

    try:

        request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )

        response = request.execute()

        if not response.get("items"):
            return None

        item = response["items"][0]

        return {
            "title": item["snippet"].get("title", ""),
            "subscribers": int(
                item["statistics"].get("subscriberCount", 0)
            ),
            "videos": int(
                item["statistics"].get("videoCount", 0)
            ),
            "views": int(
                item["statistics"].get("viewCount", 0)
            )
        }

    except HttpError:

        return None


# -------------------------------------------------------
# 댓글 DataFrame용 정리
# -------------------------------------------------------

def normalize_comments(comments):
    """
    누락된 값을 정리합니다.
    """

    normalized = []

    for c in comments:

        normalized.append({

            "author":
                c.get("author", ""),

            "text":
                c.get("text", ""),

            "likeCount":
                int(c.get("likeCount", 0)),

            "publishedAt":
                c.get("publishedAt", ""),

            "updatedAt":
                c.get("updatedAt", ""),

            "replyCount":
                int(c.get("replyCount", 0)),

            "isReply":
                bool(c.get("isReply", False))
        })

    return normalized


# -------------------------------------------------------
# 영상 URL 검사
# -------------------------------------------------------

def is_youtube_url(url):
    """
    YouTube URL 여부를 확인합니다.
    """

    return get_video_id(url) is not None


# -------------------------------------------------------
# 영상 통계 요약
# -------------------------------------------------------

def get_video_statistics(api_key, video_id):

    info = get_video_info(api_key, video_id)

    if info is None:
        return None

    return {

        "조회수":
            info["viewCount"],

        "좋아요":
            info["likeCount"],

        "댓글":
            info["commentCount"],

        "게시일":
            info["publishedAt"][:10]
    }


# -------------------------------------------------------
# API 연결 테스트
# -------------------------------------------------------

def test_api_key(api_key):
    """
    API Key가 정상인지 확인합니다.
    """

    try:

        youtube = get_service(api_key)

        youtube.videos().list(
            part="id",
            id="dQw4w9WgXcQ"
        ).execute()

        return True

    except Exception:

        return False


# -------------------------------------------------------
# 단독 실행 테스트
# -------------------------------------------------------

if __name__ == "__main__":

    API_KEY = "YOUR_API_KEY"

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    video_id = get_video_id(url)

    print("Video ID :", video_id)

    if test_api_key(API_KEY):

        print("API 연결 성공")

        info = get_video_info(
            API_KEY,
            video_id
        )

        print(info)

        comments = get_comments(
            API_KEY,
            video_id,
            max_comments=10,
            include_replies=False
        )

        print(f"댓글 {len(comments)}개 수집")

        for c in comments[:3]:
            print("-" * 50)
            print(c["author"])
            print(c["text"])

    else:

        print("API Key 오류")
