#!/bin/env python3
""" test """
import unittest
import json
import requests
from apiclient import APIClient
from fakeapi import FakeAPI, get_url, get_url2

url_config = {
    'GET http://localhost/api': {
        'status_code': 200,
        'data': {'message': 'Call successfull'}
    },
    'GET http://localhost/api?test=yop%20man': {
        'status_code': 200,
        'data': {'message': 'Call successfull'}
    },
    'GET http://localhost/api?t=yop man/yop&test=yop man/yop': {
        'status_code': 400,
        'data': {'message': 'query ok'}
    },
    'GET azezazhttp://localhost/api?t=yop%20man/yop&test=yop+man%2Fyop/get': {
        'status_code': 400,
        'data': {'message': 'query ok'}
    },
    'POST http://localhost/api?name=foo bar': {
        'data': {'message': 'foo bar created'}
    },
    'PATCH http://localhost/api/1?name=foo%2Fbar': {
        'status_code': 404,
        'data': {'message': 'failed to update: no item with id 1'}
    },
    'PUT http://localhost/api?id=1&name=foo/bar': {
        'status_code': 200,
        'data': {'message': 'record updated'}
    },
    'DELETE http://localhost/api/1': {
        'status_code': 200,
        'data': None,
    },
}

def printjs(data):
    """ print data in json"""
    print(json.dumps(data, indent=2))


def other_tests(api):
    """ debug tests """
    r1 = api.get('http://localhost/api')
    r2 = api.get('http://localhost/api?test=yop man')
    print(r1.url)
    printjs(api.get('http://localhost/api').json())
    printjs(api.get('http://localhost/api?test=yop man').json())
    printjs(api.get('http://localhost/api?t=yop man/yop', {'test': 'yop man/yop'}).json())

    printjs(api.url_history)
    #printjs(api.url_calls)

    response = requests.get('https://reqres.in/api/users/1?q=toto titi/yop',
                            {'q2':'toto titi/yop'}, timeout=2)
    print(response.url)
    print(get_url('https://reqres.in/api/users/1?q=toto titi/yop', {'q2':'toto titi/yop'}))
    print(get_url('http://localhost/api?t=yop man/yop', {'test': 'yop man/yop'}))
    print(get_url2('https://reqres.in/api/users/1?q=toto titi/yop', {'q2':'toto titi/yop'}))
    print(get_url2('http://localhost/api?t=yop man/yop', {'test': 'yop man/yop'}))

    #print(requests.utils.requote_uri('https://reqres.in/api/users/1?q=toto titi'))
    #print(requests.utils.requote_uri('https://reqres.in/api/users/1?q=toto titi/cho'))

