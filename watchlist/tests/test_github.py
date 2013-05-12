from requests import HTTPError
from watchlist import github
from watchlist.tests.base import GithubMockTestCase
from watchlist.tests.base import RequestsResponseStub
from watchlist.tests.base import StubConfig
import json


def generate_links(path, **pages):
    header = []
    template = '<https://api.github.com/%s?page=%i>; rel="%s"'

    for rel, page in pages.items():
        header.append(template % (path, page, rel))

    return ', '.join(header)


class TestGithubRequests(GithubMockTestCase):

    def test_get_with_pagination(self):
        page_one = ['foo']
        page_two = ['bar']
        page_three = ['baz']

        self.mock_github_request(
            'foo', json.dumps(page_one), response_headers={
                'link': generate_links('foo', next=2, last=3)})

        self.mock_github_request(
            'foo?page=2', json.dumps(page_two), response_headers={
                'link': generate_links('foo', first=1, prev=1, next=3, last=3)})

        self.mock_github_request(
            'foo?page=3', json.dumps(page_three), response_headers={
                'link': generate_links('foo', first=1, prev=2)})

        self.mocker.replay()
        self.assertEquals(['foo', 'bar', 'baz'], github.get('foo', StubConfig()))

    def test_get_raises_httperrors(self):
        self.mock_github_request('foo', '', response_status_code=401)
        self.mocker.replay()

        with self.assertRaises(HTTPError) as cm:
            github.get('foo', StubConfig())

        self.assertEquals('401 Client Error: Unauthorized', str(cm.exception))

    def test_put_request(self):
        self.mock_github_request('foo', '["foo"]', method='put', payload='fuhuu')
        self.mocker.replay()
        github.put('foo', StubConfig(), 'fuhuu')

    def test_put_raises_httperrors(self):
        self.mock_github_request('foo', '["foo"]', method='put', payload='fuhuu',
                                 response_status_code=401)
        self.mocker.replay()

        with self.assertRaises(HTTPError) as cm:
            github.put('foo', StubConfig(), 'fuhuu')

        self.assertEquals('401 Client Error: Unauthorized', str(cm.exception))

    def test_delete_request(self):
        self.mock_github_request('foo', '', method='delete')
        self.mocker.replay()
        github.delete('foo', StubConfig())

    def test_delete_raises_httperrors(self):
        self.mock_github_request('foo', '', method='delete', response_status_code=401)
        self.mocker.replay()

        with self.assertRaises(HTTPError) as cm:
            github.delete('foo', StubConfig())

        self.assertEquals('401 Client Error: Unauthorized', str(cm.exception))

    def test_extracting_link_headers(self):
        self.mocker.replay()

        response = RequestsResponseStub(headers={
                'link': '<https://api.github.com/foo?page=2>; rel="next"'
                ', <https://api.github.com/foo?page=6>; rel="last"'})

        self.assertEquals({'next': 'https://api.github.com/foo?page=2',
                            'last': 'https://api.github.com/foo?page=6'},
                          github._extract_link_header(response))
