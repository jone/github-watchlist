from StringIO import StringIO
from mocker import ANY
from watchlist.command import UpdateCommand
from watchlist.tests.base import GithubMockTestCase
from watchlist.tests.base import StubConfig
import sys
import unittest2


class TestUpdateCommand(GithubMockTestCase):

    def setUp(self):
        super(TestUpdateCommand, self).setUp()

        self.raw_input_mock = self.mocker.replace(raw_input)
        self.expect(self.raw_input_mock(ANY)).throw(
            AssertionError('Unexpected raw_input call')).count(0, None)

    def test_updates_subscriptions(self):
        self.given_user_is_in_organisations('watchall', 'watchnone')
        self.given_repositories('john.doe/foo',
                                'watchall/bar',
                                'watchnone/baz',
                                'watchnone/foo')
        self.given_subscriptions('john.doe/foo', 'watchnone/foo')
        self.reckon_github_read_requests()

        config = StubConfig(watchlist=(('watching', 'watchall/.*'),
                                       ('not-watching', 'watchnone/.*')))

        self.expect_subscription_created('watchall/bar')
        self.expect_subscription_deleted('watchnone/foo')
        self.type_when_asked('Yes')
        self.mocker.replay()

        UpdateCommand(config)()

    def test_updates_subscriptions_without_confirmation(self):
        self.given_repositories('john.doe/foo')
        self.reckon_github_read_requests()

        config = StubConfig(watchlist=(('watching', '.*'),))

        self.expect_subscription_created('john.doe/foo')
        self.mocker.replay()

        UpdateCommand(config)(confirmed=True)

    def test_confirm_subscription_changes_with_yes(self):
        self.type_when_asked('yes')
        self.mocker.replay()

        cmd = UpdateCommand(StubConfig())
        self.assertTrue(cmd.confirm_subscription_changes())

    def test_confirm_subscription_changes_with_no(self):
        self.type_when_asked('no')

        # python2.6 does not raise SystemExit
        exit = self.mocker.replace('sys.exit')
        self.expect(exit(1)).throw(SystemExit())

        self.mocker.replay()

        cmd = UpdateCommand(StubConfig())
        with self.assertRaises(SystemExit):
            cmd.confirm_subscription_changes()

    def type_when_asked(self, answer, prompt=ANY):
        self.expect(self.raw_input_mock(prompt)).result(answer)


class TestUpdateCommandReport(unittest2.TestCase):

    def setUp(self):
        self.stdout = StringIO()
        self.ori_stdout = sys.stdout
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout = self.ori_stdout
        self.stdout = sys.stdout

    def test_report_changes_to_make(self):
        data = {
            'keep-not-watching': ['keep/not.watching'],
            'keep-watching': ['keep/watching'],
            'watch': ['start/watching'],
            'unwatch': ['stop/watching']}

        cmd = UpdateCommand(StubConfig())
        cmd.report_changes_to_make(data)

        self.stdout.seek(0)
        self.assertMultiLineEqual(
            '\n'.join((
                    'NO SUBSCRIPTION CHANGES:',
                    ' - keep not watching: keep/not.watching',
                    ' - keep watching: keep/watching',
                    '',

                    'SUBSCRIPTION CHANGES:',
                    ' - add subscription: start/watching',
                    ' - remove subscription: stop/watching',
                    '',

                    'SUMMARY:',
                    ' - Keep watching: 1',
                    ' - Keep not watching: 1',
                    ' - Start watching: 1',
                    ' - Stop watching: 1',
                    '')),
            self.stdout.read())
