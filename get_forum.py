import requests
import antiddos 
import time
import re

class LoginAndGet:
    session = requests.Session()
    cookies = {}
    data_for_login = {"login": "", "password": "", "remember_me": 1}
    data_login = {}
    forum_url = "http://gta-trinity.ru/forum/"

    def __init__(self, login: str, password: str):
        try:
            get_react = self.session.get(self.forum_url, timeout=10).text
            cookies_info = antiddos.get(get_react)
            self.cookies = {
                'name' : 'REACTLABSPROTECTION',
                'value' : cookies_info,
            }
            self.session.cookies.set(**self.cookies)
            if login and password:
                self.data_for_login['password'] = password
                self.data_for_login['login'] = login
                self.login()
        except Exception as err:
            print("ERROR: In def __init__: " + str(err))

    def login(self):
        try:
            time.sleep(2)
            get_crsf = self.session.get(self.forum_url)
            csrfKey = re.findall('name="csrfKey" value="(.*)"', get_crsf.text)
            self.data_login = {
                'csrfKey' : csrfKey[0],
                'auth' : self.data_for_login["login"],
                'password' : self.data_for_login["password"],
                'remember_me' : self.data_for_login["remember_me"],
                '_processLogin' : "usernamepassword",
            }
            self.session.post(self.forum_url, data=self.data_login)
            print("LOG: Login - OK")
        except Exception:
            print("ERROR: In def Login")
            self.login()
        
    def get(self, link: str):
        r = None
        time.sleep(2)
        try:
            r = self.session.get(link, stream = True)
            if r.status_code == 200 or r.status_code == 201 or r.status_code == 202 or r.status_code == 203:
                with open("temp_json.html", "w+", encoding="utf-8") as k:
                    k.write('Clean json')
                with open("temp_json.html", "wb") as k:
                    for key, chunk in enumerate(r.iter_content(1024)):
                        if key < 1600:
                            if not chunk:
                                break
                            k.write(chunk)
                r = None
            else:
                print("Пхд форум лег: " + str(r.status_code))
        except Exception as err:
            print("ERROR: In method GET (without login): "+str(err))
            self.getF(link)
            r = None
        with open("temp_json.html", "r", encoding="utf-8") as t:
            return t.read()

    def post(self, link: str, data: dict):
        try:
            r = self.session.post(link, data)
            print("LOG: POST Without Login - OK")
        except Exception:
            print("ERROR: In method POST (without login)")
            self.postF(link, data)
            r = None
        return r
