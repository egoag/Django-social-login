#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.1.3'
__author__ = 'Liao Xuefeng (askxuefeng@gmail.com)'

'''
Python client SDK for sina weibo API using OAuth 2.
'''

try:
    import json
except ImportError:
    import simplejson as json

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import gzip
import time
import hmac
import base64
import hashlib
import urllib
import urllib2
import logging
import mimetypes
import collections


class APIError(Exception):

    '''
    raise APIError if receiving json message indicating failure.
    '''

    def __init__(self, error_code, error, ):
        self.error_code = error_code
        self.error = error
        Exception.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s' % (self.error_code, self.error)


def _parse_json(s):
    ' parse str into JsonDict '

    def _obj_hook(pairs):
        ' convert json object to python object '
        o = JsonDict()
        for k, v in pairs.iteritems():
            o[str(k)] = v
        return o
    return json.loads(s, object_hook=_obj_hook)


class JsonDict(dict):

    ' general json object that allows attributes to be bound to and also behaves like a dict '

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(
                r"'JsonDict' object has no attribute '%s'" %
                attr)

    def __setattr__(self, attr, value):
        self[attr] = value


def _encode_params(**kw):
    '''
    do url-encode parameters

    >>> _encode_params(a=1, b='R&D')
    'a=1&b=R%26D'
    >>> _encode_params(a=u'\u4e2d\u6587', b=['A', 'B', 123])
    'a=%E4%B8%AD%E6%96%87&b=A&b=B&b=123'
    '''
    args = []
    for k, v in kw.iteritems():
        if isinstance(v, basestring):
            qv = v.encode('utf-8') if isinstance(v, unicode) else v
            args.append('%s=%s' % (k, urllib.quote(qv)))
        elif isinstance(v, collections.Iterable):
            for i in v:
                qv = i.encode('utf-8') if isinstance(i, unicode) else str(i)
                args.append('%s=%s' % (k, urllib.quote(qv)))
        else:
            qv = str(v)
            args.append('%s=%s' % (k, urllib.quote(qv)))
    return '&'.join(args)


def _encode_multipart(**kw):
    ' build a multipart/form-data body with randomly generated boundary '
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    for k, v in kw.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            # file-like object:
            filename = getattr(v, 'name', '')
            content = v.read()
            data.append(
                'Content-Disposition: form-data; name="%s"; filename="hidden"' %
                k)
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % _guess_content_type(filename))
            data.append(content)
        else:
            data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
            data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
    data.append('--%s--\r\n' % boundary)
    return '\r\n'.join(data), boundary


def _guess_content_type(url):
    n = url.rfind('.')
    if n == (-1):
        return 'application/octet-stream'
    ext = url[n:]
    return mimetypes.types_map.get(ext, 'application/octet-stream')

_HTTP_GET = 0
_HTTP_POST = 1
_HTTP_UPLOAD = 2


def _http_get(url, authorization=None, **kw):
    logging.info('GET %s' % url)
    return _http_call(url, _HTTP_GET, authorization, **kw)


def _http_post(url, authorization=None, **kw):
    logging.info('POST %s' % url)
    return _http_call(url, _HTTP_POST, authorization, **kw)


def _http_upload(url, authorization=None, **kw):
    logging.info('MULTIPART POST %s' % url)
    return _http_call(url, _HTTP_UPLOAD, authorization, **kw)


def _read_body(obj):
    using_gzip = obj.headers.get('Content-Encoding', '') == 'gzip'
    body = obj.read()
    if using_gzip:
        logging.info('gzip content received.')
        gzipper = gzip.GzipFile(fileobj=StringIO(body))
        fcontent = gzipper.read()
        gzipper.close()
        return fcontent
    return body


