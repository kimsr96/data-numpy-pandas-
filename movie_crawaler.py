import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re

# 네이버 영화 url
url = "https://movie.naver.com/movie/running/premovie.nhn"
# requests 요청
response = requests.get(url)
# 응답 확인
response
# 해당 text를 html로 변환
html = BeautifulSoup(response.text,"html.parser")
# 특정 태그 선택
data = html.select('div.obj_section div.lst_wrap ul.lst_detail_t1 li')
names = []              # 영화 제목
directors = []          # 영화 감독명
actors = []             # 영화 배우명
ratings = []            # 영화 관람등급
genres = []             # 영화 장르
times = []              # 영화 상영시간
release_dates = []      # 영화 개봉예정일
anticipate_up = []      # 기대지수 UP
anticipate_down = []    # 기대지수 DOWN

for item in data:
    # 각 컬럼별 태그 위치를 찾아서 리스트에 추가, 없다면 결측치 입력
    try:
        names.append(item.select('dl.lst_dsc dt.tit a')[0].text.strip())
    except IndexError:
        names.append(None)
    try:
        directors.append(re.sub('[\r\t\n]','',item.select('dl.lst_dsc dl.info_txt1 dd')[1].text.strip()))
    except IndexError:
        directors.append(None)
    try:
        actors.append(re.sub('[\r\t\n]','',item.select('dl.lst_dsc dl.info_txt1 dd')[2].text.strip()))
    except IndexError:
        actors.append(None)
    try:
        ratings.append(item.select('dl.lst_dsc dt.tit span')[0].text.strip())
    except IndexError:
        ratings.append(None)
    try:
        genre = item.select('dl.lst_dsc dl.info_txt1 dd')[0].select('a')[0].text.strip()
        if len(item.select('dl.lst_dsc dl.info_txt1 dd')[0].select('a')) > 1:
            for i in item.select('dl.lst_dsc dl.info_txt1 dd')[0].select('a')[1:]:
                genre += f', {i.text.strip()}'
        genres.append(genre)
    except IndexError:
        genres.append(None)
    try:
        star =  item.select('dl.lst_dsc dd.star dl.info_exp em')
        anticipate_up.append(star[0].text.strip())
        anticipate_down.append(star[1].text.strip())
    except IndexError:
        anticipate_up.append(None)
        anticipate_down.append(None)
    instance = re.sub('[\r\t\n]','',item.select('dl.info_txt1 dd')[0].text.strip()).split('|')
    tflag = False
    rflag = False
    for i in instance:
        if '분' in i:
            times.append(i.replace("분",""))
            tflag = True
        elif '개봉' in i:
            release_dates.append(i.replace("개봉","").strip())
            rflag = True
        else :
            continue
    if tflag == False :
        times.append(None)
    if rflag == False:
        release_dates.append(None)
# 데이터 프레임 생성
df = pd.DataFrame(columns=['Name','Director','Actor','Rating','Genre','Time','Release Date'])
df['Name'] = names
df['Director'] = directors
df['Actor'] = actors
df['Rating'] = ratings
df['Genre'] = genres
df['Time'] = times
df['Release Date'] = release_dates
df['anticipate Up'] = anticipate_up
df['anticipate Down'] = anticipate_down
# 기대지수가 없는 경우(재개봉)를 제외한 새로운 데이터프레임 생성
df2 = df.dropna(subset=['anticipate Up'])
# 인덱스 재지정 및 삭제
df2.reset_index(inplace=True)
del df2['index']

df.to_csv('./movie_final.csv',encoding='utf-8-sig')
df2.to_csv('./movies_2.csv',encoding='utf-8-sig')