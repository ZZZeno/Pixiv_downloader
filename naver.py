import requests
from bs4 import BeautifulSoup



def fetch_pics(naver_url: str):
    naver_url = "https://comic.naver.com/webtoon/detail.nhn?titleId=716776&no=1&weekday=sat"

    r = requests.get(naver_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    mg_div = soup.find('div', {"class": "wt_viewer"})
    images = mg_div.find_all('img', {"alt": "comic content"})
    imgs = []
    for img in images:
        imgs.append(img['src'])

    return imgs

