#!/usr/bin/env python3
"""Test utils module
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map
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
