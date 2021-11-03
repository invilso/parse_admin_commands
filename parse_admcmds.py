import config
import re
import get_forum
import html
import json
from bs4 import BeautifulSoup

class Patterns:
    subtitle = '<span style="color:#c0392b;">(.+)</span></span>'
    command = '"color:#2980b9;">(.+)</span>(.+)'


class Parser:
    forum = None

    def __init__(self) -> None:
        self.forum = get_forum.LoginAndGet(config.LOGIN, config.PASSWORD)

    def getLines(self, text) -> list:
        return re.split('\n', text)

    def bruteUrls(self):
        database = []
        for url in config.URLS_FOR_PARSE:
            for line in self.getLines(self.forum.get(url)):
                #пиздец, есть опыт разработки и я не могу понять почему не работает с if re.match. По этому костыляю через try.
                try:
                    subtitle = re.findall(Patterns.subtitle, line)[0]
                    subtitle = re.sub(r'\u00a0', '', BeautifulSoup(subtitle).get_text())
                    database.append({'category': subtitle, 'commands': []})
                except:
                    pass
                try:
                    command, text = re.findall(Patterns.command, line)[0]
                    command = re.sub(r'\u00a0', '', BeautifulSoup(command).get_text())
                    text = re.sub(r'\u00a0', '', BeautifulSoup(text).get_text())
                    if command[0] == '/':
                        database[-1]['commands'].append({'command': command, 'text': text}) 
                except:
                    pass
        with open('out.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(database, indent=4))
            

p = Parser()
p.bruteUrls()