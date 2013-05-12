from watchlist import github
import re


class CurrentSubscriptionsLoader(object):

    def __init__(self, config):
        self.config = config

    def load_current_subscriptions(self):
        repositories = {}
        watching = self.get_watching_repositories()

        for reponame in self.get_member_repositories():
            repositories[reponame] = {'watching': reponame in watching}

        return repositories

    def get_watching_repositories(self):
        response = github.get('user/subscriptions', self.config)
        return set(map(lambda repo: repo.get('full_name'), response))

    def get_member_repositories(self):
        repositories = github.get('user/repos', self.config)

        for organisation in github.get('user/orgs', self.config):
            org_name = organisation.get('login')
            repositories.extend(github.get('orgs/%s/repos' % org_name, self.config))

        return set(map(lambda repo: repo.get('full_name'), repositories))


class UpdateStrategy(object):

    def __init__(self, config):
        self.config = config

    def apply_watchlist(self, subscriptions):
        result = {'watch': [],
                  'unwatch': [],
                  'keep-watching': [],
                  'keep-not-watching': []}

        for item in self.config.watchlist:
            self.apply_watchlist_item(subscriptions, result, item)

        self.keep_unmatched(subscriptions, result)
        assert len(subscriptions) == 0, 'Subscriptions should be empty now: %s' % (
            subscriptions)

        self.sort_result(result)
        return result

    def apply_watchlist_item(self, subscriptions, result, item):
        type_, expression = item
        xpr = re.compile(expression)
        assert type_ in ('watching', 'not-watching'), \
            'Unexpected expression type: %s' % type_

        for reponame, watching in subscriptions.items():
            if not xpr.match(reponame):
                continue

            if type_ == 'watching':
                if watching:
                    result['keep-watching'].append(reponame)
                else:
                    result['watch'].append(reponame)

            elif type_ == 'not-watching':
                if watching:
                    result['unwatch'].append(reponame)
                else:
                    result['keep-not-watching'].append(reponame)

            del subscriptions[reponame]

    def keep_unmatched(self, subscriptions, result):
        for reponame, watching in subscriptions.items():
            if watching:
                result['keep-watching'].append(reponame)
            else:
                result['keep-not-watching'].append(reponame)

            del subscriptions[reponame]

    def sort_result(self, result):
        for _name, value in result.items():
            value.sort()
