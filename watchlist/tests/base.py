from StringIO import StringIO
from mocker import ARGS
from mocker import KWARGS
from mocker import MockerTestCase
from requests import Response


HTTP_REASONS = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Time-out",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Large",
    415: "Unsupported Media Type",
    416: "Requested range not satisfiable",
    417: "Expectation Failed",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Time-out",
    505: "HTTP Version not supported",
    }


class RequestsResponseStub(Response):
    """Stubs responses of the `requests` lib.
    """

    def __init__(self, status_code=200, text='', headers=None,
                 reason=None):
        super(RequestsResponseStub, self).__init__()
        self.status_code = status_code
        self.raw = StringIO(text)
        self.raw.reason = reason or HTTP_REASONS[status_code]

        default_headers = {
            'x-ratelimit-remaining': -1,
            'link': None}

        if headers:
            default_headers = default_headers.copy()
            default_headers.update(headers)

        self.headers = default_headers


class GithubMockTestCase(MockerTestCase):

    def setUp(self):
        super(MockerTestCase, self).setUp()

        # somehow replacing directly does not work here,
        # so we create another stub..
        self.request = self.mocker.mock()
        req_method = self.mocker.replace(
            'requests.sessions.Session.request')
        self.expect(req_method(ARGS, KWARGS)).call(
            self.request).count(0, None)
