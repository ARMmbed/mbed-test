"""
Copyright 2016 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

'''
REST API methods for use with mbedtest. Implements GET, PUT, POST and DELETE methods for now.
Also includes helper functions to set values for default headers, cert and host address.

Basic logger also included, can be easily replaced by custom loggers when constructing HttpApi object or later with setter
'''

import jsonmerge
import requests
import logging
from requests import RequestException


# Schema to make sure header fields are overwritten
schema = {
    "properties": {
        "mergeStrategy": "overwrite"
    }
}


def initLogger():
    '''
    Initializes a basic logger for use with the API. Can be replaced when constructing the HttpApi object or afterwards with setter
    '''
    logger = logging.getLogger("HttpApi")
    logger.setLevel(logging.INFO)
    #Skip attaching StreamHandler if one is already attached to logger
    if not getattr(logger, "streamhandler_set", None):
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)
        logger.streamhandler_set = True
    return logger



class HttpApi(object):
    def __init__(self, host, defaultHeaders=None, cert=None, logger=None):
        self.logger = initLogger() if logger is None else logger
        self.defaultHeaders = {} if defaultHeaders is None else defaultHeaders
        self.host = host
        self.cert = cert
        self.logger.info("HttpApi initialized")

    def setLogger(self, logger):
        '''Sets a custom logger that is to be used with the HttpApi class.

        :param logger: custom logger to use to log HttpApi log messages
        :return: Nothing
        '''
        self.logger = logger

    def set_header(self, key, value):
        '''Sets a new value for a header field in defaultHeader. Replaces old value if the key already exists
        :param key: HTTP header key name
        :param value:HTTP header key value
        :return: Nothing, modifies defaultHeaders in place
        '''
        self.defaultHeaders[key] = value

    def setCert(self, cert):
        '''Setter for certificate field. Valid values are either a string containing path to certificate .pem file
        or Tuple, ('cert', 'key') pair.

        :param cert: Valid values are either a string containing path to certificate .pem file
                    or Tuple, ('cert', 'key') pair.
        :return: Nothing, modifies field in place
        '''

        self.cert = cert

    def setHost(self, host):
        '''Setter for host parameter

        :param host: address of HTTP service
        :return: Nothing, modifies field in place
        '''

        self.host = host

    def get(self, path, headers=None, params=None, **kwargs):
        '''Sends a GET request to host/path
        :param path: String, Resource path on server
        :param params: Dictionary of parameters to be added to URL
        :param headers: Dictionary of HTTP headers to be sent with the request, overwrites default headers if there is overlap
        :param kwargs: Other arguments used in the requests.request call
            valid parameters in kwargs are the optional parameters of Requests.Request http://docs.python-requests.org/en/master/api/
        :return: requests.Response
        :raises: RequestException
        '''

        if headers is not None:
            merger = jsonmerge.Merger(schema)
            kwargs["headers"] = merger.merge(self.defaultHeaders, headers)
        else:
            kwargs["headers"] = self.defaultHeaders

        if self.cert is not None:
            kwargs["cert"] = self.cert

        if params is None:
            params = {}

        url = self.host + path
        self.logger.debug("Trying to send HTTP GET to {}".format(url))
        try:
            resp = requests.get(url, params, **kwargs)
            self.logger.debug("Server responded with {}".format(resp.status_code))
        except RequestException as es:
            self.logger.error("Exception when performing request: {}".format(es))
            raise
        return resp

    def post(self, path, data=None, json=None, headers=None, **kwargs):
        '''Sends a POST request to host/path
        :param path: String, resource path on server
        :param data: Dictionary, bytes or file-like object to send in the body of the request
        :param json: JSON formatted data to send in the body of the request
        :param headers: Dictionary of HTTP headers to be sent with the request, overwrites default headers if there is overlap
        :param kwargs: Other arguments used in the requests.request call
            valid parameters in kwargs are the optional parameters of Requests.Request http://docs.python-requests.org/en/master/api/
        :return: requests.Response
        :raises: RequestException
        '''

        if headers is not None:
            merger = jsonmerge.Merger(schema)
            kwargs["headers"] = merger.merge(self.defaultHeaders, headers)
        else:
            kwargs["headers"] = self.defaultHeaders

        url = self.host + path
        if self.cert is not None:
            kwargs["cert"] = self.cert
        self.logger.debug("Trying to send HTTP POST to {}".format(url))
        try:
            resp = requests.post(url, data, json, **kwargs)
            self.logger.debug("Server responded with {}".format(resp.status_code))
        except RequestException as es:
            self.logger.error("Exception when performing request: {}".format(es))
            raise

        return resp

    def put(self, path, data=None, headers=None, **kwargs):
        '''Sends a PUT request to host/path
        :param path: String, resource path on server
        :param data: Dictionary, bytes or file-like object to send in the body of the request
        :param headers: Dictionary of HTTP headers to be sent with the request, overwrites default headers if there is overlap
        :param kwargs: Other arguments used in the requests.request call
            valid parameters in kwargs are the optional parameters of Requests.Request http://docs.python-requests.org/en/master/api/
        :return: requests.Response
        :raises: RequestException
        '''

        if headers is not None:
            merger = jsonmerge.Merger(schema)
            kwargs["headers"] = merger.merge(self.defaultHeaders, headers)
        else:
            kwargs["headers"] = self.defaultHeaders

        url = self.host + path
        if self.cert is not None:
            kwargs["cert"] = self.cert
        self.logger.debug("Trying to send HTTP PUT to {}".format(url))
        try:
            resp = requests.put(url, data, **kwargs)
            self.logger.debug("Server responded with {}".format(resp.status_code))
        except RequestException as es:
            self.logger.error("Exception when performing request: {}".format(es))
            raise

        return resp

    def delete(self, path, headers=None, **kwargs):
        '''Sends a DELETE request to host/path
        :param path: String, resource path on server
        :param headers: Dictionary of HTTP headers to be sent with the request, overwrites default headers if there is overlap
        :param kwargs: Other arguments used in the requests.request call
            valid parameters in kwargs are the optional parameters of Requests.Request http://docs.python-requests.org/en/master/api/
        :return: requests.Response
        :raises: RequestException
        '''

        if headers is not None:
            merger = jsonmerge.Merger(schema)
            kwargs["headers"] = merger.merge(self.defaultHeaders, headers)
        else:
            kwargs["headers"] = self.defaultHeaders

        url = self.host + path
        if self.cert is not None:
            kwargs["cert"] = self.cert
        self.logger.debug("Trying to send HTTP DELETE to {}".format(url))
        try:
            resp = requests.delete(url, **kwargs)
            self.logger.debug("Server responded with {}".format(resp.status_code))
        except RequestException as es:
            self.logger.error("Exception when performing request: {}".format(es))
            raise

        return resp

