
#!/usr/bin/env python3
"""Test client module
"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
from typing import Dict, List


class TestGithubOrgClient(unittest.TestCase):
    """TestGithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: unittest.mock.Mock) -> None:
        """Test that GithubOrgClient.org returns the correct value"""
        test_payload = {"org": org_name}
        mock_get_json.return_value = test_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, test_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self) -> None:
        """Test that _public_repos_url returns the correct value"""
        test_payload = {"repos_url": "https://api.github.com/orgs/test/repos"}
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("test")
            self.assertEqual(client._public_repos_url,
                            test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: unittest.mock.Mock) -> None:
        """Test public_repos method"""
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
        ]
        mock_get_json.return_value = test_repos_payload

        with patch('client.GithubOrgClient._public_repos_url',
                  new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = "https://example.com/repos"
            client = GithubOrgClient("test")
            repos = client.public_repos()

            self.assertEqual(repos, ["repo1", "repo2"])
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo: Dict, license_key: str, expected: bool) -> None:
        """Test has_license method"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3],
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url: str) -> unittest.mock.Mock:
            """Side effect for mock get"""
            mock = unittest.mock.Mock()
            if url == "https://api.github.com/orgs/testorg":
                mock.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock.json.return_value = cls.repos_payload
            return mock

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down class"""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test public_repos integration"""
        client = GithubOrgClient("testorg")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Test public_repos with license"""
        client = GithubOrgClient("testorg")
        self.assertEqual(client.public_repos(license="apache-2.0"),
                         self.apache2_repos)
