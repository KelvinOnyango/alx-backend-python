#!/usr/bin/env python3
"""test_client.py"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from typing import Dict
from fixtures import TEST_PAYLOAD
from unittest import TestCase


class TestGithubOrgClient(unittest.TestCase):
    """
    TestGithubOrgClient class
    """

    @parameterized.expand(
        [
            ("google", {"login": "google"}),
            ("abc", {"login": "abc"}),
        ]
    )
    @patch(
        "client.get_json",
    )
    def test_org(self, org: str, resp: Dict, mocked_fxn: MagicMock) -> None:
        """testing GithubOrgClient response"""
        mocked_fxn.return_value = MagicMock(return_value=resp)
        gh_org_client = GithubOrgClient(org)
        self.assertEqual(gh_org_client.org(), resp)
        mocked_fxn.assert_called_once_with(
            f"https://api.github.com/orgs/{org}"
        )

    @patch("client.GithubOrgClient.org", new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org):
        """test public repos url"""
        mock_org.return_value = {
            "repos_url": "https://api.github.com/users/google/repos"
        }
        self.assertEqual(
            GithubOrgClient("google")._public_repos_url,
            "https://api.github.com/users/google/repos",
        )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test public_repos method using TEST_PAYLOAD"""
        org_payload, repos_payload, expected_names, _ = TEST_PAYLOAD[0]

        # Mock get_json to return repos_payload
        mock_get_json.return_value = repos_payload

        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = org_payload["repos_url"]

            client = GithubOrgClient("google")
            result = client.public_repos()

            self.assertEqual(result, expected_names)
            mock_get_json.assert_called_once_with(org_payload["repos_url"])
            mock_repos_url.assert_called_once()

    @parameterized.expand(
        [
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
            ({}, "my_license", False),
        ]
    )
    def test_has_license(self, repo, license_key, expected):
        """Test has_license static method"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD,
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Set up mock for requests.get"""
        cls.get_patcher = patch("requests.get")

        # Start the patcher and get the mock object
        mock_get = cls.get_patcher.start()

        # Define a side_effect to mock requests.get(url).json() behavior
        def side_effect(url):
            if url == "https://api.github.com/orgs/google":
                mock_response = MagicMock()
                mock_response.json.return_value = cls.org_payload
                return mock_response
            elif url == cls.org_payload["repos_url"]:
                mock_response = MagicMock()
                mock_response.json.return_value = cls.repos_payload
                return mock_response
            else:
                raise ValueError(f"Unhandled URL: {url}")

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos with no license filter"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with Apache 2.0 license"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"), self.apache2_repos
        )

    def test_public_repos(self):
        """Test public_repos returns expected list of repo names"""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filters by license correctly (apache-2.0)"""
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)
