#!/usr/bin/env python3
"""Test module for utils.py"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock, PropertyMock
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns the correct value for valid paths."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key_error):
        """Test that access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), f"'{expected_key_error}'")


class TestGetJson(unittest.TestCase):
    """Tests for get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get')
    def test_get_json(self, test_url, test_payload, mock_requests_get):
        """Test that get_json makes the correct HTTP call and returns the expected JSON."""
        # Configure the mock to return a Mock object with a json method
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_requests_get.return_value = mock_response

        result = get_json(test_url)

        # Test that the mocked get method was called exactly once with test_url
        mock_requests_get.assert_called_once_with(test_url)

        # Test that the output of get_json is equal to test_payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Tests for the memoize decorator"""

    def test_memoize(self):
        """Test that a memoized method calls its wrapped function only once."""

        class TestClass:
            def a_method(self):
                """A method to be mocked."""
                return 42

            @memoize
            def a_property(self):
                """A property using memoize."""
                return self.a_method()

        # Patch 'a_method' of TestClass
        with patch.object(TestClass, 'a_method', return_value=42) as mock_a_method:
            test_instance = TestClass()

            # Access the memoized property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Assert that the correct result is returned
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Assert that a_method was called exactly once
            mock_a_method.assert_called_once()
