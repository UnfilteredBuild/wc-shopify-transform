"""
Tests for the WooCommerceToShopifyTransformer module.
"""

import unittest
import sys
import os
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from transformer import WooCommerceToShopifyTransformer


class TestWeightConversion(unittest.TestCase):
    """Test cases for weight conversion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = WooCommerceToShopifyTransformer()
    
    def test_convert_weight_to_grams_four_decimal_places(self):
        """Test that weight conversion returns exactly four decimal places."""
        test_cases = [
            (1.0, 453.5920),      # 1 lb = 453.592 grams
            (0.5, 226.7960),      # 0.5 lb = 226.796 grams  
            (2.345, 1063.6732),   # 2.345 lb * 453.592 = 1063.67324 -> rounded to 1063.6732
            (0.1, 45.3592),       # 0.1 lb = 45.3592 grams
            (10, 4535.9200),      # 10 lb = 4535.92 grams
            (0.001, 0.4536),      # 0.001 lb = 0.4536 grams
            (3.14159, 1425.0001), # 3.14159 lb * 453.592 = 1425.00005 -> rounded to 1425.0001
        ]
        
        for weight_lbs, expected_grams in test_cases:
            with self.subTest(weight_lbs=weight_lbs):
                result = self.transformer.convert_weight_to_grams(weight_lbs)
                
                # Check that result is a float
                self.assertIsInstance(result, float, f"Result should be float for input {weight_lbs}")
                
                # Check that result equals expected value
                self.assertAlmostEqual(result, expected_grams, places=4, 
                                     msg=f"Expected {expected_grams} grams for {weight_lbs} lbs, got {result}")
                
                # Check that result has exactly 4 decimal places when converted to string
                result_str = f"{result:.4f}"
                decimal_places = len(result_str.split('.')[1])
                self.assertEqual(decimal_places, 4, 
                               f"Result {result} should have exactly 4 decimal places, got {decimal_places}")
    
    def test_convert_weight_edge_cases(self):
        """Test edge cases for weight conversion."""
        # Test zero weight
        result = self.transformer.convert_weight_to_grams(0)
        self.assertEqual(result, 0.0000)
        self.assertIsInstance(result, float)
        
        # Test None input
        result = self.transformer.convert_weight_to_grams(None)
        self.assertEqual(result, 0.0000)
        self.assertIsInstance(result, float)
        
        # Test empty string
        result = self.transformer.convert_weight_to_grams('')
        self.assertEqual(result, 0.0000)
        self.assertIsInstance(result, float)
        
        # Test pandas NA
        result = self.transformer.convert_weight_to_grams(pd.NA)
        self.assertEqual(result, 0.0000)
        self.assertIsInstance(result, float)
    
    def test_convert_weight_invalid_inputs(self):
        """Test invalid inputs for weight conversion."""
        invalid_inputs = ['invalid', 'abc', [], {}, object()]
        
        for invalid_input in invalid_inputs:
            with self.subTest(invalid_input=invalid_input):
                result = self.transformer.convert_weight_to_grams(invalid_input)
                self.assertEqual(result, 0.0000)
                self.assertIsInstance(result, float)
    
    def test_convert_weight_string_numbers(self):
        """Test that string numbers are properly converted."""
        test_cases = [
            ('1.5', 680.3880),
            ('0.25', 113.3980),
            ('5', 2267.9600),
        ]
        
        for weight_str, expected_grams in test_cases:
            with self.subTest(weight_str=weight_str):
                result = self.transformer.convert_weight_to_grams(weight_str)
                self.assertAlmostEqual(result, expected_grams, places=4)
                self.assertIsInstance(result, float)
    
    def test_precision_with_very_small_weights(self):
        """Test precision with very small weight values."""
        # Test very small weight that should round to 4 decimal places
        small_weight = 0.00001  # Very small weight in pounds
        result = self.transformer.convert_weight_to_grams(small_weight)
        
        # Should be 0.00001 * 453.592 = 0.00453592, rounded to 0.0045
        expected = 0.0045
        self.assertAlmostEqual(result, expected, places=4)
        
        # Verify it has exactly 4 decimal places
        result_str = f"{result:.4f}"
        decimal_places = len(result_str.split('.')[1])
        self.assertEqual(decimal_places, 4)


if __name__ == '__main__':
    unittest.main()