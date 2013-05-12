from watchlist.loader import CurrentSubscriptionsLoader
from watchlist.tests.base import GithubMockTestCase
from watchlist.tests.base import StubConfig


class TestCurrentSubscriptionsLoader(GithubMockTestCase):

    def test_returns_all_repositories_with_watching_state(self):
        self.given_user_is_in_organisations('bigorg')
        self.given_repositories('john.doe/foo', 'bigorg/bar')
        self.given_subscriptions('john.doe/foo')

        self.reckon_github_read_requests()
        self.mocker.replay()

        loader = CurrentSubscriptionsLoader(StubConfig())
        self.assertEquals({'john.doe/foo': {'watching': True},
                           'bigorg/bar': {'watching': False}},
                          loader.load_current_subscriptions())

    def test_does_not_return_watch_repositories_without_member_access(self):
        self.given_repositories('john.doe/foo', 'otheruser/bar')

        self.reckon_github_read_requests()
        self.mocker.replay()

        loader = CurrentSubscriptionsLoader(StubConfig())
        self.assertEquals(['john.doe/foo'],
                          loader.load_current_subscriptions().keys())
