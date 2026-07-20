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
