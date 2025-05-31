#!/usr/bin/env python3


import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from typing import Dict, List
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Comprehensive test suite for GithubOrgClient"""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org: str, expected: Dict, mock_get_json: MagicMock) -> None:
        """Test that org returns correct data"""
        mock_get_json.return_value = expected
        client = GithubOrgClient(org)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org}"
        )

    def test_public_repos_url(self) -> None:
        """Test the _public_repos_url property"""
        with patch(
            'client.GithubOrgClient.org',
            new_callable=PropertyMock
        ) as mock_org:
            test_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
            mock_org.return_value = test_payload
            client = GithubOrgClient("google")
            self.assertEqual(
                client._public_repos_url,
                "https://api.github.com/orgs/google/repos"
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """Test public_repos with proper mocking"""
        test_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos",
            "repos": [
                {"name": "repo1", "license": {"key": "mit"}},
                {"name": "repo2", "license": {"key": "apache-2.0"}},
            ]
        }
        mock_get_json.return_value = test_payload["repos"]

        with patch(
            'client.GithubOrgClient._public_repos_url',
            new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = test_payload["repos_url"]
            client = GithubOrgClient("google")
            repos = client.public_repos()

            expected_repos = ["repo1", "repo2"]
            self.assertEqual(repos, expected_repos)
            mock_get_json.assert_called_once()
            mock_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo: Dict, license_key: str, expected: bool) -> None:
        """Test the has_license static method"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up integration test mocks"""
        cls.get_patcher = patch('requests.get', side_effect=cls.mock_requests_get)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up integration test mocks"""
        cls.get_patcher.stop()

    @classmethod
    def mock_requests_get(cls, url: str) -> MagicMock:
        """Mock requests.get based on URL"""
        mock_response = MagicMock()
        
        if url == "https://api.github.com/orgs/google":
            mock_response.json.return_value = cls.org_payload
        elif url == cls.org_payload["repos_url"]:
            mock_response.json.return_value = cls.repos_payload
        else:
            raise ValueError(f"Unmocked URL: {url}")
        
        return mock_response

    def test_public_repos(self) -> None:
        """Integration test for public_repos"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Integration test for public_repos with license filter"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
