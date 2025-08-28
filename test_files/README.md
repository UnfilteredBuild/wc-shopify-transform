# Test Files Directory

This directory contains CSV test files for validating the customer import functionality.

## Test Files Overview

### Zip Code Validation Tests

#### `test_4digit_zips.csv`
- **Purpose**: Test 4-digit US zip codes that need leading zeros
- **Contains**: US customers with zip codes like `2101`, `1001`
- **Expected Behavior**: Should show fixable validation errors and "Fix Zip Codes" button

#### `test_invalid_zips.csv`
- **Purpose**: Test various invalid US zip code formats
- **Contains**: Mix of too short (`1234`) and too long (`123456`) zip codes
- **Expected Behavior**: Should show validation errors that cannot be auto-fixed

#### `test_leading_zeros.csv`
- **Purpose**: Test that leading zeros are preserved in valid zip codes
- **Contains**: Valid 5-digit zip codes with leading zeros like `01234`
- **Expected Behavior**: Should pass validation and preserve leading zeros

#### `test_mixed_zip_formats.csv`
- **Purpose**: Test mix of valid and invalid zip code formats
- **Contains**: Valid 5-digit, valid 5+4, invalid short, and invalid incomplete formats
- **Expected Behavior**: Should show validation errors for invalid formats only

#### `test_valid_zip_formats.csv`
- **Purpose**: Test both acceptable US zip code formats
- **Contains**: Valid 5-digit (`02101`) and valid 5+4 (`10001-1234`) formats
- **Expected Behavior**: Should pass all validation checks

#### `test_validation_examples.csv`
- **Purpose**: Test comprehensive validation scenarios
- **Contains**: Mix of valid US, invalid US, and non-US addresses
- **Expected Behavior**: Should validate only US addresses according to US rules

#### `test_zip_fix_workflow.csv`
- **Purpose**: Test complete fix workflow from detection to resolution
- **Contains**: Mix of 4-digit fixable and already-valid formats
- **Expected Behavior**: Should offer to fix some, leave others unchanged

## Usage

These files can be used to:
1. **Manual Testing**: Upload through the Streamlit customer import interface
2. **Unit Testing**: Reference in automated test cases
3. **Validation**: Verify specific edge cases and error handling

## File Format

All test files follow the customer CSV template format with required columns:
- First Name, Last Name, Email, Accepts Email Marketing
- Default Address fields (Company, Address1, City, Province Code, Country Code, Zip)
- Phone, Role

#### **New Test File:**

#### `test_role_only.csv`
- **Purpose**: Test Role-based tagging (Is_Retailer logic completely removed)
- **Contains**: Customers with Role='retailer' and Role='customer'
- **Expected Behavior**: Should create Tags='Retailer' only for Role='retailer' entries

#### `test_invalid_us_states.csv`
- **Purpose**: Test US state code validation for various invalid formats
- **Contains**: Mix of full state names, single characters, empty values, and valid codes
- **Expected Behavior**: Should show validation errors for invalid US state codes with helpful fix instructions and bypass button

#### `test_mixed_errors.csv`
- **Purpose**: Test mixed validation errors (critical + bypassable)
- **Contains**: Customers with empty email (critical) AND invalid state codes (bypassable)
- **Expected Behavior**: Should NOT show bypass button due to critical validation errors

#### `test_bypass_workflow.csv`
- **Purpose**: Test complete bypass workflow with both zip fixes and state bypass
- **Contains**: Customer with 4-digit zip (fixable) AND invalid state code (bypassable)
- **Expected Behavior**: Should fix zip code first, then allow bypass for state code while preserving fixed zip

## Expected Validation Rules

- **US Zip Codes**: Must be exactly 5 digits OR 5+4 format (12345-6789)
- **4-Digit US Zips**: Automatically fixable by adding leading zero
- **Non-US Addresses**: Zip/postal codes not validated for format
- **Empty Zips**: Allowed for any country
- **US State Codes**: Must be exactly 2 letters (e.g., CA, NY, TX, FL) for US addresses
- **Non-US State/Province Codes**: No format validation applied
- **Empty US State Codes**: Not allowed - will show validation error with fix instructions

## Bypass Feature

- **Bypassable Errors**: US state code validation errors can be bypassed with "Bypass Fixes and Download" button
- **Non-Bypassable Errors**: Missing required columns, empty emails, and other critical validation errors cannot be bypassed
- **Mixed Scenarios**: If both bypassable and non-bypassable errors exist, bypass button will not appear