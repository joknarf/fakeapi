[![Travis CI](https://travis-ci.com/joknarf/fakeapi.svg?branch=main)](https://travis-ci.com/github/joknarf/fakeapi)
[![Codecov](https://codecov.io/github/joknarf/fakeapi/coverage.svg?branch=main)](https://codecov.io/gh/joknarf/fakeapi)
[![Upload Python Package](https://github.com/joknarf/fakeapi/workflows/Upload%20Python%20Package/badge.svg)](https://github.com/joknarf/fakeapi/actions?query=workflow%3A%22Upload+Python+Package%22)
[![Pypi version](https://img.shields.io/pypi/v/fakeapi.svg)](https://pypi.org/project/fakeapi/)
[![Downloads](https://pepy.tech/badge/fakeapi)](https://pepy.tech/project/fakeapi)
[![Python versions](https://img.shields.io/badge/python-3.6-blue.svg)](https://shields.io/)
[![Licence](https://img.shields.io/badge/licence-MIT-blue.svg)](https://shields.io/)

# fakeapi
Faking/Mocking API Rest Call requests

Faking API calls using static fixtures with FakeAPI class.  
Mocking API calls using FakeAPI get/post/patch/delete methods.  
Create HTTP server Rest API with a single json response file.

# FakeAPI class

Fakes http requests calls (get/post/put/patch/delete).  
Instead of doing http calls to urls, FakeAPI class will returns response with data from url dict data or json file.  
Can be used during development of Application that must use 3rd party API without actually calling the API, but using static tests sets data for url calls.

Another purpose is to use FakeAPI class to mock http requests when doing Unit testing of application that is using 3rd party API calls (the tests won't actually call the 3rd party API that is not to be tested)

FakeAPI class is also able to act as a HTTP Rest API server using a single json description of responses to calls.

## Quick examples:

### Start http server using `fakeapi_server` responding to 'GET http://localhost:8080/api'
```shell
$ fakeapi_server <<< '{ "GET http://localhost:8080/api": { "data": { "message": "Call successfull" }}}'
Starting http server : http://localhost:8080
127.0.0.1 - - [15/Jan/2023 13:00:20] GET localhost:8080/api
fakeapi: Calling: GET http://localhost:8080/api
127.0.0.1 - - [15/Jan/2023 13:00:20] "GET /api HTTP/1.1" 200 -
```

On Client side:  
```shell
$ curl http://localost:8080/api
{"message": "Call successfull"}
```

### Using FakeAPI class
```python
>>> from fakeapi import FakeAPI
>>> api = FakeAPI({
  'GET http://localhost/api': {
    'status_code': 200,
    'data': {
      'message': 'Call successfull'
    }
  }
})
>>> response = api.get('http://localhost/api')
>>> response.status_code
200
>>> response.json()
{'message': 'Call successfull'}
>>> api.http_server()
Starting http server : http://localhost:8080
...
```

FakeAPI class can easily mock requests calls in unittest.  
Usefull to test Application that is calling 3rd party API that is not to be tested.
>```python
>mycli.py:
>import requests
>
>def call_api():
>  response = requests.get('http://localhost/api')
>  return response.json()
>```
>```python
>test_mycli.py:
>import unittest, mycli
>from fakeapi import FakeAPI
>
>class TestMyCLI(unittest.TestCase):
>  fakeapi = FakeAPI({'GET http://localhost/api': {'data': {'message': 'Call successfull'}}})
>  def setUp(self):
>    # mock 'mycli.requests' get/post/patch/put/delete calls to fakeapi
>    self.mocks = self.fakeapi.mock_module(self, 'mycli.requests')
>  
>  def test_mycli(self):
>    data = mycli.call_api()   # requests calls are mocked to fakeAPI
>    self.mocks.get.assert_called_with('http://localhost/api')
>    print(data)
>
>if __name__ == "__main__":
>    unittest.main(failfast=True, verbosity=2)
>```
>```python
>$ python test_mycli.py
>test_mycli (__main__.TestMyCLI) ... {'message': 'Call successfull'}
>ok
>
>----------------------------------------------------------------------
>Ran 1 test in 0.002s
>
>OK
>```

## fakeapi_server usage

fakeapi_server is starting an http server responding to http calls defined in json description.
json url description :

```json
  "<METHOD> <url>": {
    "status_code": <status_code>,
    "data": <url_data>
  }
```

```shell
$ ./fakeapi_server -h
usage: fakeapi_server [-h] [-s SERVER] [-p PORT] [-P PREFIX] [jsonfile]

positional arguments:
  jsonfile              Json file for FakeAPI

options:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        HTTP server address
  -p PORT, --port PORT  HTTP server port
  -P PREFIX, --prefix PREFIX
                        HTTP prefix (http://server:port)
```

## FakeAPI class Usage

FakeAPI class defines the 5 methods:
* get
* post
* put
* patch
* delete

FakeAPI provides the mocking methods to be used in unittest.TestCase.setUp():
* mock_module(test_case: TestCase, module: str)
* mock_class(apicli: Object)

## Mapping Static data to urls calls

Instead of calling 3rd party API, FakeAPI will use static data (from dict or json files). 
static data can be defined several ways :
* passing FakeAPI url_config parameter with data: 
  * `api = FakeAPI(url_config={'METHOD url':{'data':{...}},...})`
* passing FakeAPI url_json parameter with json file containing url_config data: 
  * `api = FakeAPI(url_json='url_config.json')`
* FakeAPI.url_config property can be modified after creation

## Using url_config

Each different url calls can be configured in url_config to provide specific status_code or data.

Providing data in url_config for url
```json
  "<METHOD> <url>": {
    "status_code": <status_code>,
    "data": <url_data>
  }
```
* `<METHOD>      `: http method : GET/POST/PUT/PATCH/DELETE
* `<url>         `: full url that is called (with query string)
* `<status_code> `: http code to return in repsonse (200/201/404/500...)
* `<url_data>    `: data to retrieve for url call on method.

When a request method occurs on `<url>` if the key `<METHOD> <url>` has a entry in url_config, returns 'data'/'status_code' if defined.  

## FakePI returns FakeResponse or json

FakeAPI methods by default returns `FakeResponse` with following :
* status_code = 200/201 (for post) or status_code defined in url_config
* json() : return json from json file corresponding to METHOD url
* url : url called
* content : byte text
* text : text
* ok : True if status_code <400

`fakeapi = FakeAPI(returns='json')` is to be used to return directly 'json', instead of response.  
To be used with api-client module class APIClient(response_handler=JsonResponseHandler) as get/post/patch/delete returns directly json() from response.


## Mocking http requests using FakeAPI

Mocking can be done using mock_module or mock_class methods in unittest.TestCase.setUp() method.

Example to mock requests with api-client APIClient():
```python
mycli.py:
from apiclient import APIClient
class MyClient(APIClient):
  def call_api(self):
    return self.get('http://localhost/api').json()
```

```python
import unittest
from fakeapi import FakeAPI
from mycli import MyClient
class UnitTest(unittest.TestCase):
    """ Unit Testing mocking MyClient get/post/put/patch """
    fakeapi = FakeAPI({'GET http://localhost/api': {'data': {'message': 'Call successfull'}}})
    apicli = MyClient()

    def setUp(self):
        """ Mock API calls """
        self.apicli = self.fakeapi.mock_class(self.apicli)

    def test_call_api(self):
        """ test_call_api """
        data = self.apicli.call_api()
        self.apicli.get.assert_called_with('http://localhost/api')
        print(data)
```

## Generating test sets 

To have url_config corresponding to API calls, you can generate url_config from real calls to API, 
then use the result in your tests.

The urlconfighelper module can help, as can create a class derived from your class,
supercharging the get/post/put/pach/delete method to generate url_config for all calls.

You can then save the url_config containing all calls you made to a json file to be used as url_config in tests.

Example:
```python
""" Generate url_config for tests from MyClient real API calls """
import json
from mycli import MyClient
from fakeapi import UrlConfigHelper

api = UrlConfigHelper(MyClient)
api.call_api()    # make calls to the API and updates api.url_config
api.save_urlconfig('mytests.json')
print(json.dumps(api.url_config, indent=2))
```
