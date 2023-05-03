from logic import HtmlHandler
from mail import MailManager
from collections import OrderedDict
import datetime
from datetime import datetime as dt
import os
from distutils.util import strtobool


def make_mail(dict, msg, debug_flg):
    subject = "[セキュリティ監視君]"

    text = ""
    for key, value in dict.items():
        text += (
            "########################\n"
            + "{}\n".format(key)
            + "########################\n"
            + "----------\n"
        )
        for v in value:
            text += "{}\n{}\n".format(v.title, v.url)
            text += "----------\n"

    if msg != "":
        text += (
            "########################\n"
            + "【データ取得エラー】\n"
            + "########################\n"
            + "----------\n"
            + msg
        )

    mm = MailManager()
    mm.send_mail(subject, text, debug_flg)


if __name__ == "__main__":
    yesterday = dt.today().replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + datetime.timedelta(days=-1)

    debug_flg = strtobool(os.environ["DEBUG_FLG"])
    hm = HtmlHandler(day=yesterday, debug_flg=debug_flg)
    od = OrderedDict(
        {
            "窓の杜": hm.search_forest(),
            "JVN": hm.search_jvn(),
            "IPA": hm.search_ipa(),
            "SecurityNext": hm.search_sn(),
        }
    )

    if (
        len(od["窓の杜"]) != 0
        or len(od["JVN"]) != 0
        or len(od["IPA"]) != 0
        or len(od["Security Next"]) != 0
    ):
        make_mail(dict=od, msg=hm.err_msg, debug_flg=hm.debug_flg)
