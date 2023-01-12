""" urlconfighelper """
# pylint: disable=W0613,E0239
import json
import fakeapi
UrlConfigHelperBase = fakeapi.UrlConfigHelperBase

class DynClass():
    """ create class of type """
    def __new__(cls, base_class, *args, **kwargs):
        """ set class from base_class """
        return base_class

class UrlConfigHelper(DynClass(UrlConfigHelperBase)):
    """
    Class will derive from urlconfighelper_base
    Class to contruct url_config from real API calls
    to create test sets
    """
    url_config = {}

    def _call(self, method, url, params=None, data=None, **kwargs):
        """
        call super().method with params
        add returned urls/data in url_config
        """
        call = getattr(super(), method)
        response = call(url, data=data, params=params, **kwargs)
        url = fakeapi.get_url(response.url, data)
        self.url_config[f'{method.upper()} {url}'] = {
            'status_code': response.status_code,
            'data': response.json() if response.content else None,
            'payload': data
        }
        return response

    def save_urlconfig(self, json_file):
        """ save url_config to json file """
        with open(json_file, 'w', encoding='utf-8') as jsf:
            json.dump(self.url_config, jsf, indent=2)

    def get(self, url, params=None, **kwargs):
        """ supercharge get """
        return self._call('get', url, params, **kwargs)

    def post(self, url, data=None, params=None, **kwargs):
        """ supercharge post """
        return self._call('post', url, params, data, **kwargs)

    def put(self, url, data=None, params=None, **kwargs):
        """ supercharge put """
        return self._call('put', url, params, data, **kwargs)

    def patch(self, url, data=None, params=None, **kwargs):
        """ supercharge patch """
        return self._call('patch', url, params, data, **kwargs)

    def delete(self, url, **kwargs):
        """ supercharge delete """
        return self._call('delete', url, **kwargs)
