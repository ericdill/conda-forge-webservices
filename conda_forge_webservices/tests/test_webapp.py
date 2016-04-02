import json
import unittest
try:
    from urllib.parse import urlencode
    import unittest.mock as mock
except ImportError:
    from urllib import urlencode
    import mock

from tornado.testing import AsyncHTTPTestCase

from conda_forge_webservices.webapp import create_webapp


class TestHandlerBase(AsyncHTTPTestCase):
    def get_app(self):
        return create_webapp()


class TestBucketHandler(TestHandlerBase):
    def test_bad_header(self):
        response = self.fetch('/conda-linting/hook', method='POST',
                              body=urlencode({'a': 1}))
        self.assertEqual(response.code, 404)

    @mock.patch('conda_forge_webservices.linting.compute_lint_message', return_value=mock.sentinel.message)
    @mock.patch('conda_forge_webservices.linting.comment_on_pr')
    def test_good_header(self, comment_on_pr, compute_lint_message):
        body = {'repository': {'name': 'repo_name',
                               'clone_url': 'repo_clone_url',
                               'owner': {'login': 'conda-forge'}},
                'pull_request': {'number': '3',
                                 'state': 'open'}}

        response = self.fetch('/conda-linting/hook', method='POST',
                              body=json.dumps(body),
                              headers={'X-GitHub-Event': 'pull_request'})

        self.assertEqual(response.code, 200)
        compute_lint_message.assert_called_once_with('conda-forge', 'repo_name',
                                                     3)

        comment_on_pr.assert_called_once_with('conda-forge', 'repo_name',
                                              3, mock.sentinel.message)
