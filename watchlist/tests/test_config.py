from unittest2 import TestCase
from tempfile import NamedTemporaryFile
from watchlist.config import Config
from watchlist.config import ConfigurationError


class TestConfig(TestCase):

    def test_parsing_errors_are_reported(self):
        with NamedTemporaryFile() as configfile:
            configfile.write('\n'.join((
                        '[watchlist',)))
            configfile.file.flush()

            with self.assertRaises(ConfigurationError) as cm:
                Config().load(configfile.name)

            self.assertIn(
                'MissingSectionHeaderError: File contains no section headers.',
                str(cm.exception))

    def test_configuration_error_when_no_section_in_config_file(self):
        with NamedTemporaryFile() as configfile:
            # empty config file

            with self.assertRaises(ConfigurationError) as cm:
                Config().load(configfile.name)

            self.assertEquals(
                'The config file should have exactly one section called "watchlist",'
                ' got: none', str(cm.exception))

    def test_configuration_error_when_wrong_sections_in_config_file(self):
        with NamedTemporaryFile() as configfile:
            configfile.write('\n'.join((
                        '[foo]',
                        '[bar]')))
            configfile.file.flush()

            with self.assertRaises(ConfigurationError) as cm:
                Config().load(configfile.name)

            self.assertEquals(
                'The config file should have exactly one section called "watchlist",'
                ' got: bar, foo', str(cm.exception))

    def test_configuration_error_when_missing_configuration_options(self):
        with NamedTemporaryFile() as configfile:
            configfile.write('\n'.join((
                        '[watchlist]',
                        '')))
            configfile.file.flush()

            with self.assertRaises(ConfigurationError) as cm:
                Config().load(configfile.name)

            self.assertEquals(
                'Missing configuration options: github-login, github-oauth-token,'
                ' watchlist', str(cm.exception))

    def test_configuration_error_on_bad_indent_in_watchlist(self):
        with NamedTemporaryFile() as configfile:
            configfile.write('\n'.join((
                        '[watchlist]',
                        'github-login = foo',
                        'github-oauth-token = bar',
                        'watchlist =',
                        'watching: foo/*')))
            configfile.file.flush()

            with self.assertRaises(ConfigurationError) as cm:
                Config().load(configfile.name)

            self.assertEquals(
                'Unexpected configuration options: watching.'
                ' Is the watchlist not properly indented?', str(cm.exception))

    def test_login_and_token_value_required(self):
        with NamedTemporaryFile() as configfile:
            configfile.write('\n'.join((
                        '[watchlist]',
                        'github-login =',
                        'github-oauth-token =',
                        'watchlist =')))
            configfile.file.flush()

            with self.assertRaises(ConfigurationError) as cm:
                Config().load(configfile.name)

            self.assertEquals(
                'Values required for the options github-login and github-oauth-token.',
                str(cm.exception))

    def test_propper_config_has_values(self):
        config = Config()

        with NamedTemporaryFile() as configfile:
            configfile.write('\n'.join((
                        '[watchlist]',
                        'github-login = foo',
                        'github-oauth-token = bar',
                        'watchlist =',
                        '  watching: foo/*',
                        '  watching: bar/bar',
                        '  not-watching: bar/*')))
            configfile.file.flush()
            config.load(configfile.name)

        self.assertEquals('foo', config.github_login, 'Wrong github login')
        self.assertEquals('bar', config.github_oauth_token, 'Wrong github token')

        self.assertEquals(
            [('watching', 'foo/*'),
             ('watching', 'bar/bar'),
             ('not-watching', 'bar/*')],
            config.watchlist, 'Unexpected watchlist in config')

    def test_configuration_error_when_watchlist_item_is_invalid(self):
        with NamedTemporaryFile() as configfile:
            configfile.write('\n'.join((
                        '[watchlist]',
                        'github-login = foo',
                        'github-oauth-token = bar',
                        'watchlist =',
                        '  watching: foo/*',
                        '  bar/bar',
                        '  not-watching: bar/*')))
            configfile.file.flush()

            with self.assertRaises(ConfigurationError) as cm:
                Config().load(configfile.name)

            self.assertEquals(
                'Unexpected format of watchlist item: bar/bar',
                str(cm.exception))
