#   Copyright 2013 Nebula Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""HTTP utilities"""

import json
import logging
import requests


USER_AGENT = 'python-openstackclient'

_logger = logging.getLogger(__name__)


def request(method, url, **kwargs):
    """Common wrapper for making HTTP requests

    Handles common headers and JSON encoding
    """
    # FIXME(dtroyer): Used for making direct REST API calls before the client
    #                 objects have been initialized, specifically in API
    #                 version negotiation.  Should be replaced with direct
    #                 calls to the common apiclient lib once it has been
    #                 adopted.
    kwargs.setdefault('headers', kwargs.get('headers', {}))
    if 'User-Agent' not in kwargs['headers']:
        kwargs['headers']['User-Agent'] = USER_AGENT
    if 'Content-Type' not in kwargs['headers']:
        kwargs['headers']['Content-Type'] = 'application/json'
    if 'data' in kwargs and isinstance(kwargs['data'], type({})):
        kwargs['data'] = json.dumps(kwargs['json'])
    log_request(method, url, kwargs)
    resp = requests.request(method, url, **kwargs)
    log_response(resp)
    return resp


def log_request(method, url, kwargs):
    string_parts = [
        "curl -i",
        "-X '%s'" % method,
        "'%s'" % url,
    ]

    for element in kwargs['headers']:
        header = " -H '%s: %s'" % (element, kwargs['headers'][element])
        string_parts.append(header)

    _logger.debug("REQ: %s" % " ".join(string_parts))
    if 'data' in kwargs:
        _logger.debug("REQ BODY: %s\n" % (kwargs['data']))


def log_response(resp):
    _logger.debug(
        "RESP: [%s] %s\n",
        resp.status_code,
        resp.headers,
    )
    if resp._content_consumed:
        _logger.debug(
            "RESP BODY: %s\n",
            resp.text,
        )
