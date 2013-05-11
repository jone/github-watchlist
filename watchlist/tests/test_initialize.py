from requests import HTTPError
from watchlist.initialize import OAuthTokenCreator
from watchlist.tests.base import GithubMockTestCase
from watchlist.tests.base import RequestsResponseStub
from watchlist.tests.github import authorization_token_data
import json


class TestOAuthTokenCreator(GithubMockTestCase):

    def test_oauth_token_is_created_and_returned(self):
        token = '80fff6600885bb75ac5f6a32cfdce60d'
        username = 'john.doe'
        password = 'very secret!'

        self.expect_creates_github_authorization_token(
            username=username, password=password, token=token)

        self.mocker.replay()

        self.assertEquals(token, OAuthTokenCreator().create_token(username, password))

    def test_exception_raised_with_invalid_credentials(self):
        username = 'john.doe'
        password = 'wrong password'

        self.expect_unauthorized_exception_with_wrong_credentials(
            username=username, password=password)

        self.mocker.replay()

        with self.assertRaises(HTTPError) as cm:
            OAuthTokenCreator().create_token(username, password)

        self.assertEquals('401 Client Error: Unauthorized',
                          str(cm.exception))

    def expect_creates_github_authorization_token(self, username, password, token):
        request_data = {'scopes': ['notifications'],
                        'note': 'github-watchlist'}
        response_data = authorization_token_data(token)

        self.request(method='post', url='https://api.github.com/authorizations',
                     auth=(username, password), data=json.dumps(request_data))
        self.mocker.result(RequestsResponseStub(text=json.dumps(response_data)))

    def expect_unauthorized_exception_with_wrong_credentials(self, username, password):
        request_data = {'scopes': ['notifications'],
                        'note': 'github-watchlist'}
        self.request(method='post', url='https://api.github.com/authorizations',
                     auth=(username, password), data=json.dumps(request_data))
        self.mocker.result(RequestsResponseStub(status_code=401))
