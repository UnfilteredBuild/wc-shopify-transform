"""
Customer data transformation module for Shopify import.
"""

import pandas as pd
from typing import Dict, Any, List


class CustomerToShopifyTransformer:
    """Transforms customer data to Shopify import format."""
    
    def __init__(self):
        self.required_columns = [
            'First Name', 'Last Name', 'Email', 'Accepts Email Marketing',
            'Default Address Company', 'Default Address Address1', 
            'Default Address City', 'Default Address Province Code',
            'Default Address Country Code', 'Phone'
        ]
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate that the DataFrame has required columns and data integrity."""
        errors = []
        fixable_zip_errors = []
        
        # Check for required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for empty emails
        if 'Email' in df.columns:
            empty_emails = df['Email'].isna().sum()
            if empty_emails > 0:
                errors.append(f"{empty_emails} customers have empty email addresses")
        
        # Check US zip code format (5 digits OR 5 digits + dash + 4 digits)
        if 'Default Address Country Code' in df.columns and 'Default Address Zip' in df.columns:
            import re
            
            # Convert to string and handle nulls
            country_codes = df['Default Address Country Code'].astype(str).str.upper()
            zip_codes = df['Default Address Zip'].astype(str)
            
            # Find US entries
            us_mask = country_codes == 'US'
            us_customers = df[us_mask]
            
            if len(us_customers) > 0:
                invalid_zips = []
                fixable_4digit_zips = []
                
                # US zip code patterns: 12345 OR 12345-6789
                zip_pattern = re.compile(r'^\d{5}(-\d{4})?$')
                four_digit_pattern = re.compile(r'^\d{4}$')
                
                for idx, row in us_customers.iterrows():
                    zip_code = str(row['Default Address Zip']).strip()
                    # Skip empty/null values
                    if zip_code == 'nan' or zip_code == '':
                        continue
                    
                    # Check if zip matches valid US format
                    if not zip_pattern.match(zip_code):
                        customer_name = f"{row.get('First Name', 'Unknown')} {row.get('Last Name', 'Customer')}"
                        
                        # Check if it's a 4-digit zip that can be auto-fixed
                        if four_digit_pattern.match(zip_code):
                            fixable_4digit_zips.append({
                                'row': idx + 2,
                                'customer': customer_name,
                                'zip': zip_code,
                                'fixed_zip': f"0{zip_code}"
                            })
                        else:
                            invalid_zips.append(f"Row {idx + 2}: {customer_name} - '{zip_code}' (must be 5 digits or 5+4 format like '12345-6789')")
                
                # Handle fixable 4-digit zips
                if fixable_4digit_zips:
                    fixable_zip_errors = fixable_4digit_zips
                    fixable_details = [f"Row {item['row']}: {item['customer']} - '{item['zip']}' → '{item['fixed_zip']}'" 
                                     for item in fixable_4digit_zips]
                    errors.append(f"4-digit US zip codes found that can be auto-fixed by adding leading zero:\n" + 
                                "\n".join(fixable_details))
                
                # Handle other invalid zips
                if invalid_zips:
                    errors.append(f"Invalid US zip codes found. US zip codes must be 5 digits or 5+4 format (12345 or 12345-6789):\n" + 
                                "\n".join(invalid_zips))
        
        # Check US state codes (2 characters for US addresses)
        if 'Default Address Country Code' in df.columns and 'Default Address Province Code' in df.columns:
            import re
            
            # Convert to string and handle nulls
            country_codes = df['Default Address Country Code'].astype(str).str.upper()
            province_codes = df['Default Address Province Code'].astype(str)
            
            # Find US entries
            us_mask = country_codes == 'US'
            us_customers = df[us_mask]
            
            if len(us_customers) > 0:
                invalid_states = []
                
                # US state code pattern: exactly 2 uppercase letters
                state_pattern = re.compile(r'^[A-Z]{2}$')
                
                for idx, row in us_customers.iterrows():
                    state_code_raw = row['Default Address Province Code']
                    # Check for truly empty/null values first
                    if pd.isna(state_code_raw) or str(state_code_raw).strip() == '' or str(state_code_raw).strip().lower() == 'nan':
                        customer_name = f"{row.get('First Name', 'Unknown')} {row.get('Last Name', 'Customer')}"
                        invalid_states.append(f"Row {idx + 2}: {customer_name} - Empty state code")
                        continue
                    
                    state_code = str(state_code_raw).strip().upper()
                    
                    # Check if state code matches valid US format (2 letters)
                    if not state_pattern.match(state_code):
                        customer_name = f"{row.get('First Name', 'Unknown')} {row.get('Last Name', 'Customer')}"
                        invalid_states.append(f"Row {idx + 2}: {customer_name} - '{state_code}' (must be 2-letter US state code like 'CA', 'NY', 'TX')")
                
                # Handle invalid state codes
                if invalid_states:
                    error_count = len(invalid_states)
                    errors.append(f"Invalid US state codes found ({error_count} issue{'s' if error_count != 1 else ''}). US addresses must have 2-letter state codes (e.g., CA, NY, TX, FL):\n" + 
                                "\n".join(invalid_states) + 
                                "\n\nTo fix: Replace with valid 2-letter US state abbreviations. Common examples:\n" +
                                "• California = CA\n• New York = NY\n• Texas = TX\n• Florida = FL\n• Illinois = IL\n• Pennsylvania = PA")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'fixable_zip_errors': fixable_zip_errors
        }
    
    def fix_4digit_zip_codes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix 4-digit US zip codes by adding leading zero."""
        if 'Default Address Country Code' not in df.columns or 'Default Address Zip' not in df.columns:
            return df
        
        import re
        
        # Create a copy to modify
        fixed_df = df.copy()
        
        # Convert to string and handle nulls
        country_codes = fixed_df['Default Address Country Code'].astype(str).str.upper()
        
        # Find US entries
        us_mask = country_codes == 'US'
        
        # Pattern to match exactly 4 digits
        four_digit_pattern = re.compile(r'^\d{4}$')
        
        # Fix 4-digit zip codes for US addresses
        for idx in fixed_df[us_mask].index:
            zip_code = str(fixed_df.loc[idx, 'Default Address Zip']).strip()
            
            # If it's a 4-digit zip, add leading zero
            if four_digit_pattern.match(zip_code):
                fixed_df.loc[idx, 'Default Address Zip'] = f"0{zip_code}"
        
        return fixed_df
    
    def transform_email_marketing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform 'Accepts Email Marketing' column values."""
        if 'Accepts Email Marketing' in df.columns:
            df['Accepts Email Marketing'] = df['Accepts Email Marketing'].apply(
                lambda x: 'yes' if x == 1 else 'no'
            )
        return df
    
    def create_tags_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create 'Tags' column based on 'Role' column only (Is_Retailer logic removed)."""
        # Create "Tags" column
        df['Tags'] = ''
        
        # Check Role column - if it contains 'retailer', set Tags to 'Retailer'
        # Note: Is_Retailer column is ignored - only Role column determines tags
        if 'Role' in df.columns:
            mask_role = (df['Role'].notna()) & (df['Role'].str.lower() == 'retailer')
            df.loc[mask_role, 'Tags'] = 'Retailer'
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize customer data."""
        cleaned_df = df.copy()
        
        # Ensure string fields that might have leading zeros are treated as strings
        preserve_leading_zero_columns = [
            'Default Address Zip', 'Phone', 'Default Address Province Code',
            'Default Address Country Code'
        ]
        for col in preserve_leading_zero_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str)
        
        # Clean up any null values in string columns
        string_columns = ['First Name', 'Last Name', 'Email', 'Phone', 'Tags', 
                         'Default Address Zip', 'Default Address Province Code', 
                         'Default Address Country Code']
        for col in string_columns:
            if col in cleaned_df.columns:
                # Convert nan strings back to empty strings
                cleaned_df[col] = cleaned_df[col].replace('nan', '').fillna('')
        
        return cleaned_df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform customer DataFrame to Shopify import format."""
        # Create a copy to work with
        transformed_df = df.copy()
        
        # Apply transformations
        transformed_df = self.transform_email_marketing(transformed_df)
        transformed_df = self.create_tags_column(transformed_df)
        transformed_df = self.clean_data(transformed_df)
        
        # Add Note column with default value
        transformed_df['Note'] = 'Imported from WooCommerce'
        
        # Drop columns that shouldn't be in the final output
        columns_to_drop = ['Role', 'Is_Retailer']  # Drop both Role and Is_Retailer from final output
        existing_columns_to_drop = [col for col in columns_to_drop if col in transformed_df.columns]
        if existing_columns_to_drop:
            transformed_df = transformed_df.drop(columns=existing_columns_to_drop)
        
        # Create a clean DataFrame with only the remaining columns to ensure no phantom columns
        final_columns = [col for col in transformed_df.columns if col not in columns_to_drop]
        clean_df = transformed_df[final_columns].copy()
        clean_df.reset_index(drop=True, inplace=True)
        
        # Additional cleanup: rename any empty column names to avoid CSV issues
        new_columns = []
        for col in clean_df.columns:
            if not col or col.strip() == '':
                # Skip empty columns entirely by not including them
                continue
            new_columns.append(col.strip())
        
        # Only keep columns with valid names
        if len(new_columns) != len(clean_df.columns):
            clean_df = clean_df.loc[:, [col for col in clean_df.columns if col and col.strip()]]
        
        return clean_df