class UnitTest(unittest.TestCase):
    """ testing fakeapi """
    api = FakeAPI(url_config)

    def test1_fakeapi(self):
        """ test GET http://localhost/api """
        url = 'http://localhost/api'
        url1 = get_url(url, None)
        print(url1)
        self.assertEqual(url1, url)
        url2 = get_url2(url, None)
        self.assertEqual(url2, url)
        url_method = f'GET {url1}'
        url_conf = self.api.get_conf('get', url, None, None)
        self.assertEqual(url_conf, url_config[url_method])
        response = self.api.get(url)
        print(response.ok)
        self.assertTrue(response.ok)
        print(response.status_code)
        self.assertEqual(response.status_code, 200)
        print(response.url)
        self.assertEqual(response.url, url1)
        print(response.text)
        self.assertEqual(response.text, json.dumps(url_conf['data']))
        printjs(response.json())
        self.assertEqual(response.json(), url_conf['data'])
        printjs(self.api.url_history)
        self.assertEqual(self.api.url_history, [url_method])
        printjs(self.api.url_calls)
        self.assertEqual(self.api.url_calls[url_method], {
            "data": url_conf['data'],
            "status_code": 200,
            "payload": None,
        })
        self.assertEqual(len(self.api.responses), 1)
        self.assertEqual(self.api.responses[0].url, response.url)

    def test2_fakeapi(self):
        """ test POST http://localhost/api """
        url = "http://localhost/api"
        data = {'name':'foo bar'}
        url1 = get_url(url, data)
        print(url1)
        self.assertEqual(url1, f'{url}?name=foo+bar')
        url2 = get_url2(url, data)
        print(url2)
        self.assertEqual(url2, f'{url}?name=foo bar')
        url_method = f'POST {url2}'
        url_conf = self.api.get_conf('post', url, None, data)
        self.assertEqual(url_conf, url_config[url_method])
        response = self.api.post(url, data)
        self.assertTrue(response.ok)
        print(response.text)

    def test3_fakeapi(self):
        """ test PATCH """
        url = "http://localhost/api/1"
        data = {'name':'foo/bar'}
        url1 = get_url(url, data)
        print(url1)
        self.assertEqual(url1, f'{url}?name=foo%2Fbar')
        url2 = get_url2(url, data)
        print(url2)
        self.assertEqual(url2, f'{url}?name=foo/bar')
        url_method = f'PATCH {url1}'
        url_conf = self.api.get_conf('patch', url, None, data)
        self.assertEqual(url_conf, url_config[url_method])
        response = self.api.patch(url, data)
        self.assertFalse(response.ok)
        print(response.status_code)
        self.assertEqual(response.status_code, 404)
        print(response.text)

    def test4_fakeapi(self):
        """ test PUT """
        url = "http://localhost/api"
        data = {'name':'foo/bar'}
        params = {'id':1}
        url1 = get_url(url, params)
        print(url1)
        self.assertEqual(url1, f'{url}?id=1')
        url1 = get_url(url1, data)
        self.assertEqual(url1, f'{url}?id=1&name=foo%2Fbar')
        url2 = get_url2(url, params)
        url2 = get_url2(url2, data)
        print(url2)
        self.assertEqual(url2, f'{url}?id=1&name=foo/bar')
        url_method = f'PUT {url2}'
        url_conf = self.api.get_conf('put', url, params, data)
        self.assertEqual(url_conf, url_config[url_method])
        response = self.api.put(url, data, params)
        self.assertTrue(response.ok)
        print(response.status_code)
        self.assertEqual(response.status_code, 200)
        print(response.text)

    def test5_fakeapi(self):
        """ test DELETE """
        url = 'http://localhost/api/1'
        response = self.api.delete(url)
        self.assertTrue(response.ok)

    def test6_fakeapi(self):
        """ test other """
        response = self.api.get('http://toto')
        print(response.text)
        self.api.set_config(url_json='tests/test.json')
        self.assertIn("GET http://localhost/api/test.json", self.api.url_config)


class MyClient(APIClient):
    """ client api """
    def call_api(self):
        """ http get """
        return self.get('http://localhost/api').json()

class TestMyClient(unittest.TestCase):
    """ Unit Testing mocking MyClient get/post/put/patch """
    fakeapi = FakeAPI({'GET http://localhost/api': {'data': {'message': 'Call successfull'}}})
    apicli = MyClient()

    def setUp(self):
        """ Mock API calls """
        self.apicli = self.fakeapi.mock_class(self.apicli)

    def test1_call_api(self):
        """ test_call_api """
        data = self.apicli.call_api()
        self.apicli.get.assert_called_with('http://localhost/api')
        print(data)


# mock_module test
def call_api():
    """ simple http get """
    response = requests.get('http://localhost/api', timeout=60)
    return response.json()

class TestCallAPI(unittest.TestCase):
    """ test mock module """
    fakeapi = FakeAPI({'GET http://localhost/api': {'data': {'message': 'Call successfull'}}})
    def setUp(self):
        """ mock 'mycli.requests' get/post/patch/put/delete calls to fakeapi """
        self.mocks = self.fakeapi.mock_module(self, 'requests')

    def test2_call_api(self):
        """ test call_api"""
        data = call_api()   # requests calls are mocked to fakeAPI
        self.mocks.get.assert_called_with('http://localhost/api', timeout=60)
        print(data)


if __name__ == "__main__":
    unittest.main(failfast=True, verbosity=2)
