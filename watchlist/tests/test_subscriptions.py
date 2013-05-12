from unittest2 import TestCase
from watchlist.subscriptions import CurrentSubscriptionsLoader
from watchlist.subscriptions import UpdateStrategy
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


class TestUpdateStrategy(TestCase):

    def test_strategy_with_simple_watchlist_watching_nothing(self):
        config = StubConfig(watchlist=(('watching', 'foo/bar'),
                                       ('not-watching', 'foo/.*'),
                                       ('watching', '.*')))

        subscriptions = {'foo/foo': False,
                         'foo/bar': False,
                         'bar/bar': False}
        self.assertEquals({'watch': ['bar/bar', 'foo/bar'],
                           'unwatch': [],
                           'keep-watching': [],
                           'keep-not-watching': ['foo/foo']},
                          UpdateStrategy(config).apply_watchlist(subscriptions))

    def test_strategy_with_simple_watchlist_watching_all(self):
        config = StubConfig(watchlist=(('watching', 'foo/bar'),
                                       ('not-watching', 'foo/.*'),
                                       ('watching', '.*')))

        subscriptions = {'foo/foo': True,
                         'foo/bar': True,
                         'bar/bar': True}
        self.assertEquals({'watch': [],
                           'unwatch': ['foo/foo'],
                           'keep-watching': ['bar/bar', 'foo/bar'],
                           'keep-not-watching': []},
                          UpdateStrategy(config).apply_watchlist(subscriptions))

    def test_strategy_is_top_down(self):
        config = StubConfig(watchlist=(('watching', '.*'),
                                       ('not-watching', '.*')))

        subscriptions = {'foo/foo': False,
                         'foo/bar': False,
                         'bar/bar': False}
        self.assertEquals({'watch': ['bar/bar', 'foo/bar', 'foo/foo'],
                           'unwatch': [],
                           'keep-watching': [],
                           'keep-not-watching': []},
                          UpdateStrategy(config).apply_watchlist(subscriptions))

    def test_unmatched_repositories_are_kept(self):
        config = StubConfig(watchlist=(('watching', 'foo/.*'),))

        subscriptions = {'foo/foo': False,
                         'foo/bar': False,
                         'bar/foo': True,
                         'bar/bar': False}
        self.assertEquals({'watch': ['foo/bar', 'foo/foo'],
                           'unwatch': [],
                           'keep-watching': ['bar/foo'],
                           'keep-not-watching': ['bar/bar']},
                          UpdateStrategy(config).apply_watchlist(subscriptions))
