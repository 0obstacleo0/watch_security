from bs4 import BeautifulSoup
from datetime import datetime as dt
import ssl
import urllib.request


class Article:
    def __init__(self, title, url, date):
        self.title = title
        self.url = url
        self.date = date

    def __eq__(self, __o: object):
        if not isinstance(__o, Article):
            return NotImplemented
        return self.url == __o.url

    def __ne__(self, __o: object):
        return not self.__eq__(__o)


class HtmlHandler:
    def __init__(self, day, debug_flg=False, err_msg=""):
        self.day = day
        self.debug_flg = debug_flg
        self.err_msg = err_msg

    def _get_content(self, url):
        # SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED 対応
        ctx = ssl.create_default_context()
        ctx.options |= 0x4

        res = urllib.request.urlopen(url, context=ctx)
        soup = BeautifulSoup(res, "html.parser")
        return soup

    def _get_forest_content(self, url, articles):
        soup = self._get_content(url)
        lists = soup.find_all("ul", class_="list-02")
        lists = lists[4]
        lists = lists.find_all("li")

        for l in lists:
            link = l.select_one("p.title > a")
            date = l.select_one("p.date")
            if link is not None and date is not None:
                try:
                    url = link.get("href")
                    title = link.contents[0]
                    date = dt.strptime(date.contents[0], r"(%Y/%m/%d)")

                    # 重複チェック
                    exist_flg = False
                    for a in articles:
                        if a.url == url:
                            exist_flg = True
                            break

                    if self.debug_flg == False:
                        if self.day == date:
                            article = Article(title, url, date)
                            if not exist_flg:
                                articles.append(article)
                    else:
                        article = Article(title, url, date)
                        if not exist_flg:
                            articles.append(article)

                except IndexError:
                    None

    # 窓の杜
    def search_forest(self):
        list_article = []
        try:
            self._get_forest_content(
                url="https://forest.watch.impress.co.jp/category/internet/",
                articles=list_article,
            )
            self._get_forest_content(
                url="https://forest.watch.impress.co.jp/category/security/",
                articles=list_article,
            )
        except Exception as e:
            print(e)
            self.err_msg += "・窓の杜\n"

        return list_article

    # IPA
    def search_ipa(self):
        list_article = []
        try:
            soup = self._get_content(
                "https://www.ipa.go.jp/security/security-alert/index.html"
            )
            list = soup.find(class_="news-list")
            list = list.find_all("li")

            for l in list:
                if l.attrs["class"][0] != "news-list__item":
                    continue
                title = l.select_one("p.news-list__ttl").text
                url = "https://www.ipa.go.jp" + l.select_one("a").get("href")
                date = dt.strptime(
                    l.select_one("li.news-list__date").contents[0], r"%Y年%m月%d日"
                )

                if self.debug_flg == False:
                    if self.day == date:
                        article = Article(title, url, date)
                        list_article.append(article)
                else:
                    article = Article(title, url, date)
                    list_article.append(article)
        except Exception as e:
            print(e)
            self.err_msg += "・IPA\n"

        return list_article

    # JVN
    def search_jvn(self):
        list_article = []
        try:
            soup = self._get_content("https://jvn.jp")
            lists = soup.find_all(id="news-list")
            lists = lists[0]
            lists = lists.find_all("dl")

            for l in lists:
                url = "https://jvn.jp" + l.select_one("a").get("href")
                title = l.select_one("a").contents[0]
                date = dt.strptime(
                    l.select_one("li").contents[4], r"　[%Y/%m/%d %H:%M]"
                ).replace(hour=0, minute=0, second=0, microsecond=0)

                if self.debug_flg == False:
                    if self.day == date:
                        article = Article(title, url, date)
                        list_article.append(article)
                else:
                    article = Article(title, url, date)
                    list_article.append(article)
        except Exception as e:
            print(e)
            self.err_msg += "・JVN\n"

        return list_article

    # Security NEXT
    def search_sn(self):
        list_article = []
        try:
            soup = self._get_content("https://www.security-next.com")
            lists = soup.find_all(class_="content")[0].find_all("dl")[0].contents
            for l in lists:
                if l == "\n":
                    lists.remove("\n")

            date = ""
            for l in lists:
                if l.name == "dt":
                    date = dt.strptime(l.text, r"%Y/%m/%d").replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    continue
                elif l.name == "dd":
                    url = l.contents[0].get("href")
                    title = l.text

                if self.debug_flg == False:
                    if self.day == date:
                        article = Article(title, url, date)
                        list_article.append(article)
                else:
                    article = Article(title, url, date)
                    list_article.append(article)
        except Exception as e:
            print(e)
            self.err_msg += "・Security NEXT\n"

        return list_article
