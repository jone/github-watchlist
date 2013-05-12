from watchlist.tests import github
from watchlist.tests.base import GithubMockTestCase
from watchlist.tests.base import StubConfig
from watchlist.updater import SubscriptionsUpdater
import json


class TestSubscriptionsUpdater(GithubMockTestCase):

    def test_watches_repositories(self):
        data = {'watch': ['bar/bar', 'foo/bar'],
                'unwatch': [],
                'keep-watching': [],
                'keep-not-watching': ['foo/foo']}
        self.expect_subscription_created('bar/bar')
        self.expect_subscription_created('foo/bar')
        self.mocker.replay()

        updater = SubscriptionsUpdater(StubConfig())
        updater.update(data)

    def test_unwatches_repositories(self):
        data = {'watch': [],
                'unwatch': ['bar/bar', 'foo/bar'],
                'keep-watching': ['foo/foo'],
                'keep-not-watching': []}
        self.expect_subscription_deleted('bar/bar')
        self.expect_subscription_deleted('foo/bar')
        self.mocker.replay()

        updater = SubscriptionsUpdater(StubConfig())
        updater.update(data)

    def expect_subscription_created(self, reponame):
        watch_payload = json.dumps({'subscribed': True, 'ignored': False})

        self.mock_github_request(
            '%s/subscription' % reponame,
            github.subscription(reponame),
            method='put',
            payload=watch_payload)

    def expect_subscription_deleted(self, reponame):
        self.mock_github_request('%s/subscription' % reponame, '', method='delete')
