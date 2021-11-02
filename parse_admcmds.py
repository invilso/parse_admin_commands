import config
import get_forum

class Parser:
    forum = None

    def __init__(self) -> None:
        self.forum = get_forum.LoginAndGet(config.LOGIN, config.PASSWORD)

    def parseUrls(self):
        for url in config.URLS_FOR_PARSE:
            self.forum.get(url)

p = Parser()
p.parseUrls()