import requests
from bs4 import BeautifulSoup
import time
import cookiejar
import re
import getpass


sess = requests.session()
class Pixiv:
    def __init__(self, pixiv_id: str, password: str):
        self.base_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
        self.login_url = "https://accounts.pixiv.net/login?lang=en"
        self.account = pixiv_id
        self.passwd = password
        self.req_headers = {
            "Host": "accounts.pixiv.net",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36",
            "Referer": self.base_url,
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "keep-alive"
        }
        # self.sess = requests.session()
        self.post_key = []
        self.return_to = "http://www.pixiv.net/"
        self.cook = ""

    def login(self):
        login_html = sess.get(self.base_url)
        pattern = re.compile('<input type="hidden".*?value="(.*?)">', re.S)
        result = re.search(pattern, login_html.text)
        self.post_key = result.group(1)
        login_data = {
            "pixiv_id": self.account,
            "password": self.passwd,
            "post_key": self.post_key,
            "return_to": self.return_to,
            "Host": "accounts.pixiv.net",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36",
            "Referer": self.base_url,
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            "Connection": "keep-alive"
        }
        tmp = sess.post(self.login_url, data=login_data)
        self.cook = tmp.cookies



if __name__ == "__main__":
    account = None
    passwd  = None

    account = input("input account:")
    passwd  = getpass.getpass("input password:")
    tmp = Pixiv(account, passwd)
    tmp.login()
