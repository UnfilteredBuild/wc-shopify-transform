"""
Tests for the CustomerToShopifyTransformer module.
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from customer_transformer import CustomerToShopifyTransformer


class TestCustomerTransformerValidation(unittest.TestCase):
    """Test cases for customer data validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CustomerToShopifyTransformer()
        
        # Complete valid customer data
        self.valid_data = {
            'First Name': ['John', 'Jane'],
            'Last Name': ['Doe', 'Smith'],
            'Email': ['john@example.com', 'jane@example.com'],
            'Accepts Email Marketing': [1, 0],
            'Default Address Company': ['ACME Corp', 'XYZ Inc'],
            'Default Address Address1': ['123 Main St', '456 Oak Ave'],
            'Default Address City': ['New York', 'Los Angeles'],
            'Default Address Province Code': ['NY', 'CA'],
            'Default Address Country Code': ['US', 'US'],
            'Phone': ['123-456-7890', '098-765-4321']
        }
    
    def test_validate_complete_data(self):
        """Test validation with complete valid data."""
        df = pd.DataFrame(self.valid_data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_missing_required_columns(self):
        """Test validation with missing required columns."""
        incomplete_data = self.valid_data.copy()
        del incomplete_data['First Name']
        del incomplete_data['Email']
        
        df = pd.DataFrame(incomplete_data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Missing required columns:' in error and 'First Name' in error and 'Email' in error for error in result['errors']))
    
    def test_validate_empty_emails(self):
        """Test validation with empty email addresses."""
        data_with_empty_emails = self.valid_data.copy()
        data_with_empty_emails['Email'] = ['john@example.com', np.nan]
        
        df = pd.DataFrame(data_with_empty_emails)
        result = self.transformer.validate_dataframe(df)
        
        self.assertFalse(result['valid'])
        self.assertIn('1 customers have empty email addresses', result['errors'][0])
    
    def test_validate_multiple_errors(self):
        """Test validation with multiple errors."""
        bad_data = {
            'First Name': ['John'],
            'Last Name': ['Doe'],
            'Email': [np.nan],  # Missing email
            # Missing most required columns
        }
        
        df = pd.DataFrame(bad_data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertFalse(result['valid'])
        self.assertEqual(len(result['errors']), 2)  # Missing columns + empty email
    
    def test_validate_us_zip_codes(self):
        """Test validation of US zip codes - both 5 digit and 5+4 formats."""
        # Valid US zip codes in both formats
        valid_data = self.valid_data.copy()
        valid_data['Default Address Country Code'] = ['US', 'US', 'US']
        valid_data['Default Address Zip'] = ['12345', '67890-1234', '01234']  # 5-digit, 5+4, leading zero
        # Add third customer data
        for key in valid_data:
            if key not in ['Default Address Country Code', 'Default Address Zip']:
                if len(valid_data[key]) == 2:
                    valid_data[key].append(valid_data[key][0])
        
        df = pd.DataFrame(valid_data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_invalid_us_zip_codes(self):
        """Test validation with invalid US zip codes."""
        invalid_data = self.valid_data.copy()
        invalid_data['Default Address Country Code'] = ['US', 'US', 'US', 'US']
        invalid_data['Default Address Zip'] = ['1234', '123456', '12345-', '12345-12345']  # Too short, too long, incomplete 5+4, too many digits
        # Add more customer data
        for key in invalid_data:
            if key not in ['Default Address Country Code', 'Default Address Zip']:
                while len(invalid_data[key]) < 4:
                    invalid_data[key].append(invalid_data[key][0])
        
        df = pd.DataFrame(invalid_data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertFalse(result['valid'])
        self.assertTrue(any('Invalid US zip codes found' in error for error in result['errors']))
        # Should mention the invalid zip codes
        error_text = ' '.join(result['errors'])
        self.assertIn('1234', error_text)
        self.assertIn('123456', error_text)
        self.assertIn('12345-', error_text)
        self.assertIn('12345-12345', error_text)
    
    def test_validate_non_us_zip_codes_ignored(self):
        """Test that non-US zip codes are not validated for 5-character rule."""
        data = self.valid_data.copy()
        data['Default Address Country Code'] = ['CA', 'UK']
        data['Default Address Zip'] = ['K1A0A9', 'SW1A1AA']  # Canadian and UK postal codes
        
        df = pd.DataFrame(data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertTrue(result['valid'])  # Should pass even with non-5-character codes
    
    def test_validate_empty_us_zip_codes(self):
        """Test that empty US zip codes don't trigger validation error."""
        data = self.valid_data.copy()
        data['Default Address Country Code'] = ['US', 'US']
        data['Default Address Zip'] = ['', np.nan]  # Empty and NaN
        
        df = pd.DataFrame(data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertTrue(result['valid'])  # Empty/NaN zip codes should be allowed
    
    def test_validate_us_extended_zip_codes(self):
        """Test validation of US extended zip codes (5+4 format)."""
        data = self.valid_data.copy()
        data['Default Address Country Code'] = ['US', 'US', 'US']
        data['Default Address Zip'] = ['12345-6789', '01234-5678', '99999-0000']  # Valid 5+4 formats
        # Add third customer data
        for key in data:
            if key not in ['Default Address Country Code', 'Default Address Zip']:
                if len(data[key]) == 2:
                    data[key].append(data[key][0])
        
        df = pd.DataFrame(data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_4digit_zip_codes_fixable(self):
        """Test validation identifies 4-digit zip codes as fixable."""
        data = self.valid_data.copy()
        data['Default Address Country Code'] = ['US', 'US']
        data['Default Address Zip'] = ['1234', '5678']  # Both 4-digit
        
        df = pd.DataFrame(data)
        result = self.transformer.validate_dataframe(df)
        
        self.assertFalse(result['valid'])  # Should fail validation
        self.assertTrue('fixable_zip_errors' in result)
        self.assertEqual(len(result['fixable_zip_errors']), 2)  # Both should be fixable
        
        # Check fixable error details
        fixable_errors = result['fixable_zip_errors']
        self.assertEqual(fixable_errors[0]['zip'], '1234')
        self.assertEqual(fixable_errors[0]['fixed_zip'], '01234')
        self.assertEqual(fixable_errors[1]['zip'], '5678')
        self.assertEqual(fixable_errors[1]['fixed_zip'], '05678')
    
    def test_fix_4digit_zip_codes(self):
        """Test the zip code fixing functionality."""
        data = {
            'First Name': ['John', 'Jane', 'Bob'],
            'Last Name': ['Doe', 'Smith', 'Johnson'],
            'Email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
            'Default Address Country Code': ['US', 'US', 'CA'],
            'Default Address Zip': ['1234', '5678', '1234'],  # US 4-digit, US 4-digit, Canadian (ignored)
            'Accepts Email Marketing': [1, 0, 1],
            'Phone': ['123-456-7890', '098-765-4321', '555-123-4567'],
            'Default Address Company': ['ACME', 'XYZ', 'ABC'],
            'Default Address Address1': ['123 Main St', '456 Oak Ave', '789 Pine St'],
            'Default Address City': ['Boston', 'NYC', 'Toronto'],
            'Default Address Province Code': ['MA', 'NY', 'ON']
        }
        
        df = pd.DataFrame(data)
        fixed_df = self.transformer.fix_4digit_zip_codes(df)
        
        # Check that US 4-digit zips were fixed
        self.assertEqual(fixed_df.loc[0, 'Default Address Zip'], '01234')  # John
        self.assertEqual(fixed_df.loc[1, 'Default Address Zip'], '05678')  # Jane
        self.assertEqual(fixed_df.loc[2, 'Default Address Zip'], '1234')   # Bob (Canadian, unchanged)
        
        # Verify fixed data now passes validation
        result = self.transformer.validate_dataframe(fixed_df)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result.get('fixable_zip_errors', [])), 0)


class TestEmailMarketingTransformation(unittest.TestCase):
    """Test cases for email marketing transformation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CustomerToShopifyTransformer()
    
    def test_transform_email_marketing_with_ones(self):
        """Test transforming 1 values to 'yes'."""
        data = {
            'First Name': ['John', 'Jane'],
            'Accepts Email Marketing': [1, 1]
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform_email_marketing(df)
        
        self.assertEqual(result['Accepts Email Marketing'].tolist(), ['yes', 'yes'])
    
    def test_transform_email_marketing_with_zeros(self):
        """Test transforming 0 values to 'no'."""
        data = {
            'First Name': ['John', 'Jane'],
            'Accepts Email Marketing': [0, 0]
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform_email_marketing(df)
        
        self.assertEqual(result['Accepts Email Marketing'].tolist(), ['no', 'no'])
    
    def test_transform_email_marketing_with_null_values(self):
        """Test transforming null/NaN values to 'no'."""
        data = {
            'First Name': ['John', 'Jane', 'Bob'],
            'Accepts Email Marketing': [np.nan, None, '']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform_email_marketing(df)
        
        self.assertEqual(result['Accepts Email Marketing'].tolist(), ['no', 'no', 'no'])
    
    def test_transform_email_marketing_mixed_values(self):
        """Test transforming mixed values."""
        data = {
            'First Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Accepts Email Marketing': [1, 0, np.nan, 2, 'yes']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform_email_marketing(df)
        
        expected = ['yes', 'no', 'no', 'no', 'no']
        self.assertEqual(result['Accepts Email Marketing'].tolist(), expected)
    
    def test_transform_email_marketing_missing_column(self):
        """Test handling when column doesn't exist."""
        data = {
            'First Name': ['John', 'Jane'],
            'Last Name': ['Doe', 'Smith']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform_email_marketing(df)
        
        # Should not create the column if it doesn't exist
        self.assertNotIn('Accepts Email Marketing', result.columns)


class TestTagsColumnCreation(unittest.TestCase):
    """Test cases for tags column creation based on retailer status."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CustomerToShopifyTransformer()
    
    def test_create_tags_from_is_retailer_yes(self):
        """Test creating tags when Is_Retailer is 'yes'."""
        data = {
            'First Name': ['John', 'Jane'],
            'Is_Retailer': ['yes', 'no']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        self.assertEqual(result['Tags'].tolist(), ['Retailer', ''])
    
    def test_create_tags_from_is_retailer_case_insensitive(self):
        """Test that Is_Retailer check is case insensitive."""
        data = {
            'First Name': ['John', 'Jane', 'Bob', 'Alice'],
            'Is_Retailer': ['YES', 'Yes', 'yEs', 'no']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        expected = ['Retailer', 'Retailer', 'Retailer', '']
        self.assertEqual(result['Tags'].tolist(), expected)
    
    def test_create_tags_from_role_retailer(self):
        """Test creating tags when Role is 'retailer'."""
        data = {
            'First Name': ['John', 'Jane'],
            'Role': ['retailer', 'customer']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        self.assertEqual(result['Tags'].tolist(), ['Retailer', ''])
    
    def test_create_tags_from_role_case_insensitive(self):
        """Test that Role check is case insensitive."""
        data = {
            'First Name': ['John', 'Jane', 'Bob', 'Alice'],
            'Role': ['RETAILER', 'Retailer', 'rEtAiLeR', 'customer']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        expected = ['Retailer', 'Retailer', 'Retailer', '']
        self.assertEqual(result['Tags'].tolist(), expected)
    
    def test_is_retailer_takes_precedence_over_role(self):
        """Test that Is_Retailer column takes precedence over Role column."""
        data = {
            'First Name': ['John', 'Jane', 'Bob'],
            'Is_Retailer': ['yes', 'no', 'yes'],
            'Role': ['customer', 'retailer', 'customer']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        # Is_Retailer should override Role
        # John: Is_Retailer='yes' overrides Role='customer' -> 'Retailer'
        # Jane: Is_Retailer='no' overrides Role='retailer' -> ''
        # Bob: Is_Retailer='yes' overrides Role='customer' -> 'Retailer'
        expected = ['Retailer', '', 'Retailer']
        self.assertEqual(result['Tags'].tolist(), expected)
    
    def test_create_tags_with_only_role_column(self):
        """Test creating tags when only Role column exists."""
        data = {
            'First Name': ['John', 'Jane'],
            'Role': ['retailer', 'customer']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        self.assertEqual(result['Tags'].tolist(), ['Retailer', ''])
    
    def test_create_tags_with_only_is_retailer_column(self):
        """Test creating tags when only Is_Retailer column exists."""
        data = {
            'First Name': ['John', 'Jane'],
            'Is_Retailer': ['yes', 'no']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        self.assertEqual(result['Tags'].tolist(), ['Retailer', ''])
    
    def test_create_tags_with_neither_column(self):
        """Test creating tags when neither column exists."""
        data = {
            'First Name': ['John', 'Jane'],
            'Last Name': ['Doe', 'Smith']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        # Should create empty tags column
        self.assertEqual(result['Tags'].tolist(), ['', ''])
    
    def test_create_tags_with_null_values(self):
        """Test creating tags with null values in retailer columns."""
        data = {
            'First Name': ['John', 'Jane', 'Bob', 'Alice'],
            'Is_Retailer': ['yes', np.nan, 'no', None],
            'Role': ['customer', 'retailer', np.nan, None]
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.create_tags_column(df)
        
        # John: Is_Retailer='yes' -> 'Retailer'
        # Jane: Is_Retailer=NaN, falls back to Role='retailer' -> 'Retailer' 
        # Bob: Is_Retailer='no' overrides Role=NaN -> ''
        # Alice: Is_Retailer=None, falls back to Role=None -> ''
        expected = ['Retailer', 'Retailer', '', '']
        self.assertEqual(result['Tags'].tolist(), expected)


class TestCompleteTransformation(unittest.TestCase):
    """Test cases for complete customer data transformation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CustomerToShopifyTransformer()
    
    def test_complete_transformation(self):
        """Test complete transformation with all features."""
        data = {
            'First Name': ['John', 'Jane', 'Bob'],
            'Last Name': ['Doe', 'Smith', 'Johnson'],
            'Email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
            'Accepts Email Marketing': [1, 0, np.nan],
            'Is_Retailer': ['yes', 'no', np.nan],
            'Role': ['customer', 'retailer', 'retailer'],
            'Phone': ['123-456-7890', '098-765-4321', '555-555-5555']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform(df)
        
        # Check email marketing transformation
        expected_email = ['yes', 'no', 'no']
        self.assertEqual(result['Accepts Email Marketing'].tolist(), expected_email)
        
        # Check tags creation (Is_Retailer takes precedence when not null)
        expected_tags = ['Retailer', '', 'Retailer']  # John=Retailer, Jane=no overrides retailer, Bob=NaN falls back to Role=retailer
        self.assertEqual(result['Tags'].tolist(), expected_tags)
        
        # Check that other columns are preserved
        self.assertEqual(result['First Name'].tolist(), ['John', 'Jane', 'Bob'])
        self.assertEqual(result['Phone'].tolist(), ['123-456-7890', '098-765-4321', '555-555-5555'])
        
        # Check that Note column is added
        self.assertIn('Note', result.columns)
        self.assertEqual(result['Note'].tolist(), ['Imported from WooCommerce', 'Imported from WooCommerce', 'Imported from WooCommerce'])
        
        # Check that Role and Is_Retailer columns are dropped
        self.assertNotIn('Role', result.columns)
        self.assertNotIn('Is_Retailer', result.columns)
    
    def test_transform_with_minimal_data(self):
        """Test transformation with minimal required data."""
        data = {
            'First Name': ['John'],
            'Last Name': ['Doe'],
            'Email': ['john@example.com'],
            'Accepts Email Marketing': [1],
            'Default Address Company': [''],
            'Default Address Address1': ['123 Main St'],
            'Default Address City': ['New York'],
            'Default Address Province Code': ['NY'],
            'Default Address Country Code': ['US'],
            'Phone': ['123-456-7890']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform(df)
        
        # Should handle transformation without errors
        self.assertEqual(result['Accepts Email Marketing'].tolist(), ['yes'])
        self.assertEqual(result['Tags'].tolist(), [''])  # Tags column gets created during transformation
    
    def test_data_cleaning(self):
        """Test data cleaning functionality."""
        data = {
            'First Name': ['John', np.nan],
            'Last Name': ['Doe', None],
            'Email': ['john@example.com', 'jane@example.com'],
            'Phone': [np.nan, '123-456-7890']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.clean_data(df)
        
        # Null values should be converted to empty strings
        self.assertEqual(result['First Name'].tolist(), ['John', ''])
        self.assertEqual(result['Last Name'].tolist(), ['Doe', ''])
        self.assertEqual(result['Phone'].tolist(), ['', '123-456-7890'])
    
    def test_note_column_and_dropped_columns(self):
        """Test that Note column is added and Role/Is_Retailer columns are dropped."""
        data = {
            'First Name': ['John', 'Jane'],
            'Last Name': ['Doe', 'Smith'],
            'Email': ['john@example.com', 'jane@example.com'],
            'Accepts Email Marketing': [1, 0],
            'Is_Retailer': ['yes', 'no'],
            'Role': ['customer', 'retailer'],
            'Phone': ['123-456-7890', '098-765-4321']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform(df)
        
        # Check Note column is added with correct value
        self.assertIn('Note', result.columns)
        self.assertEqual(result['Note'].tolist(), ['Imported from WooCommerce', 'Imported from WooCommerce'])
        
        # Check that Role and Is_Retailer columns are dropped
        self.assertNotIn('Role', result.columns)
        self.assertNotIn('Is_Retailer', result.columns)
        
        # Check that other transformations still work
        self.assertEqual(result['Accepts Email Marketing'].tolist(), ['yes', 'no'])
        self.assertEqual(result['Tags'].tolist(), ['Retailer', ''])  # Is_Retailer takes precedence
    
    def test_preserve_leading_zeros(self):
        """Test that leading zeros are preserved in string fields."""
        data = {
            'First Name': ['John'],
            'Last Name': ['Doe'],
            'Email': ['john@example.com'],
            'Accepts Email Marketing': [1],
            'Default Address Zip': ['01234'],  # Zip with leading zero
            'Phone': ['0123456789'],  # Phone with leading zero
            'Default Address Province Code': ['MA'],
            'Default Address Country Code': ['US'],
            'Default Address Company': ['ACME'],
            'Default Address Address1': ['123 Main St'],
            'Default Address City': ['Boston']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform(df)
        
        # Check that leading zeros are preserved
        if 'Default Address Zip' in result.columns:
            self.assertEqual(result['Default Address Zip'].iloc[0], '01234')
        if 'Phone' in result.columns:
            self.assertEqual(result['Phone'].iloc[0], '0123456789')


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transformer = CustomerToShopifyTransformer()
    
    def test_empty_dataframe(self):
        """Test transformation with empty dataframe."""
        df = pd.DataFrame()
        result = self.transformer.transform(df)
        
        # Should handle empty dataframe gracefully
        self.assertTrue(result.empty)
        self.assertIn('Tags', result.columns)
    
    def test_single_row_dataframe(self):
        """Test transformation with single row."""
        data = {
            'First Name': ['John'],
            'Accepts Email Marketing': [1],
            'Is_Retailer': ['yes']
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform(df)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result['Accepts Email Marketing'].iloc[0], 'yes')
        self.assertEqual(result['Tags'].iloc[0], 'Retailer')
    
    def test_large_dataset_performance(self):
        """Test transformation with larger dataset."""
        size = 1000
        data = {
            'First Name': ['John'] * size,
            'Last Name': ['Doe'] * size,
            'Email': [f'user{i}@example.com' for i in range(size)],
            'Accepts Email Marketing': [1 if i % 2 == 0 else 0 for i in range(size)],
            'Is_Retailer': ['yes' if i % 3 == 0 else 'no' for i in range(size)],
            'Phone': ['123-456-7890'] * size
        }
        df = pd.DataFrame(data)
        
        result = self.transformer.transform(df)
        
        self.assertEqual(len(result), size)
        # Check that transformations were applied correctly
        retailer_count = sum(1 for tag in result['Tags'] if tag == 'Retailer')
        expected_retailers = sum(1 for i in range(size) if i % 3 == 0)
        self.assertEqual(retailer_count, expected_retailers)


if __name__ == '__main__':
    unittest.main()