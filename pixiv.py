import requests
from bs4 import BeautifulSoup
import re
import getpass
from io import BytesIO
from PIL import Image


class Pixiv:
    def __init__(self, pixiv_id: str, password: str, id: int):
        self.base_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
        self.login_url = "https://accounts.pixiv.net/login?lang=en"
        self.account = pixiv_id
        self.passwd = password
        self.painter_id = id
        self.req_headers = {
            "Host": "accounts.pixiv.net",
            "Referer": self.base_url,
            "Connection": "keep-alive"
        }
        self.post_key = []
        self.cookie = ""
        self.sess = requests.session()
        self.work_list = []
        self.page_list = []

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
        self.sess.post(self.login_url, data=login_data)
        #至此模拟登录完成

    def search_all_works_pages_by_id(self):
        self.login()
        #便于测试,从指定某个画师作品的首页获取
        # painter_page = self.sess.get("http://www.pixiv.net/member_illust.php?id=465133")
        req_url = "http://www.pixiv.net/member_illust.php"
        painter_page = self.sess.get(req_url + '?id=' + str(self.painter_id))
        fav_soup = BeautifulSoup(painter_page.text, 'lxml')

        # 获取所有的的页码
        gallery_list = fav_soup.find('ul', 'page-list')
        page_list_buffer = BeautifulSoup(str(gallery_list), 'lxml').find_all('a')
        
        self.page_list = ['?id=' + str(self.painter_id)]
        for x in page_list_buffer:
            req = BeautifulSoup(str(x), 'lxml')
            self.page_list.append(req.a['href'])

        page_count = 0
        for page in self.page_list:
            ret_htm = self.sess.get(req_url + page)
            work_soup = BeautifulSoup(ret_htm.text, 'lxml')
            work_list_origin = work_soup.find_all('a', 'work')

            #获取每个画册的源地址
            for x in work_list_origin:
                tmp = BeautifulSoup(str(x), 'lxml')
                self.work_list.append(tmp.a['href'])

            gallery_count = 0
            
            #对每页的画册深度搜索
            for i in range(0, len(self.work_list)):
                print('Downloading from the page %d - %d gallery' % (page_count, gallery_count))
                manga_page = "http://www.pixiv.net" + self.work_list[i].replace('medium', 'manga')
                work_sub_lib = self.sess.get(manga_page)
                work_sub_lib_src = BeautifulSoup(work_sub_lib.text, 'lxml')
                img_src_register = work_sub_lib_src.find_all('img', 'image ui-scroll-view')

                #将所有的图片源地址放到sub_list里
                sub_list = []
                for x in img_src_register:
                    tmp = BeautifulSoup(str(x), 'lxml')
                    sub_list.append(tmp.img['data-src'])

                #下载图片
                for x in sub_list:
                    self.get_image(x, manga_page)
                gallery_count += 1
            page_count += 1

    def get_image(self, url, referer):
        img = self.sess.get(url, headers={"Referer": referer})
        im = Image.open(BytesIO(img.content))
        im.save("pics/" + url[-26:-4] + ".png", 'png')


if __name__ == "__main__":
    account = input("input account:")
    passwd  = getpass.getpass("input password:")
    while(1):
        painter_id = input("input the painter's id:")
        if(painter_id != '#'):
            tmp = Pixiv(account, passwd, painter_id)
            tmp.search_all_works_pages_by_id()
        else:
            exit(0)

