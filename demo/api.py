from django.conf import settings as st

from weibo import APIClient as Weibo
from douban_client import DoubanClient as Douban
from pyoauth2 import Client

weibo_client = Weibo(st.WEIBO_KEY, st.WEIBO_SECRET,
        redirect_uri=st.WEIBO_REDIRECT)
douban_client = Douban(st.DOUBAN_KEY, st.DOUBAN_SECRET,
        st.DOUBAN_REDIRECT,
        'douban_basic_common,shuo_basic_r,shuo_basic_w')
qq_client = Client(st.QQ_KEY,st.QQ_SECRET,
        site='https://graph.qq.com',
        authorize_url='https://graph.qq.com/oauth2.0/authorize',
        token_url='https://graph.qq.com/oauth2.0/token')