def _http_call(the_url, method, authorization, **kw):
    '''
    send an http request and return a json object if no error occurred.
    '''
    params = None
    boundary = None
    if method == _HTTP_UPLOAD:
        # fix sina upload url:
        the_url = the_url.replace('https://api.', 'https://upload.api.')
        params, boundary = _encode_multipart(**kw)
    else:
        params = _encode_params(**kw)
        if '/remind/' in the_url:
            # fix sina remind api:
            the_url = the_url.replace('https://api.', 'https://rm.api.')
    http_url = '%s?%s' % (the_url, params) if method == _HTTP_GET else the_url
    http_body = None if method == _HTTP_GET else params
    req = urllib2.Request(http_url, data=http_body)
    req.add_header('Accept-Encoding', 'gzip')
    if authorization:
        req.add_header('Authorization', 'OAuth2 %s' % authorization)
    if boundary:
        req.add_header(
            'Content-Type',
            'multipart/form-data; boundary=%s' %
            boundary)
    try:
        resp = urllib2.urlopen(req)
        body = _read_body(resp)
        try:
            r = _parse_json(body)
        except ValueError:
            r = _parse_json(body[10:-3])
        if hasattr(r, 'error'):
            raise APIError(r.error, r.get('error_description', ''))
        if hasattr(r, 'ret') and r.ret < 0:
            raise APIError(r.ret, r.get('msg', ''))
        if hasattr(r, 'error_code'):
            raise APIError(r.error_code, r.get('msg', ''))
        return r
    except urllib2.HTTPError as e:
        try:
            r = _parse_json(_read_body(e))
        except:
            r = None
        if hasattr(r, 'error'):
            raise APIError(r.error, r.get('error_description', ''))
        raise e


class HttpObject(object):

    def __init__(self, client, method):
        self.client = client
        self.method = method

    def __getattr__(self, attr):
        def wrap(**kw):
            if self.client.is_expires():
                raise APIError('21327', 'expired_token', attr)
            return _http_call(
                '%s%s' %
                (self.client.api_url,
                 attr.replace(
                     '__',
                     '/')),
                self.method,
                self.client.access_token,
                **kw)
        return wrap


class APIClient(object):

    '''
    API client using synchronized invocation.
    '''

    def __init__(self, app_key, app_secret, redirect_uri=None,
                 clientip='127.0.0.1', response_type='code',
                 domain='graph.qq.com'):
        self.client_id = str(app_key)
        self.client_secret = str(app_secret)
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.auth_url = 'https://%s/oauth2.0/' % domain
        self.api_url = 'https://%s/' % (domain)
        self.openid_url = 'https://%s/oauth2.0/me' % domain
        self.access_token = None
        self.openid = None
        self.expires = 0.0
        self.get = HttpObject(self, _HTTP_GET)
        self.post = HttpObject(self, _HTTP_POST)
        self.upload = HttpObject(self, _HTTP_UPLOAD)

    def parse_signed_request(self, signed_request):
        '''
        parse signed request when using in-site app.

        Returns:
            dict object like { 'uid': 12345, 'access_token': 'ABC123XYZ', 'expires': unix-timestamp },
            or None if parse failed.
        '''

        def _b64_normalize(s):
            appendix = '=' * (4 - len(s) % 4)
            return s.replace('-', '+').replace('_', '/') + appendix

        sr = str(signed_request)
        logging.info('parse signed request: %s' % sr)
        enc_sig, enc_payload = sr.split('.', 1)
        sig = base64.b64decode(_b64_normalize(enc_sig))
        data = _parse_json(base64.b64decode(_b64_normalize(enc_payload)))
        if data['algorithm'] != u'HMAC-SHA256':
            return None
        expected_sig = hmac.new(
            self.client_secret,
            enc_payload,
            hashlib.sha256).digest()
        if expected_sig == sig:
            data.user_id = data.uid = data.get('user_id', None)
            data.access_token = data.get('oauth_token', None)
            expires = data.get('expires', None)
            if expires:
                data.expires = data.expires_in = time.time() + expires
            return data
        return None

    def set_access_token(self, access_token, expires, openid=None):
        self.access_token = str(access_token)
        self.openid = openid
        self.expires = float(expires)

    def get_authorize_url(self, redirect_uri=None, **kw):
        '''
        return the authorization url that the user should be redirected to.
        '''
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        if not redirect:
            raise APIError(
                '21305',
                'Parameter absent: redirect_uri',
                'OAuth2 request')
        response_type = kw.pop('response_type', 'code')
        return '%s%s?%s' % (self.auth_url, 'authorize',
                            _encode_params(client_id=self.client_id,
                                           response_type=response_type,
                                           redirect_uri=redirect, **kw))

    def request_access_token(self, code, redirect_uri=None):
        '''
        return access token as a JsonDict: {"access_token":"your-access-token","expires_in":12345678,"uid":1234}, expires_in is represented using standard unix-epoch-time
        '''
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        if not redirect:
            raise APIError(
                '21305',
                'Parameter absent: redirect_uri',
                'OAuth2 request')
        http_url = '%s%s?grant_type=authorization_code&' % (self.auth_url,
                                                            'token') + _encode_params(redirect_uri=self.redirect_uri,
                                                                                      code=code,
                                                                                      client_secret=self.client_secret,
                                                                                      client_id=self.client_id)
        req = urllib2.Request(http_url)
        req.add_header('Accept-Encoding', 'gzip')
        try:
            resp = urllib2.urlopen(req)
            body = _read_body(resp)
            try:
                body = dict([p.split('=') for p in body.split('&')])
            except ValueError:
                r = _parse_json(body[10:-3])
                if hasattr(r, 'error'):
                    raise APIError(r.error, r.get('error_description', ''))
            #r = _parse_json(body)
            r = JsonObject()
            for k, v in body.iteritems():
                r[str(k)] = v
            return r
        except urllib2.HTTPError as e:
            try:
                r = _parse_json(_read_body(e))
            except:
                r = None
            if hasattr(r, 'error'):
                raise APIError(r.error, r.get('error_description', ''))
            raise e

        current = int(time.time())
        expires = r.expires_in + current
        remind_in = r.get('remind_in', None)
        if remind_in:
            rtime = int(remind_in) + current
            if rtime < expires:
                expires = rtime
        return JsonDict(
            access_token=r.access_token,
            expires=expires,
            expires_in=expires,
            uid=r.get(
                'uid',
                None))

    def refresh_token(self, refresh_token):
        req_str = '%s%s' % (self.auth_url, 'access_token')
        r = _http_post(req_str,
                       client_id=self.client_id,
                       client_secret=self.client_secret,
                       refresh_token=refresh_token,
                       grant_type='refresh_token')
        current = int(time.time())
        expires = r.expires_in + current
        remind_in = r.get('remind_in', None)
        if remind_in:
            rtime = int(remind_in) + current
            if rtime < expires:
                expires = rtime
        return JsonDict(
            access_token=r.access_token,
            expires=expires,
            expires_in=expires,
            uid=r.get(
                'uid',
                None))

    def is_expires(self):
        return not self.access_token or time.time() > self.expires

    def __getattr__(self, attr):
        if '__' in attr:
            return getattr(self.get, attr)
        return _Callable(self, attr)

    def get_openid(self, token):
        http_url = '%s?%s' % (
            self.openid_url, _encode_params(access_token=token))
        req = urllib2.Request(http_url, data=None)
        #resp = urllib2.urlopen(req)
        #body = resp.read()
        #body = body[10:-3]
        try:
            resp = urllib2.urlopen(req)
            body = _read_body(resp)
            body = body[10:-3]
            r = _parse_json(body)
            if hasattr(r, 'error'):
                raise APIError(r.error, r.get('error_description', ''))
            self.openid = r.openid
            return r
        except urllib2.HTTPError as e:
            try:
                r = _parse_json(_read_body(e))
            except:
                r = None
            if hasattr(r, 'error'):
                raise APIError(r.error, r.get('error_description', ''))
            raise e

