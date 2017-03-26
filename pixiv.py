import requests
from bs4 import BeautifulSoup
import time
import re
import getpass
from io import BytesIO
from PIL import Image


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

    def search_for_painter_by_id(self):
        painter_page = self.sess.get("http://www.pixiv.net/member.php?id=465133", headers={"Cookie": self.cookie})
        fav_soup = BeautifulSoup(painter_page.text, 'lxml')

        f = open("sky.htm", 'w')
        f.write(fav_soup.prettify())
        f.close()

    def get_image(self):
        test_img_url = "https://i1.pixiv.net/img-original/img/2017/03/23/01/12/06/62049404_p3.png"
        send = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36",
            "Referer": self.base_url,
            "Cookie": self.cookie
        }
        img = self.sess.get(test_img_url, headers=send)
        im = Image.open(BytesIO(img.content))
        im.save("tmp.png", 'png')


if __name__ == "__main__":

    account = input("input account:")
    passwd  = getpass.getpass("input password:")
    tmp = Pixiv(account, passwd)
    tmp.login()
    tmp.get_image()
    tmp.search_for_painter_by_id()

