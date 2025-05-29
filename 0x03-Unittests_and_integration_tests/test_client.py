#!/usr/bin/env python3
"""Test client module"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock, Mock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """TestGithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value"""
        test_payload = {"login": org_name}
        mock_get_json.return_value = test_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, test_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test _public_repos_url returns correct value"""
        test_payload = {"repos_url": "https://api.github.com/orgs/test/repos"}
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock,
                   return_value=test_payload):
            client = GithubOrgClient("test")
            self.assertEqual(client._public_repos_url,
                             test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos method"""
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"}, # Repo without a license key
            {"name": "repo4", "license": {"name": "Some License"}}, # Repo with license object but no 'key'
        ]
        mock_get_json.return_value = test_repos_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock,
                   return_value="https://example.com/repos"):
            client = GithubOrgClient("test")
            
            # Test without license filter
            repos_all = client.public_repos()
            self.assertEqual(repos_all, ["repo1", "repo2", "repo3", "repo4"])

            # Test with 'mit' license filter
            repos_mit = client.public_repos(license="mit")
            self.assertEqual(repos_mit, ["repo1"])

            # Test with 'apache-2.0' license filter
            repos_apache = client.public_repos(license="apache-2.0")
            self.assertEqual(repos_apache, ["repo2"])

            # Test with a license that doesn't exist in the payload
            repos_non_existent = client.public_repos(license="gpl")
            self.assertEqual(repos_non_existent, [])

            # get_json should still only be called once due to memoization
            mock_get_json.assert_called_once()


    @parameterized.expand([
        # Positive cases
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        # Negative cases (license key exists but doesn't match)
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": {"key": "mit"}}, "apache-2.0", False),
        # Edge cases: missing 'key' within 'license' object
        ({"license": {"name": "Some License"}}, "my_license", False),
        ({"license": {}}, "my_license", False), # empty license dict
        # Edge cases: missing 'license' object
        ({"name": "repo_without_license"}, "my_license", False),
        ({}, "my_license", False), # empty repo
        # Edge cases: license key is an empty string
        ({"license": {"key": "my_license"}}, "", False),
        ({"license": {"key": ""}}, "my_license", False), # repo has empty license key
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license method with various valid inputs."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

    def test_has_license_raises_assertion_error_on_none_key(self):
        """Test that has_license raises AssertionError when license_key is None."""
        repo = {"license": {"key": "any_license"}}
        license_key = None
        with self.assertRaisesRegex(AssertionError, "license_key cannot be None"):
            GithubOrgClient.has_license(repo, license_key)


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3],
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up class"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            mock = Mock()
            if url == "https://api.github.com/orgs/google":
                mock.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock.json.return_value = cls.repos_payload
            return mock

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down class"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos integration"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
        self.mock_get.assert_any_call("https://api.github.com/orgs/google")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])
        # Due to memoization, these two calls should be the only ones
        self.assertEqual(self.mock_get.call_count, 2)


    def test_public_repos_with_license(self):
        """Test public_repos with license"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(license="apache-2.0"),
                         self.apache2_repos)
        # Verify calls. The calls should have already been made by test_public_repos
        # if tests run in the same class instance.
        self.mock_get.assert_any_call("https://api.github.com/orgs/google")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])


if __name__ == '__main__':
    unittest.main()
