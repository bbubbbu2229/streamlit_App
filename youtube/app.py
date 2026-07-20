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
