#!/usr/bin/env python3
"""Test utils module
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize
from typing import Dict, Tuple, Any


class TestAccessNestedMap(unittest.TestCase):
    """TestAccessNestedMap class
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
            self,
            nested_map: Dict,
            path: Tuple[str],
            expected: Any) -> None:
        """Test access_nested_map method
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(
            self,
            nested_map: Dict,
            path: Tuple[str],
            expected_exception: str) -> None:
        """Test access_nested_map exception
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_exception}'")


class TestGetJson(unittest.TestCase):
    """TestGetJson class
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(
            self,
            test_url: str,
            test_payload: Dict) -> None:
        """Test get_json method
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock()
            mock_get.return_value.json.return_value = test_payload
            
            result = get_json(test_url)
            
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """TestMemoize class
    """
    def test_memoize(self) -> None:
        """Test memoize decorator
        """
        class TestClass:
            """TestClass
            """
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock_method:
            mock_method.return_value = 42
            test_class = TestClass()
            
            # First call
            self.assertEqual(test_class.a_property, 42)
            # Second call
            self.assertEqual(test_class.a_property, 42)
            
            mock_method.assert_called_once()
