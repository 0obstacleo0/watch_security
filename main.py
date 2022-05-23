import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt
import datetime
import mail

# 記事クラス
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


# html取得
def get_content(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    return soup


# メール送信
def make_mail(forest_lists, ipa_lists, jvn_lists, sn_lists, debug_flg=False):
    text = ""
    subject = "[セキュリティ監視君]"
    if len(forest_lists) != 0:
        subject += "窓の杜:{}".format(len(forest_lists))
    if len(ipa_lists) != 0:
        subject += "/IPA:{}".format(len(ipa_lists))
    if len(jvn_lists) != 0:
        subject += "/JVN:{}".format(len(jvn_lists))
    if len(sn_lists) != 0:
        subject += "/Security NEXT:{}".format(len(sn_lists))

    if len(forest_lists) != 0:
        text += (
            "########################\n"
            + "【窓の杜-インターネット/セキュリティ関連記事】\n"
            + "########################\n"
            + "----------\n"
        )
        for l in forest_lists:
            text += "{}\n{}\n".format(l.title, l.url)
            text += "----------\n"

    if len(ipa_lists) != 0:
        text += (
            "########################\n"
            + "【IPA-重要なセキュリティ情報】\n"
            + "########################\n"
            + "----------\n"
        )
        for l in ipa_lists:
            text += "{}\n{}\n".format(l.title, l.url)
            text += "----------\n"

    if len(jvn_lists) != 0:
        text += (
            "########################\n"
            + "【JVN-脆弱性情報】\n"
            + "########################\n"
            + "----------\n"
        )
        for l in jvn_lists:
            text += "{}\n{}\n".format(l.title, l.url)
            text += "----------\n"

    if len(sn_lists) != 0:
        text += (
            "########################\n"
            + "【Security NEXT-新着記事】\n"
            + "########################\n"
            + "----------\n"
        )
        for l in sn_lists:
            text += "{}\n{}\n".format(l.title, l.url)
            text += "----------\n"

    if err_msg != "":
        text += (
            "########################\n"
            + "【データ取得エラー】\n"
            + "########################\n"
            + "----------\n"
            + err_msg
        )

    # 件名調整
    if subject[11:12] == "/":
        subject = subject[:11] + subject[12:]

    if debug_flg is False:
        mail.send_mail(subject, text)


# 窓の杜コンテンツ取得
def get_forest_content(url, articles):
    soup = get_content(url)
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

                if debug_flg is False:
                    if yester_day == date:
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
def search_forest():
    list_article = []
    try:
        get_forest_content(
            url="https://forest.watch.impress.co.jp/category/internet/",
            articles=list_article,
        )
        get_forest_content(
            url="https://forest.watch.impress.co.jp/category/security/",
            articles=list_article,
        )
    except:
        global err_msg
        err_msg += "・窓の杜\n"

    return list_article


# IPA
def search_ipa():
    list_article = []
    try:
        soup = get_content("https://www.ipa.go.jp/security/announce/alert.html")
        lists = soup.find_all(class_="ipar_newstable")
        lists = lists[0]
        lists = lists.find_all("tr")

        for l in lists:
            url = "https://www.ipa.go.jp" + l.select_one("a").get("href")
            title = l.select_one("a").contents[0]
            date = dt.strptime(l.select_one("th").contents[0], r"%Y年%m月%d日")

            if debug_flg is False:
                if yester_day == date:
                    article = Article(title, url, date)
                    list_article.append(article)
            else:
                article = Article(title, url, date)
                list_article.append(article)
    except:
        global err_msg
        err_msg += "・IPA\n"

    return list_article


# JVN
def serach_jvn():
    list_article = []
    try:
        soup = get_content("https://jvn.jp")
        lists = soup.find_all(id="news-list")
        lists = lists[0]
        lists = lists.find_all("dl")

        for l in lists:
            url = "https://jvn.jp" + l.select_one("a").get("href")
            title = l.select_one("a").contents[0]
            date = dt.strptime(
                l.select_one("li").contents[4], r"　[%Y/%m/%d %H:%M]"
            ).replace(hour=0, minute=0, second=0, microsecond=0)

            if debug_flg is False:
                if yester_day == date:
                    article = Article(title, url, date)
                    list_article.append(article)
            else:
                article = Article(title, url, date)
                list_article.append(article)
    except:
        global err_msg
        err_msg += "・JVN\n"

    return list_article


# Security NEXT
def serach_sn():
    list_article = []
    try:
        soup = get_content("https://www.security-next.com")
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

            if debug_flg is False:
                if yester_day == date:
                    article = Article(title, url, date)
                    list_article.append(article)
            else:
                article = Article(title, url, date)
                list_article.append(article)
    except:
        global err_msg
        err_msg += "・Security NEXT\n"

    return list_article


if __name__ == "__main__":
    debug_flg = False
    err_msg = ""
    yester_day = dt.today().replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + datetime.timedelta(days=-1)

    forest_lists = search_forest()
    ipa_lists = search_ipa()
    jvn_lists = serach_jvn()
    sn_lists = serach_sn()

    if (len(forest_lists) + len(ipa_lists) + len(jvn_lists) + len(sn_lists)) != 0:
        make_mail(forest_lists, ipa_lists, jvn_lists, sn_lists)
