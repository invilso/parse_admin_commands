import requests
from requests.models import parse_url
from bs4 import BeautifulSoup
import json
import pandas as pd
import config
import time

class Parser():
    max_page = 1
    current_page = 1
    filters = []
    filtered_posts = []
    temp_ids = []

    def getPostTitle(self, post):
        soup = BeautifulSoup(post, 'lxml')
        try:
            return soup.find_all("h1", {'data-cy': 'ad_title'})[0].text
        except IndexError:
            return 'Error'

    def getPostDescription(self, post):
        soup = BeautifulSoup(post, 'lxml')
        decription_container = soup.find_all("div", {'data-cy': 'ad_description'})[0]
        return decription_container.find_all("div")[0].text

    def getTitleCell(self, post):
        return post.find_all("td", {'class': 'title-cell'})[0]

    def getPostLink(self, post):
        title_cell = self.getTitleCell(post)
        return title_cell.find_all("a", {'data-cy':'listing-ad-title'})[0]['href']

    def getPostTitle(self, post):
        title_cell = self.getTitleCell(post)
        title_link = title_cell.find_all("a", {'data-cy':'listing-ad-title'})[0]
        return title_link.find_all("strong")[0].text
    
    def getPostPrice(self, post):
        try:
            price_cell = post.find_all("p", {'class':'price'})[0]
            return price_cell.find_all("strong")[0].text
        except IndexError:
            return 'Null'

    def getPostLocation(self, post):
        return post.find_all("i", {'data-icon':'location-filled'})[0].next

    def getPostDate(self, post):
        return post.find_all("i", {'data-icon':'clock'})[0].next

    def getPostPhoto(self, post):
        try:
            return post.find_all("img")[0]['src']
        except IndexError:
            return 'https://st4.depositphotos.com/37366546/38555/v/600/depositphotos_385551166-stock-illustration-no-photos-icon-linear-vector.jpg'

    def getAllPosts(self, page):
        soup = BeautifulSoup(page, 'lxml')
        posts = soup.find_all("table", {'summary': 'Объявление'})
        posts_data = []
        notf = Notifier()
        for post in posts:
            title = self.getPostTitle(post)
            if self.filterTitle(title):
                if int(post['data-id']) not in self.temp_ids:
                    if not self.checkForOld(int(post['data-id'])):
                        data = {
                            'id': int(post['data-id']),
                            'link': self.getPostLink(post),
                            'title': title,
                            'location': self.getPostLocation(post),
                            'photo': self.getPostPhoto(post),
                            'price': self.getPostPrice(post),
                            'date': self.getPostDate(post),
                        }
                        posts_data.append(data)
                        self.temp_ids.append(int(post['data-id']))
                        notf.prepareToSend(data)
                        print('Объявление '+data['title']+' отправлено вам в Telegram и добавлено в базу.')
        return posts_data

    def getMaxPage(self, page):
        soup = BeautifulSoup(page, 'lxml')
        try:
            last_page = soup.find_all("a", {'data-cy': 'page-link-last'})[0]
            return last_page.find_all("span")[0].text
        except IndexError:
            return '1'

    def getPages(self, category):
        pages = []
        while int(self.max_page) >= int(self.current_page):
            print('Start parsed page: '+str(self.current_page)+'/'+str(self.max_page))
            resp = requests.get('https://www.olx.ua/'+str(category)+'/?page='+str(self.current_page))
            page = resp.text
            for pg in self.getAllPosts(page):
                pages.append(pg)
            if int(self.current_page) != int(self.max_page) or int(self.max_page) == 1:
                self.max_page = self.getMaxPage(page)
            print('End parsed page: '+str(self.current_page)+'/'+str(self.max_page))
            self.current_page = self.current_page + 1
            time.sleep(1)
        return pages

    def prepareToNextCategoty(self):
        self.current_page = 1
        self.max_page = 1

    def filterTitle(self, title):
        for filter in self.filters:
            check_and = 0
            for word in filter['words']:
                if word in title.lower():
                    check_and = check_and + 1
            if check_and == len(filter["words"]):
                return True
        return False
                       
    def getCategoryes(self, categoryes):
        for category in categoryes:
            for page in self.getPages(category):
                self.filtered_posts.append(page)
            self.prepareToNextCategoty()

    def checkForOld(self, id):
        ids_old = []
        notf = Notifier()
        for post in notf.read():
            ids_old.append(post['id'])
        if id in ids_old:
            return True
        return False

