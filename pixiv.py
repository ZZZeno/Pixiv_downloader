import requests
from bs4 import BeautifulSoup
import time
import re
import getpass
from io import BytesIO
from PIL import Image


sess = requests.session()
class Pixiv:
    def __init__(self, pixiv_id: str, password: str):
        self.base_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
        self.login_url = "https://accounts.pixiv.net/login?lang=en"
        self.account = pixiv_id
        self.passwd = password
        self.req_headers = {
            "Host": "accounts.pixiv.net",
            "Referer": self.base_url,
            "Connection": "keep-alive"
        }
        self.post_key = []
        self.cookie = ""
        self.sess = requests.session()
        self.work_list = []

    def login(self):
        login_html = self.sess.get(self.base_url)
        pattern = re.compile('<input type="hidden".*?value="(.*?)">', re.S)
        result = re.search(pattern, login_html.text)
        self.post_key = result.group(1)
        login_data = {
            "pixiv_id": self.account,
            "password": self.passwd,
            "post_key": self.post_key
        }
        tmp = self.sess.post(self.login_url, data=login_data)
        self.cookie = tmp.headers.get('Set-cookie')
        #至此模拟登录完成
        #这里的self.cookie没有用到

    def search_for_painter_by_id(self):
        #cookie.txt里存的是request headers里的cookie
        f = open('cookie.txt', 'r')
        temp_cookie = ""
        for x in f:
            temp_cookie += x

        #便于测试,从指定某个画师作品的首页获取
        painter_page = self.sess.get("http://www.pixiv.net/member_illust.php?id=465133", headers={"Cookie": temp_cookie})
        fav_soup = BeautifulSoup(painter_page.text, 'lxml')

        #从这个画师的作品中获取含多个图片的画册,关键词multiple
        work_list_origin = fav_soup.find_all('a', 'multiple')

        #获取每个画册的源地址
        for x in work_list_origin:
            tmp = BeautifulSoup(str(x), 'lxml')
            self.work_list.append(tmp.a['href'])

        #对所有的画册深度搜索,下载里面的图片,(0,13)是手动查出来的
        for i in range(0, 13):
            work_lib = self.sess.get("http://www.pixiv.net/"+self.work_list[i])
            tmp_soup = BeautifulSoup(work_lib.text, 'lxml')
            tmp_find = tmp_soup.find_all('div', 'img-container')
            tmp_find_soup = BeautifulSoup(str(tmp_find), 'lxml')
            print(tmp_find_soup.a['href'])

            #获取到图片lib
            work_sub_lib = self.sess.get("http://www.pixiv.net/"+tmp_find_soup.a['href'])
            work_sub_lib_src = BeautifulSoup(work_sub_lib.text, 'lxml')
            tmp_work_sub_lib_src = work_sub_lib_src.find_all('img', 'image ui-scroll-view')

            #将所有的图片源地址放到sub_list里
            sub_list = []
            for x in tmp_work_sub_lib_src:
                tmp = BeautifulSoup(str(x), 'lxml')
                sub_list.append(tmp.img['data-src'])

            #下载图片
            for x in sub_list:
                self.get_image(x, temp_cookie)


    def get_image(self, url, cookie):
        img = self.sess.get(url, headers={"Referer": self.base_url, "Cookie": cookie})
        im = Image.open(BytesIO(img.content))
        im.save("pics/" + url[-26:-4] + ".png", 'png')

if __name__ == "__main__":

    account = input("input account:")
    passwd  = getpass.getpass("input password:")
    tmp = Pixiv(account, passwd)
    # tmp.login()
    # tmp.get_image()
    tmp.search_for_painter_by_id()

