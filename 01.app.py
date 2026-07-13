import streamlit as st
from datetime import date

st.set_page_config(
    page_title="✨ 별자리 궁합",
    page_icon="🌙",
    layout="centered"
)

# ------------------------
# 디자인
# ------------------------
st.markdown("""
<style>
.stApp{
background:linear-gradient(180deg,#1d2671,#c33764);
color:white;
}

.main-title{
text-align:center;
font-size:45px;
font-weight:bold;
color:#FFD700;
}

.sub{
text-align:center;
font-size:20px;
color:white;
}

.card{
background:rgba(255,255,255,0.15);
padding:20px;
border-radius:20px;
margin-top:15px;
box-shadow:0px 0px 20px rgba(255,255,255,0.2);
}

.big{
font-size:28px;
font-weight:bold;
color:#FFD700;
text-align:center;
}

.good{
color:#7CFC00;
font-weight:bold;
}

.bad{
color:#FF6B6B;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🌌 별자리 궁합</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>생년월일을 입력하면 별자리와 궁합을 알려드려요!</div>", unsafe_allow_html=True)

# ------------------------
# 별자리 판별
# ------------------------
def zodiac(month, day):

    if (month==3 and day>=21) or (month==4 and day<=19):
        return "양자리"
    elif (month==4 and day>=20) or (month==5 and day<=20):
        return "황소자리"
    elif (month==5 and day>=21) or (month==6 and day<=21):
        return "쌍둥이자리"
    elif (month==6 and day>=22) or (month==7 and day<=22):
        return "게자리"
    elif (month==7 and day>=23) or (month==8 and day<=22):
        return "사자자리"
    elif (month==8 and day>=23) or (month==9 and day<=22):
        return "처녀자리"
    elif (month==9 and day>=23) or (month==10 and day<=22):
        return "천칭자리"
    elif (month==10 and day>=23) or (month==11 and day<=22):
        return "전갈자리"
    elif (month==11 and day>=23) or (month==12 and day<=24):
        return "사수자리"
    elif (month==12 and day>=25) or (month==1 and day<=19):
        return "염소자리"
    elif (month==1 and day>=20) or (month==2 and day<=18):
        return "물병자리"
    else:
        return "물고기자리"

# ------------------------
# 궁합 데이터
# ------------------------

good_match={
"양자리":"사자자리",
"황소자리":"처녀자리",
"쌍둥이자리":"물병자리",
"게자리":"물고기자리",
"사자자리":"양자리",
"처녀자리":"황소자리",
"천칭자리":"쌍둥이자리",
"전갈자리":"게자리",
"사수자리":"양자리",
"염소자리":"황소자리",
"물병자리":"쌍둥이자리",
"물고기자리":"게자리"
}

bad_match={
"양자리":"게자리",
"황소자리":"사자자리",
"쌍둥이자리":"전갈자리",
"게자리":"양자리",
"사자자리":"황소자리",
"처녀자리":"사수자리",
"천칭자리":"염소자리",
"전갈자리":"쌍둥이자리",
"사수자리":"처녀자리",
"염소자리":"천칭자리",
"물병자리":"황소자리",
"물고기자리":"사자자리"
}

# ------------------------
# 입력
# ------------------------

st.divider()

birthday=st.date_input(
"🎂 나의 생년월일",
value=date(2010,1,1),
min_value=date(1950,1,1),
max_value=date.today()
)

my_star=zodiac(birthday.month,birthday.day)

st.markdown(f"""
<div class="card">
<div class="big">🌟 당신의 별자리는 {my_star}</div>

<p class='good'>💖 가장 잘 맞는 별자리 : {good_match[my_star]}</p>

<p class='bad'>⚠️ 잘 맞지 않는 별자리 : {bad_match[my_star]}</p>

</div>
""",unsafe_allow_html=True)

st.divider()

st.header("👭 친구와의 궁합")

friend=st.date_input(
"친구 생년월일",
value=date(2010,6,1),
key="friend"
)

friend_star=zodiac(friend.month,friend.day)

score=60

if friend_star==good_match[my_star]:
    score=98
elif friend_star==bad_match[my_star]:
    score=30
elif friend_star==my_star:
    score=90
else:
    score=75

st.markdown(f"""
<div class="card">

<h2>😊 친구의 별자리 : {friend_star}</h2>

<h1 style="text-align:center;color:#FFD700;">궁합 점수 {score}%</h1>

</div>
""",unsafe_allow_html=True)

if score>=90:
    st.success("💖 최고의 궁합입니다! 서로 잘 통하는 친구예요.")
elif score>=70:
    st.info("😊 좋은 궁합입니다. 함께하면 즐거운 시간을 보낼 수 있어요.")
elif score>=50:
    st.warning("🙂 무난한 궁합입니다. 서로 이해하려는 노력이 중요해요.")
else:
    st.error("⚠️ 성격 차이가 있을 수 있어요. 서로 배려하면 좋은 친구가 될 수 있습니다.")

st.divider()

st.caption("🌙 별자리 궁합은 재미로 즐겨주세요!")
