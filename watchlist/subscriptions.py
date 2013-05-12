from watchlist import github


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
