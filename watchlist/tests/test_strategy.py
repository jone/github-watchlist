from watchlist.tests.base import StubConfig
from unittest2 import TestCase
from watchlist.strategy import UpdateStrategy

class TestUpdateStrategy(TestCase):

    def test_strategy_with_simple_watchlist_watching_nothing(self):
        config = StubConfig(watchlist=(('watching', 'foo/bar'),
                                       ('not-watching', 'foo/.*'),
                                       ('watching', '.*')))

        subscriptions = {'foo/foo': {'watching': False},
                         'foo/bar': {'watching': False},
                         'bar/bar': {'watching': False}}
        self.assertEquals({'watch': ['bar/bar', 'foo/bar'],
                           'unwatch': [],
                           'keep-watching': [],
                           'keep-not-watching': ['foo/foo']},
                          UpdateStrategy(config).apply_watchlist(subscriptions))

    def test_strategy_with_simple_watchlist_watching_all(self):
        config = StubConfig(watchlist=(('watching', 'foo/bar'),
                                       ('not-watching', 'foo/.*'),
                                       ('watching', '.*')))

        subscriptions = {'foo/foo': {'watching': True},
                         'foo/bar': {'watching': True},
                         'bar/bar': {'watching': True}}
        self.assertEquals({'watch': [],
                           'unwatch': ['foo/foo'],
                           'keep-watching': ['bar/bar', 'foo/bar'],
                           'keep-not-watching': []},
                          UpdateStrategy(config).apply_watchlist(subscriptions))

    def test_strategy_is_top_down(self):
        config = StubConfig(watchlist=(('watching', '.*'),
                                       ('not-watching', '.*')))

        subscriptions = {'foo/foo': {'watching': False},
                         'foo/bar': {'watching': False},
                         'bar/bar': {'watching': False}}
        self.assertEquals({'watch': ['bar/bar', 'foo/bar', 'foo/foo'],
                           'unwatch': [],
                           'keep-watching': [],
                           'keep-not-watching': []},
                          UpdateStrategy(config).apply_watchlist(subscriptions))

    def test_unmatched_repositories_are_kept(self):
        config = StubConfig(watchlist=(('watching', 'foo/.*'),))

        subscriptions = {'foo/foo': {'watching': False},
                         'foo/bar': {'watching': False},
                         'bar/foo': {'watching': True},
                         'bar/bar': {'watching': False}}
        self.assertEquals({'watch': ['foo/bar', 'foo/foo'],
                           'unwatch': [],
                           'keep-watching': ['bar/foo'],
                           'keep-not-watching': ['bar/bar']},
                          UpdateStrategy(config).apply_watchlist(subscriptions))
