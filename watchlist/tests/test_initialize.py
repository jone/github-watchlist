from mocker import ANY
from requests import HTTPError
from watchlist.initialize import InitializeWatchlistConfiguration
from watchlist.initialize import OAuthTokenCreator
from watchlist.tests.base import GithubMockTestCase
from watchlist.tests.base import RequestsResponseStub
from watchlist.tests.github import authorization_token_data
import json
import os
import tempfile


class OAuthCreationTestCase(GithubMockTestCase):

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


class TestOAuthTokenCreator(OAuthCreationTestCase):

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


class TestInitializeWatchlistConfiguration(OAuthCreationTestCase):

    def setUp(self):
        super(TestInitializeWatchlistConfiguration, self).setUp()

        self.raw_input_mock = self.mocker.replace(raw_input)
        self.expect(self.raw_input_mock(ANY)).throw(
            AssertionError('Unexpected raw_input call')).count(0, None)

        self.getpass_mock = self.mocker.replace('getpass.getpass')
        self.expect(self.getpass_mock()).throw(
            AssertionError('Unexpected getpass call')).count(0, None)

    def test_integration_create_watchlist_configuration(self):
        with self.mocker.order():
            self.type_when_asked('john.doe', prompt='Your GitHub username: ')
            self.type_when_asked('wrong-password', prompt='Your GitHub password: ',
                                 hidden=True)

            self.expect_unauthorized_exception_with_wrong_credentials(
                username='john.doe', password='wrong-password')

            self.type_when_asked('correct-password', prompt='Your GitHub password: ',
                                 hidden=True)

            self.expect_creates_github_authorization_token(
                username='john.doe', password='correct-password', token='123asdf')

        self.mocker.replay()

        path = os.path.join(tempfile.gettempdir(), 'watchlist-config.ini')
        try:
            InitializeWatchlistConfiguration()(path)

            configfile = open(path).read()

            self.assertIn('github-oauth-token = 123asdf', configfile,
                          'Missing github-oauth-token in config file')

        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_integration_asked_for_oauth_token_on_empty_password(self):
        with self.mocker.order():
            self.type_when_asked('john.doe', prompt='Your GitHub username: ')
            self.type_when_asked('', prompt='Your GitHub password: ', hidden=True)
            self.type_when_asked('94a08da1fecbb6e8b46990538c7b50b2',
                                 prompt='GitHub OAuth token: ')

        self.mocker.replay()

        path = os.path.join(tempfile.gettempdir(), 'watchlist-config.ini')
        try:
            InitializeWatchlistConfiguration()(path)

            configfile = open(path).read()

            self.assertIn('github-oauth-token = 94a08da1fecbb6e8b46990538c7b50b2',
                          configfile,
                          'Missing or wrong github-oauth-token in config file')

        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_ask_for_login(self):
        self.type_when_asked('jone')
        self.mocker.replay()

        self.assertEquals(
            'jone',
            InitializeWatchlistConfiguration().ask_for_github_login())

    def test_retry_when_github_login_invalid(self):
        with self.mocker.order():
            self.type_when_asked('wrong user')
            self.type_when_asked('-other-wrong-user')
            self.type_when_asked('foo$')
            self.type_when_asked('val-id.user')
        self.mocker.replay()

        self.assertEquals(
            'val-id.user',
            InitializeWatchlistConfiguration().ask_for_github_login())

    def test_ask_for_github_password(self):
        self.type_when_asked('secret!!', hidden=True)
        self.mocker.replay()

        self.assertEquals(
            'secret!!',
            InitializeWatchlistConfiguration().ask_for_github_password())

    def test_ask_for_oauth_token(self):
        self.type_when_asked('098765ertfgi')
        self.mocker.replay()

        self.assertEquals(
            '098765ertfgi',
            InitializeWatchlistConfiguration().ask_for_oauth_token('john.doe'))

    def test_generate_config_file(self):
        self.mocker.replay()

        path = os.path.join(tempfile.gettempdir(), 'watchlist-config.ini')
        try:
            login = 'john.doe'
            token = '345231jkasd'

            InitializeWatchlistConfiguration().generate_config_file(path, login, token)

            with open(path) as file_:
                data = file_.read().split('\n')

            self.assertIn('[watchlist]', data,
                          'Missing [watchlist] section header in config file')

            self.assertIn('github-login = john.doe', data,
                          'Missing github-login in config file')

            self.assertIn('github-oauth-token = 345231jkasd', data,
                          'Missing github-oauth-token in config file')

            self.assertIn('watchlist =', data,
                          'Missing watchlist boilerplate in config file')

        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_generate_config_file_asks_when_file_exists(self):
        path = os.path.join(tempfile.gettempdir(), 'watchlist-config.ini')
        try:
            open(path, 'w+').close()
            login = 'john.doe'
            token = '345231jkasd'

            self.type_when_asked('', prompt='Confirm replacing file with ENTER'
                                 ' or abort with Ctrl-C: ')

            self.mocker.replay()

            InitializeWatchlistConfiguration().generate_config_file(path, login, token)

        finally:
            if os.path.exists(path):
                os.unlink(path)

    def type_when_asked(self, answer, prompt=ANY, hidden=False):
        if hidden:
            self.expect(self.getpass_mock(prompt)).result(answer)
        else:
            self.expect(self.raw_input_mock(prompt)).result(answer)
