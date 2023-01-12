"""
FakeAPI class to simulate rest API calls from json static files/data
Usefull to easily mock requests or api-client (APIClient) in unittest

api = FakeAPI(url_config: dict, url_json: string, response: string)

url_config permits to set up specific data or json file for each url
and method (get/post/patch/put/delete), also permits to simulate
http status_code in response.

url_config will be used to determine data to return instead of using json files:
using 'data' key
api = FakeAPI(url_config = {
    'GET https://example.com/api/subnet?cidr=192.160.0.0/24': {'data':
        {'result': [{'gateway':'192.168.0.1'}]}
    }
})

url_config can be used to put the status_code wanted in the response:
api = FakeAPI(url_config = {
    'GET https://example.com/api/subnet?cidr=192.160.0.0/24': {'status_code': 404}
})

url_config data can be loaded by json file specified in url_json.
"""
# pylint: disable=W0613,C0103,R0902,R0903

import json
import sys
from copy import copy
from urllib.parse import urlencode, urlparse, unquote_plus #, parse_qs, quote
from unittest.mock import MagicMock, patch
from requests.utils import requote_uri

UrlConfigHelperBase = object

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


class FakeResponse():
    """ Fake Response """
    status_code = 200
    ok          = True
    url         = None
    method      = None
    payload     = None
    params      = None
    content     = None
    reason      = None
    text        = None

    def json(self):
        """ return data """
        return json.loads(self.content)

class FakeAPI():
    """ Fake API from static json files """

    def __init__(self, url_config=None, url_json=None, returns='response'):
        """
            url_config optional dict to map urls to json files
            url_json path to json file containing url_config dict
            returns may be 'response' or 'json'
        """
        self.returns = returns
        self.set_config(url_config, url_json)
        self.reset_history()

    def set_config(self, url_config=None, url_json=None):
        """ Set url_config """
        self.url_config = url_config or {}
        if url_json:
            with open(url_json, 'r', encoding='utf-8') as jsf:
                self.url_config = json.load(jsf)

    def reset_history(self):
        """ Reset all calls history"""
        self.url_history = []
        self.url_history_full = []
        self.url_calls = {}
        self.responses = []


    def get_conf(self, method, url, params, data):
        """ retrieve conf for url in url_config """
        method = method.upper()
        url_key1 = get_url(url, params)
        url_key2 = get_url2(url, params)
        url_key3 = get_url(url_key1, data)
        url_key4 = get_url2(url_key2, data)
        self.url_history_full.append(f'{method} {url_key3}')
        print(f'fakeapi: Calling: {method} {url_key3}', file=sys.stderr)
        for url_k in list({url_key3, url_key4, url_key1, url_key2}):
            url_k = f'{method} {url_k}'
            if url_k in self.url_config:
                return self.url_config[url_k]
        print('fakeapi: No URL config found')
        return None

    def fake_call(self, method, url, data=None, params=None):
        """ load json file corresponding to url/method """
        response = FakeResponse()
        response.method = method
        response.params = params
        response.payload = data
        response.status_code = 201 if method == 'post' else 200
        response.url = get_url(url, params)
        url_method = f'{method.upper()} {response.url}'
        return_data = {}
        url_conf = self.get_conf(method, url, params, data)
        if url_conf:
            if 'status_code' in url_conf:
                response.status_code = url_conf['status_code']
            return_data = url_conf['data']
        response.text = json.dumps(return_data)
        response.content = json.dumps(return_data).encode('utf-8')
        response.ok = response.status_code < 400
        self.responses.append(copy(response))
        self.url_history.append(url_method)
        self.url_calls[url_method] = {
            'data': return_data,
            'status_code': response.status_code,
            'payload': data
        }
        if self.returns == 'json':
            return return_data
        return response

    def get(self, url, params=None, **kwargs):
        """ http get simulation """
        return self.fake_call('get', url, params=params)

    def post(self, url, data=None, params=None, **kwargs):
        """ http post simulation """
        return self.fake_call('post', url, data, params)

    def put(self, url, data=None, params=None, **kwargs):
        """ http put simulation """
        return self.fake_call('put', url, data, params)

    def patch(self, url, data=None, params=None, **kwargs):
        """ http patch simulation """
        return self.fake_call('patch', url, data, params)

    def delete(self, url, **kwargs):
        """ http delete simulation """
        return self.fake_call('delete', url)

    def mock_class(self, apicli):
        """ to be called in unittest.TestCase.setUp() """
        apicli.get    = MagicMock(side_effect=self.get)
        apicli.post   = MagicMock(side_effect=self.post)
        apicli.patch  = MagicMock(side_effect=self.patch)
        apicli.put    = MagicMock(side_effect=self.put)
        apicli.delete = MagicMock(side_effect=self.delete)
        return apicli

    def patch_method(self, test_case, module, method):
        """ mock module method """
        patcher = patch(f'{module}.{method}', side_effect=getattr(self, method))
        mock = patcher.start()
        test_case.addCleanup(patcher.stop)
        return mock

    def mock_module(self, test_case, module):
        """
            setup mocks for module (requests)
            to be called in unittest.TestCase.setUp()
            self.mocks = self.fakeapi.mock_module(self, 'apicli.requests')
            in tests use:
            self.mocks.get.assert_called_with()
        """
        mocks = MockAPI()
        for method in ['get', 'post', 'put', 'patch', 'delete']:
            setattr(mocks, method, self.patch_method(test_case, module, method))
        return mocks

class MockAPI:
    """mocks for requests calls"""
    get = None
    post = None
    put = None
    patch = None
    delete = None
