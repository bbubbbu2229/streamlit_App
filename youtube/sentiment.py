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