class Notifier():
    def write(self):
        current = []
        temp_ids = []
        old = self.read()
        for post in old:
            if int(post['id']) not in temp_ids:
                current.append(post)
                temp_ids.append(int(post['id']))
        for post in Parser.filtered_posts:
            if int(post['id']) not in temp_ids:
                current.append(post)
                temp_ids.append(int(post['id']))
        with open('posts.json', 'w+', encoding='utf-8') as f:
            f.write(json.dumps(current))

    def read(self):
        with open('posts.json', 'r', encoding='utf-8') as f:
            return json.loads(f.read())

    def prepareToSend(self, post):
        text = f"""Новое обьявление на OLX!\nID: {post['id']}\nTITLE: {post['title']}\nLOCATION: {post['location']}\nPRICE: {post['price']}\nDATE: {post['date']}\nLINK: {post['link']}"""
        self.send(text, post['photo'])

    def send(self, text, photo):
        data = {'chat_id': config.USER_ID, 'photo': photo, 'caption': text}
        requests.post('https://api.telegram.org/bot'+config.TOKEN+'/sendPhoto', data=data)
      

class Writer():
    notf = Notifier()

    def serializeToWrite(self):
        ids = []
        data = self.notf.read()
        for post in data:
            ids.append(post['id'])
        titles = []
        for post in data:
            titles.append(post['title'])
        links = []
        for post in data:
            links.append(post['link'])
        dates = []
        for post in data:
            dates.append(post['date'])
        locations = []
        for post in data:
            locations.append(post['location'])
        photos = []
        for post in data:
            photos.append(post['photo'])
        prices = []
        for post in data:
            prices.append(post['price'])
        return {'ID': ids, 'TITLE': titles, 'LINKS': links, 'PRICE': prices, 'DATE': dates, 'LOCATION': locations, 'PHOTO': photos}

    def write(self):
        dataframe = pd.DataFrame(self.serializeToWrite())
        file_write = False
        while not file_write:
            try:
                dataframe.to_excel('./items.xlsx', index = False)
                file_write = True
            except Exception as err:
                print('Вами открыт файл items.xlsx!! Ожидаю закрытия 10 секунд.')
            time.sleep(10)



class Init():
    def readCategoryes(self):
        with open('categoryes.txt', encoding='utf-8') as f:
            categoryes = []
            for category in f.read().split('\n'):
                category = category.strip(' \t\n\r')
                category = category.strip('/')
                categoryes.append(category)
        return categoryes


    def readFilters(self):
        with open('filter.txt', encoding='utf-8') as f:
            Parser().filters = []
            for line in f.read().split('\n'):
                line = line.strip(' \t\n\r')
                words = []
                for word in line.split(','):
                    word = word.strip(' \t\n\r')
                    word = word.lower()
                    words.append(word)
                Parser().filters.append({'words': words})
            
    def start(self):
        p = Parser()
        notf = Notifier()
        wr = Writer()

        self.readFilters()
        notf.read()
        p.getCategoryes(self.readCategoryes())
        notf.write()
        wr.write()
        p.filtered_posts = []
        

secs_or_min = input('Привет. Выберите как вы хотите задавать интервал (0 - минуты, 1 - часы, другое - секунды): ')
secs = int(input('Введите числом интервал с которым будет запускаться скрипт: '))

if secs_or_min == '0':
    secs = secs * 60
elif secs_or_min == '1':
    secs = secs * 3600

init = Init()
i = 0
while True:
    try:
        i = i + 1
        init.start()
        print(f'Закончен {i} проход.')
        time.sleep(int(secs))
    except Exception as err:
        if "[Errno 13] Permission denied: './items.xlsx'" in str(err):
            print('Закройте файл Excel!! Жду 1 минуту.')
            time.sleep(60)
        else:
            print(f'ОШИБКА: {str(err)}')
    
    