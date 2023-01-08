"""
FakeAPI class to simulate rest API calls from json static files/data
Usefull to easily mock requests or api-client (APIClient) in unittest

api = FakeAPI(url_config: dict, response: string)

url_config permits to set up specific data or json file for each url
and method (get/post/patch/put/delete), also permits to simulate
http status_code in response.

You can put the json test sets response files in:
fixtures/<api endpoint>/<method>.json
<api endpoint>: url to call without 'https://'
<method>: get / post / put / patch / delete
Example:
fixtures/example.com/api/v1/users/get.json
fixtures/example.com/api/v1/users/post.json

As url can contains characters that cannot be used in path name (mostly on Windows OS),
- fakeapi removes server port from url (example.com:8443 => example.com)
- fakeapi is trying non encoded urls and encoded urls to get path name to json file.
- fakeapi it trying file name replacing ? and & chars with # (windows can't have ?& in file names)
json file to perform get from url 'https://example.com:8443/v1/users?search=My search&foo=/bar'
will be taken from either :
'fixtures/example.com/api/v1/users?name=Joe Man&foo=/bar/get.json'
'fixtures/example.com/api/v1/users#name=Joe Man&foo=/bar/get.json'
'fixtures/example.com/api/v1/users?name=Joe+Man&foo=%2Fbar/get.json'
'fixtures/example.com/api/v1/users#name=Joe+Man#foo=%2Fbar/get.json'
(not that + stands for space character, not %20 !)

The json file names can also be specified using url_config for each <url>/<method>:

api = FakeAPI(url_config = {
    'https://example.com/api/subnet?cidr=192.160.0.1/21/get':
        {'json': 'example.com/api/v1/subnet_cidr.json'}
})
the url key can be url encoded ('https://example.com/api/subnet?cidr=192.160.0.1%2F21/get')

url_config can also be used to determine directly data to return instead of using json files:
using 'data' key
api = FakeAPI(url_config = {
    'https://example.com/api/subnet?cidr=192.160.0.0/24': {'data':
        {'result': [{'gateway':'192.168.0.1'}]}
    }
})

url_config can be used to put the status_code wanted in the response:
api = FakeAPI(url_config = {
    'https://example.com/api/subnet?cidr=192.160.0.0/24': {'status_code': 404}
})

"""
# pylint: disable=W0613

import json
import re
import os.path
from urllib.parse import urlencode, unquote_plus
from unittest.mock import MagicMock, patch

class FakeResponse():
    """ Fake Response """
    data        = None
    status_code = 200
    url         = None
    method      = None
    payload     = None
    params      = None
    content     = None
    reason      = None
    text        = None

    def json(self):
        """ return data """
        return self.data

class FakeAPI():
    """ Fake API from static json files """
    response = FakeResponse()

    def __init__(self, url_config=None, returns='response'):
        """
            jsmocks optional dict to map urls to json files
            returns may be 'response' or 'json'
        """
        self.url_config = url_config or {}
        self.returns = returns

    def fake_call(self, method, url, data=None, params=None):
        """ load json file corresponding to url/method """
        self.response.method = method
        self.response.params = params
        self.response.payload = data
        self.response.status_code = 201 if method == 'post' else 200
        query_simple = ''
        query_encoded = ''
        if params:
            query_encoded = '?' + urlencode(params)
            query_simple = '?' + unquote_plus(urlencode(params))
        for query in list({query_simple, query_encoded}):
            full_url = url + query
            print(f'Calling: {method} {full_url}')
            self.response.url = full_url
            return_data = {}
            json_file = None
            url_conf = None
            if f'{full_url}/{method}' in self.url_config:
                url_conf = self.url_config[f'{full_url}/{method}']
                if 'json' in url_conf:
                    json_file = url_conf['json']
            elif full_url in self.url_config:
                url_conf = self.url_config[full_url]
                if 'json' in url_conf:
                    json_file = f"{url_conf['json']}/{method}.json"
            if url_conf:
                if 'status_code' in url_conf:
                    self.response.status_code = url_conf['status_code']
                if 'data' in url_conf:
                    return_data = url_conf['data']
                    break
            # automatic mapping to url/method.json file to get return_data
            if not json_file:
                json_file = re.sub('^[^/]*://','', full_url)           # remove scheme (http://)
                json_file = re.sub('^([^/]*):[0-9]*','\\1', json_file) # remove port (:8080)
                json_file += f'/{method}.json'
            json_file = f'fixtures/{json_file}'
            print(f"Info: Looking data in {json_file}")
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as jsf:
                    return_data = json.load(jsf)
                break
            json_file = re.sub('[?&]','#', json_file) # Windows can't jump
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as jsf:
                    return_data = json.load(jsf)
                break
            # print('Not found')
        self.response.data = return_data
        self.response.content = json.dumps(return_data)
        if self.returns == 'json':
            return return_data
        return self.response

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
