# fakeapi
Faking/Mocking API Rest Call requests

Faking API calls using static fixtures json with FakeAPI class.  
Mocking API calls using FakeAPI get/post/patch/delete methods.  

# FakeAPI class

Fakes http requests calls (get/post/put/patch/delete).  
Instead of doing http calls to urls, FakeAPI class will returns response with data from url dict data or json files.  
Can be used during development of Application that must use 3rd party API without actually calling the API, but using static tests sets data for url calls.

Another purpose is to use FakeAPI class to mock http requests when doing Unit testing of application that is using 3rd party API calls (the tests won't actually call the 3rd party API that is not to be tested)

## Quick examples:
>```python
>>>> from fakeapi import FakeAPI
>>>> api = FakeAPI({
>  'http://localhost/api': {
>    'status_code': 200,
>    'data': {
>      'message': 'Call successfull'
>    }
>  }
>})
>>>> response = api.get('http://localhost/api')
>>>> response.status_code
>200
>>>> response.json()
>{'message': 'Call successfull'}
>```

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
>  fakeapi = FakeAPI({'http://localhost/api': {'data': {'message': 'Call successfull'}}})
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
instead of passing data using FakeAPI(), data can be automatically get from json files located in:
`fixtures/<url>/<method>.json`  
In the example, the json file has to be located in :
`fixtures/localhost/api/get.json`

> **`fixtures/localhost/api/get.json:`**  
>```json
>{"message": "Call successfull"}
>```

>```python
>>>> from fakeapi import FakeAPI
>>>> api = FakeAPI()
>>>> api.get("http://localhost/api").json()
>{"message": "Call successfull"}
>```

This will make easy to create full test sets of the different API paths.

## Usage

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
* passing FakeAPI url_config parameter with data: `api = FakeAPI(url_config={'url':{'data':{...}},...})`
* passing FakeAPI url_config parameter with json file/dir: `api = FakeAPI(url_config={'url':{'json':'jsonfile'},...})`
  * FakeAPI.url_config property can be modified after creation
  * specific data/json for method using key : 'url/method'
* Using automatic url mapping to json files, FakeAPI will get data from `fixtures/<url>/<method>.json`

## Using url_config

Each different url calls can be configured in url_config to provide specific status_code or data.

Providing data in url_config for url
```python
  '<url>[/<method>]': {
    'status_code': <status_code>,
    'data': <url_data>
  }
```
* `<url>         `: full url that is called (with query string)
* `<method>      `: http method : get/post/put/patch/delete
* `<status_code> `: http code to return in repsonse (200/201/404/500...)
* `<url_data>    `: data to retrieve for url call on method.

When a request method occurs on `<url>` if the key `<url>/<method>` has a entry in url_config, returns 'data'/'status_code' if defined.  
Else if the `<url>` key found in url_config, will returns 'data'/'status_code' if defined for all methods calls.

Providing data using json file path:
```python 
  '<url>[/<method>]': {
    'status_code': <status_code>,
    'json': <path to json file/directory>
  }
```
if 'json' is defined for `<url>/<method>`, the data will be retrieved from json file in `fixtures/<path to json file>`.  
if 'json' is defined for `<url>`, the data will be retrieve from json directoy in `fixtures/<path to json dir>/<method>.json`.

Example:
```python
api = FakeAPI(url_config={
  'http://localhost/api/get': {
    'status_code': 200,
    'data': {'message':'successfull'}
  },
  'http://localhost/api/users': {
    'status_code': 200,
    'json': 'api/users'
  },
  'http://localhost/api/users?name=foo/get': {
    'status_code': 200,
    'json' : 'api/users_foo.json'
  }
})
```

## Automatic url/method mapping to json files

Instead of using url_config, FakeAPI will automatically search for json data files according to url.  
As characters are restricted in file names on different OSes, the following search is done to create matching file path from url/method:
* removed scheme (http://, https://...)
* removed server port (localhost:8443 => localhost)
* base directory is cwd/fixtures
* url encoded and not encoded will be checked
* characters ? and & substituted to # will be checked  

call to : `get 'http://localhost:8443/api/tests?search=my search@test&limit=5'`  
will be automatically mapped to the following file names:  
* `fixtures/localhost/api/test?search=my search@test&limit=5/get.json`  
* `fixtures/localhost/api/test?search=my+search%40test&limit=5/get.json`
* `fixtures/localhost/api/test#search=my+search%40test#limit=5/get.json`

## Summary url / data mapping
When a request to a url is done, FakeAPI will get data from:
* `<url>/<method>` in url_config
  * 'data' defined returns data
  * 'json' defined returns json file data
* `<url>` in url_config
  * 'data' defined returns dat`
  * 'json' defined returns `json directory/<method>.json` data
* when no 'data' or 'json' found for 'url'/'url/method' in url_config:
  * Automatic mapping of url/method to json files:
  

## FakePI returns FakeResponse or json

FakeAPI methods by default returns `FakeResponse` with following :
* status_code = 200/201 (for post) or status_code defined in url_config
* url : url called
* content : json text
* json() : return json from json file corresponding to url / method

`fakeapi = FakeAPI(returns='json')` is to be used to return directly 'json', instead of response.  
To be used with api-client module class APIClient(response_handler=JsonResponseHandler) as get/post/patch/delete returns directly json() from response.


## Mocking http requests using FakeAPI

Mocking can be done using mock_module or mock_class methods in unittest.TestCase.setUp() method.

Example to mock requests with api-client APIClient():
```python
mycli.py:
from apiclient import APIClient
class MyClient(APIClient):
  def call_api():
    return self.get('http://localhost/api').json()
```

```python
import unittest
from fakeapi import FakeAPI
from mycli import MyClient
class UnitTest(unittest.TestCase):
    """ Unit Testing mocking MyClient get/post/put/patch """
    fakeapi = FakeAPI()
    apicli = MyClient()

    def setUp(self):
        """ Mock API calls """
        self.apicli = self.fakeapi.mock_class(self.apicli)

    def test_call_api(self):
        """ test_call_api """
        response = self.apicli.call_api()
        self.apicli.get.assert_called_with('http://localhost/api')
        print(response.json())
```