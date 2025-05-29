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
        ]
        mock_get_json.return_value = test_repos_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock,
                   return_value="https://example.com/repos"):
            client = GithubOrgClient("test")
            repos = client.public_repos()
            self.assertEqual(repos, ["repo1", "repo2"])
            mock_get_json.assert_called_once()

    # --- Start of the different approach for test_has_license ---

    @staticmethod
    def has_license_test_cases():
        """Provides test cases for test_has_license."""
        return [
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
            ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
            ({"license": {"key": "apache-2.0"}}, "mit", False),
            # New edge cases
            ({"license": None}, "my_license", False),  # repo has 'license' but its value is None
            ({}, "my_license", False),  # repo has no 'license' key at all
            ({"name": "no_license_repo"}, "my_license", False), # repo missing 'license' entirely
            ({"license": {"name": "GPL"}}, "my_license", False), # repo has 'license' but no 'key' within it
            ({"license": {"key": ""}}, "my_license", False), # empty license key
            ({"license": {"key": "my_license"}}, "", False), # empty license_key to match against
        ]

    @parameterized.expand(has_license_test_cases())
    def test_has_license(self, repo, license_key, expected):
        """Test has_license method using a data provider."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

    # --- End of the different approach for test_has_license ---


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
        # Verify calls. Call count will depend on test execution order.
        # It's better to assert specific calls were made.
        self.mock_get.assert_any_call("https://api.github.com/orgs/google")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])


if __name__ == '__main__':
    unittest.main()
