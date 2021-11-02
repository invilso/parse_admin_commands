from _typeshed import Self
import config
import get_forum

class Parser:
    forum = None

    def __init__(self) -> None:
        self.forum = get_forum.LoginAndGet(config.LOGIN, config.PASSWORD)

    def parseUrls(self):
        print(self.forum.get(config.TEST_URL))

p = Parser()
p.parseUrls()