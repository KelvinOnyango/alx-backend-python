#!/usr/bin/env python3
"""Test module for client.py"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient"""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org, resp, mock_get_json):
        """Test org method returns correct data"""
        mock_get_json.return_value = resp
        client = GithubOrgClient(org)
        self.assertEqual(client.org(), resp)
        mock_get_json.assert_called_once_with(
            "https://api.github.com/orgs/{}".format(org)
        )

    @patch('client.GithubOrgClient.org', new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org):
        """Test _public_repos_url property"""
        mock_org.return_value = {
            "repos_url": "https://api.github.com/users/google/repos"
        }
        self.assertEqual(
            GithubOrgClient("google")._public_repos_url,
            "https://api.github.com/users/google/repos",
        )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos method"""
        test_payload = TEST_PAYLOAD[0]
        mock_get_json.return_value = test_payload[1]

        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = test_payload[0]["repos_url"]
            client = GithubOrgClient("google")
            result = client.public_repos()

            self.assertEqual(result, test_payload[2])
            mock_get_json.assert_called_once()
            mock_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license static method"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up for integration tests"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Side effect for requests.get mock"""
            mock = MagicMock()
            if url == "https://api.github.com/orgs/google":
                mock.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock.json.return_value = cls.repos_payload
            return mock

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Clean up after integration tests"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos integration"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
