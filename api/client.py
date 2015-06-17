from django.conf import settings as st
from .sdk.weibo import APIClient as WeiboClient
#from .sdk.douban_client import DoubanClient
from douban_client import DoubanClient
from .sdk.qq import APIClient as QQClient


class Weibo(WeiboClient):

    def __init__(self):
        super(Weibo, self).__init__(app_key=st.WEIBO_KEY,
                                    app_secret=st.WEIBO_SECRET,
                                    redirect_uri=st.WEIBO_REDIRECT)


class Douban(DoubanClient):

    def __init__(self):
        super(Douban, self).__init__(key=st.DOUBAN_KEY,
                                     secret=st.DOUBAN_SECRET,
                                     redirect=st.DOUBAN_REDIRECT)


class QQ(QQClient):

    def __init__(self):
        super(QQ, self).__init__(app_key=st.QQ_KEY,
                                 app_secret=st.QQ_SECRET,
                                 redirect_uri=st.QQ_REDIRECT)
