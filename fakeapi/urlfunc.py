""" url generation functions """
from urllib.parse import urlencode, urlparse, unquote_plus #, parse_qs, quote
from requests.utils import requote_uri

def get_url(url, params):
    """
    full url string from current url + params
    calculated like in response.url from requests
    """
    params = params or {}
    urlp = urlparse(url)
    query = urlencode(params)
    urlp = urlp._replace(query='&'.join([urlp.query, query]).strip('&'))
    return requote_uri(urlp.geturl())

def get_url2(url, params):
    """ full url without encoding """
    params = params or {}
    urlp = urlparse(url)
    query = unquote_plus(urlencode(params))
    urlp = urlp._replace(query='&'.join([urlp.query, query]).strip('&'))
    return urlp.geturl()
