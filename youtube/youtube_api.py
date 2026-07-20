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