_METHOD_MAP = {'GET': _HTTP_GET, 'POST': _HTTP_POST, 'UPLOAD': _HTTP_UPLOAD}


class JsonObject(dict):

    '''
    general json object that can bind any fields but also act as a dict.
    '''

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class _Executable(object):

    def __init__(self, client, method, path):
        self._client = client
        self._method = method
        self._path = path

    def __call__(self, **kw):
        method = _METHOD_MAP[self._method]
        if method == _HTTP_POST and 'pic' in kw:
            method = _HTTP_UPLOAD
        return _http_call(
            '%s%s' %
            (self._client.api_url,
             self._path),
            method,
            self._client.access_token,
            **kw)
        # return _http_call('%s%s' % (self._client.api_url, self._path), method, self._client.access_token,
        # access_token=self._client.token,
        # openid=self._client.openid,
        # oauth_consumer_key=self._client.client_id,
        #**kw)

    def __str__(self):
        return '_Executable (%s %s)' % (self._method, self._path)

    __repr__ = __str__


class _Callable(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, attr):
        if attr == 'get':
            return _Executable(self._client, 'GET', self._name)
        if attr == 'post':
            return _Executable(self._client, 'POST', self._name)
        name = '%s/%s' % (self._name, attr)
        return _Callable(self._client, name)

    def __str__(self):
        return '_Callable (%s)' % self._name

    __repr__ = __str__

if __name__ == '__main__':
    import doctest
    doctest.testmod()
