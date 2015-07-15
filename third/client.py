from django.conf import settings as st
from .sdk.weibo import APIClient as WeiboClient
from douban_client import DoubanClient
from .sdk.qq import APIClient as QQClient


class Weibo(WeiboClient):

    def __init__(self):
        if not (st.WEIBO_KEY or st.WEIBO_REDIRECT or st.WEIBO_SECRET):
            raise NameError
        super(Weibo, self).__init__(app_key=st.WEIBO_KEY,
                                    app_secret=st.WEIBO_SECRET,
                                    redirect_uri=st.WEIBO_REDIRECT)


class Douban(DoubanClient):

    def __init__(self):
        if not (st.DOUBAN_KEY or st.DOUBAN_SECRET or st.DOUBAN_REDIRECT):
            raise NameError
        super(Douban, self).__init__(key=st.DOUBAN_KEY,
                                     secret=st.DOUBAN_SECRET,
                                     redirect=st.DOUBAN_REDIRECT)


class QQ(QQClient):

    def __init__(self):
        if not (st.QQ_KEY or st.QQ_SECRET or st.QQ_REDIRECT):
            raise NameError
        super(QQ, self).__init__(app_key=st.QQ_KEY,
                                 app_secret=st.QQ_SECRET,
                                 redirect_uri=st.QQ_REDIRECT)
