from StringIO import StringIO
from mocker import ARGS
from mocker import KWARGS
from mocker import MockerTestCase
from requests import Response
from watchlist.github import make_github_url
from watchlist.tests import github
import json


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


class StubConfig(object):

    def __init__(self, user=None, token=None, watchlist=None):
        self.github_login = user or 'john'
        self.github_oauth_token = token or '123asdfX'
        self.watchlist = watchlist or []


class RequestsResponseStub(Response):
    """Stubs responses of the `requests` lib.
    """

    def __init__(self, status_code=200, text='', headers=None,
                 reason=None):
        super(RequestsResponseStub, self).__init__()
        self.status_code = status_code
        self.raw = StringIO(text)
        self.reason = reason or HTTP_REASONS[status_code]

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

        self.get_request = self.mocker.replace('requests.get')

        self.github_user_orgs = set([])
        self.github_repos = {}
        self.github_subscriptions = set([])

    def given_user_is_in_organisations(self, *organisations):
        self.github_user_orgs.update(organisations)

    def given_repositories(self, *repositories):
        for full_name in repositories:
            login, name = full_name.split('/')

            if login not in self.github_repos:
                self.github_repos[login] = []

            self.github_repos[login].append(full_name)

    def given_subscriptions(self, *repositories):
        self.github_subscriptions.update(repositories)

    def reckon_github_read_requests(self):
        self.stub_github_request(
            'user/subscriptions', github.repositories(self.github_subscriptions))

        self.stub_github_request(
            'user/orgs', github.organisations(self.github_user_orgs))

        for login, repositories in self.github_repos.items():
            if login == 'john.doe':
                path = 'user/repos'
            else:
                path = 'orgs/%s/repos' % login

            self.stub_github_request(path, github.repositories(repositories))

    def expect_subscription_created(self, reponame):
        watch_payload = json.dumps({'subscribed': True, 'ignored': False})

        self.mock_github_request(
            '%s/subscription' % reponame,
            github.subscription(reponame),
            method='put',
            payload=watch_payload)

    def expect_subscription_deleted(self, reponame):
        self.mock_github_request('%s/subscription' % reponame, '', method='delete')

    def stub_github_request(self, path, response_text, method='get', config=None,
                            response_headers=None, response_status_code=200,
                            payload=None, count=False):
        url = make_github_url(path, StubConfig())
        response = RequestsResponseStub(text=response_text, headers=response_headers,
                                        status_code=response_status_code)

        kwargs = {}
        if payload:
            kwargs['data'] = payload

        if method == 'get':
            self.get_request(url, **kwargs)
        else:
            self.request(method=method, url=url, **kwargs)

        self.mocker.result(response)
        if not count:
            self.mocker.count(0, None)

    def mock_github_request(self, *args, **kwargs):
        kwargs['count'] = True
        return self.stub_github_request(*args, **kwargs)
