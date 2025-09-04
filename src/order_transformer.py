"""
Order data transformer for converting various order export formats to Shopify import format.
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, Any, Optional


class OrderToShopifyTransformer:
    """Transform order data to Shopify import format using Matrixify template."""
    
    def __init__(self):
        """Initialize the transformer with Shopify column mappings."""
        self.shopify_columns = [
            'Name', 'Command', 'Send Receipt', 'Inventory Behaviour', 'Note', 'Tags', 'Tags Command', 
            'Created At', 'Updated At', 'Cancelled At', 'Cancel: Reason', 'Cancel: Send Receipt', 
            'Processed At', 'Closed At', 'Currency', 'Tax 1: Title', 'Tax 1: Rate', 'Tax 1: Price', 
            'Tax 2: Title', 'Tax 2: Rate', 'Tax 2: Price', 'Tax 3: Title', 'Tax 3: Rate', 'Tax 3: Price', 
            'Tax: Included', 'Tax: Total', 'Payment: Status', 'Additional Details', 'Customer: Email', 
            'Customer: Phone', 'Billing: First Name', 'Billing: Last Name', 'Billing: Company', 
            'Billing: Phone', 'Billing: Address 1', 'Billing: Address 2', 'Billing: Zip', 'Billing: City', 
            'Billing: Province', 'Billing: Province Code', 'Billing: Country', 'Billing: Country Code', 
            'Shipping: First Name', 'Shipping: Last Name', 'Shipping: Company', 'Shipping: Phone', 
            'Shipping: Address 1', 'Shipping: Address 2', 'Shipping: Zip', 'Shipping: City', 
            'Shipping: Province', 'Shipping: Province Code', 'Shipping: Country', 'Shipping: Country Code', 
            'Row #', 'Top Row', 'Line: Type', 'Line: ID', 'Line: Product Handle', 'Line: Title', 
            'Line: Name', 'Line: Variant ID', 'Line: Variant Title', 'Line: SKU', 'Line: Quantity', 
            'Line: Price', 'Line: Discount', 'Line: Total', 'Line: Grams', 'Line: Requires Shipping', 
            'Line: Vendor', 'Line: Properties', 'Line: Gift Card', 'Line: Taxable', 'Line: Tax 1 Title', 
            'Line: Tax 1 Rate', 'Line: Tax 1 Price', 'Line: Tax 2 Title', 'Line: Tax 2 Rate', 
            'Line: Tax 2 Price', 'Line: Tax 3 Title', 'Line: Tax 3 Rate', 'Line: Tax 3 Price', 
            'Line: Fulfillable Quantity', 'Line: Fulfillment Service', 'Line: Fulfillment Status', 
            'Refund: ID', 'Refund: Created At', 'Refund: Note', 'Refund: Restock', 'Refund: Restock Type', 
            'Refund: Restock Location', 'Refund: Send Receipt', 'Refund: Generate Transaction', 
            'Transaction: ID', 'Transaction: Kind', 'Transaction: Processed At', 'Transaction: Amount', 
            'Transaction: Currency', 'Transaction: Status', 'Transaction: Message', 'Transaction: Gateway', 
            'Transaction: Test', 'Transaction: Authorization', 'Transaction: Error Code', 
            'Transaction: CC AVS Result', 'Transaction: CC Bin', 'Transaction: CC CVV Result', 
            'Transaction: CC Number', 'Transaction: CC Company', 'Fulfillment: ID', 
            'Fulfillment: Processed At', 'Fulfillment: Status', 'Fulfillment: Shipment Status', 
            'Fulfillment: Location', 'Fulfillment: Tracking Company', 'Fulfillment: Tracking Number', 
            'Fulfillment: Tracking URL', 'Fulfillment: Send Receipt', 'ID (Ref)', 'Name (Ref)', 
            'Import Result', 'Import Comment', 'Metafield: woo.id', 'Metafield: woo.created_via', 
            'Metafield: woo.customer_id', 'Metafield: woo.transaction_id', 'Metafield: woo.payment_method', 
            'Metafield: woo.is_vat_exempt', 'Metafield: woo._woo_pp_txnData', 'Metafield: woo._paypal_status', 
            'Metafield: woo._paypal_transaction_fee', 'Metafield: woo.Payer PayPal address', 
            'Metafield: woo.Payer first name', 'Metafield: woo.Payer last name', 'Metafield: woo.Payment type', 
            'Metafield: woo._order_number', 'Metafield: woo._order_number_formatted', 
            'Metafield: woo._alg_wc_mppu_order_data_saved', 'Metafield: woo._wp_page_template', 
            'Metafield: woo._stripe_customer_id', 'Metafield: woo._stripe_source_id', 
            'Metafield: woo._stripe_intent_id', 'Metafield: woo._stripe_charge_captured', 
            'Metafield: woo._stripe_fee', 'Metafield: woo._stripe_net', 'Metafield: woo._stripe_currency', 
            'Metafield: woo.wc-shippo-shipping_shipments', 'Metafield: woo._wcpdf_invoice_settings', 
            'Metafield: woo._wcpdf_packing_slip_date', 'Metafield: woo._wcpdf_packing_slip_date_formatted', 
            'Metafield: woo._sequential_order_number_id', 'Metafield: woo._sequential_order_number', 
            'Metafield: woo._start_sequential_order_number', 'Metafield: woo._order_number_meta', 
            'Metafield: woo.wc-shippo-shipping_shipments_updated', 'Metafield: woo._stripe_refund_id', 
            'Metafield: woo._auction', 'Metafield: woo._wc_facebook_for_woocommerce_order_placed', 
            'Metafield: woo._wc_facebook_for_woocommerce_purchase_tracked', 'Metafield: woo.wf_invoice_number', 
            'Metafield: woo.mailchimp_woocommerce_landing_site', 'Metafield: woo._wf_invoice_date', 
            'Metafield: woo.wf_invoice_html', 'Metafield: woo._created_document_old', 
            'Metafield: woo.mailchimp_woocommerce_is_subscribed', 'Metafield: woo.mailchimp_woocommerce_campaign_id', 
            'Metafield: woo._stripe_status_before_hold', 'Metafield: woo._stripe_status_final', 
            'Metafield: woo._wcpdf_packing-slip_creation_trigger', 'Metafield: woo._wcpdf_packing_slip_creation_trigger', 
            'Metafield: woo._wcpdf_invoice_display_date', 'Metafield: woo._wc_order_attribution_source_type', 
            'Metafield: woo._wc_order_attribution_referrer', 'Metafield: woo._wc_order_attribution_utm_source', 
            'Metafield: woo._wc_order_attribution_session_entry', 'Metafield: woo._wc_order_attribution_session_start_time', 
            'Metafield: woo._wc_order_attribution_session_pages', 'Metafield: woo._wc_order_attribution_session_count', 
            'Metafield: woo._wc_order_attribution_user_agent', 'Metafield: woo._wc_order_attribution_device_type', 
            'Metafield: woo._wc_order_attribution_utm_medium', 'Metafield: woo._ppcp_paypal_order_id', 
            'Metafield: woo._ppcp_paypal_intent', 'Metafield: woo._ppcp_paypal_payment_mode', 
            'Metafield: woo._ppcp_paypal_payment_source', 'Metafield: woo._ppcp_paypal_fees', 
            'Metafield: woo.PayPal Transaction Fee', 'Metafield: woo._ppcp_refunds', 
            'Metafield: woo._ppcp_paypal_refund_fees', 'Metafield: woo._wc_order_attribution_utm_content', 
            'Metafield: woo._wc_stripe_charge_status', 'Metafield: woo._wc_order_attribution_utm_campaign', 
            'Metafield: woo._ppcp_paypal_payer_email', 'Metafield: woo._payment_intent_id', 
            'Metafield: woo._ppcp_paypal_tracking_info_meta_name', 'Metafield: woo._stripe_upe_payment_type', 
            'Metafield: woo._ppcp_paypal_captured', 'Metafield: woo.wt_store_credit_used', 
            'Metafield: woo._stripe_upe_waiting_for_redirect', 'Metafield: woo._stripe_upe_redirect_processed', 
            'Metafield: woo.wt_pklist_order_language', 'Metafield: woo._wt_thankyou_action_done', 
            'Metafield: woo._created_document', 'Metafield: woo._stripe_payment_awaiting_action', 
            'Metafield: woo._stripe_lock_payment', 'Metafield: woo._shipping_hash', 'Metafield: woo._coupons_hash', 
            'Metafield: woo._fees_hash', 'Metafield: woo._taxes_hash', 'Metafield: woo.urcr_allow_to', 
            'Metafield: woo._meta_purchase_tracked', 'Metafield: woo._ppcp_paypal_billing_phone', 
            'Metafield: woo._ppcp_paypal_billing_email', 'Metafield: woo.urcr_meta_content'
        ]
        
        # Common column mappings for different input formats
        self.column_mappings = {
            # WooCommerce format mappings
            'woocommerce': {
                'Name': 'Name',
                'Customer: Email': 'Customer: Email',
                'Processed At': 'Processed At',
                'Line: Title': 'Line: Title',
                'Line: SKU': 'Line: SKU',
                'Line: Quantity': 'Line: Quantity',
                'Line: Price': 'Line: Price',
                'Line: Total': 'Line: Total',
                'Transaction: Amount': 'Transaction: Amount',
            }
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the input dataframe for order transformation.
        
        Args:
            df: Input dataframe to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check if dataframe is empty
        if df.empty:
            errors.append("❌ Empty dataframe provided")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for essential columns
        essential_columns = ['Name', 'Customer: Email']
        missing_essential = [col for col in essential_columns if col not in df.columns]
        
        if missing_essential:
            errors.append(f"❌ Missing essential columns: {', '.join(missing_essential)}")
        
        # Check for line item data
        line_columns = [col for col in df.columns if col.startswith('Line:')]
        if not line_columns:
            warnings.append("⚠️ No line item columns found - will create basic order structure")
        
        # Check for transaction data
        if 'Transaction: Amount' not in df.columns and 'Line: Total' not in df.columns:
            warnings.append("⚠️ No transaction amount data found")
        
        # Run email fallback validation to check for missing emails (but don't modify the original df)
        temp_df = df.copy()
        self.email_fallback_warnings = []  # Initialize the list first
        self._handle_email_fallbacks(temp_df)
        
        # Add email fallback warnings if any were found
        if self.email_fallback_warnings:
            warnings.append("📧 Missing customer emails detected - the following fallback emails will be used:")
            warnings.extend([f"   • {warning}" for warning in self.email_fallback_warnings])
        
        # Run phone validation to check for issues (but don't modify the original df)
        self.phone_validation_warnings = []  # Initialize the list first
        self._validate_and_clean_phone_numbers(temp_df)
        
        # Add phone validation warnings if any were found
        if self.phone_validation_warnings:
            warnings.append("📞 Phone number formatting issues detected - the following will be cleaned:")
            warnings.extend([f"   • {warning}" for warning in self.phone_validation_warnings])
        
        # Validation passed if no errors
        valid = len(errors) == 0
        
        return {
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'row_count': len(df)
        }
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform order data to Shopify import format.
        
        Args:
            df: Input dataframe with order data
            
        Returns:
            Transformed dataframe ready for Shopify import
        """
        # Create a copy of the dataframe to preserve original data
        df_copy = df.copy()
        
        # Initialize warnings
        self.phone_validation_warnings = []
        self.email_fallback_warnings = []
        
        # Ensure all required columns exist in the output (add missing columns with None)
        for col in self.shopify_columns:
            if col not in df_copy.columns:
                df_copy[col] = None
        
        # Reorder columns to match the expected Shopify structure
        df_copy = df_copy[self.shopify_columns]
        
        # Fix data types first
        df_copy = self._fix_dataframe_types(df_copy)
        
        # Handle email fallbacks - only modify Customer: Email if empty
        df_copy = self._handle_email_fallbacks(df_copy)
        
        # Validate and clean phone numbers - only modify phone columns and Note as specified
        df_copy = self._validate_and_clean_phone_numbers(df_copy)
        
        # Clean up any "nan" string values AFTER all other processing
        df_copy = self._clean_nan_strings(df_copy)
        
        return df_copy
    
    def _clean_nan_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean up any values that display as 'nan' strings when converted to string.
        Replace them with appropriate empty values based on column type.
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with proper empty values instead of 'nan' strings
        """
        df_copy = df.copy()
        
        for col in df_copy.columns:
            # For each column, check what values would display as 'nan' when converted to string
            string_repr = df_copy[col].astype(str)
            nan_mask = string_repr == 'nan'
            
            if nan_mask.any():
                # Determine appropriate replacement based on column characteristics
                if df_copy[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                    # For numeric columns, keep as NaN (this is correct for CSV export)
                    continue  # Don't change numeric NaN values
                elif any(keyword in col for keyword in ['Price', 'Amount', 'Total', 'Rate', 'Grams', 'Weight', 'Discount', 'Quantity']):
                    # For numeric-named columns, keep as NaN
                    continue
                elif col in ['Top Row', 'Row #'] or any(val in [True, False] for val in df_copy[col].dropna().unique() if pd.notna(val)):
                    # For boolean-ish columns (like Top Row with True/False values), keep as NaN to avoid PyArrow issues
                    continue  # Don't change boolean columns - let them stay as NaN
                else:
                    # For string/text columns, replace with empty string
                    df_copy.loc[nan_mask, col] = ''
        
        return df_copy
    
    def _create_line_item_row(self, row: pd.Series, order_name: str, customer_email: str, processed_at: str) -> Dict[str, Any]:
        """Create a line item row for Shopify import."""
        
        # Extract line item details
        line_title = str(row.get('Line: Title', 'Product'))
        line_sku = str(row.get('Line: SKU', '')) if pd.notna(row.get('Line: SKU')) else ''
        line_quantity = self._safe_float_to_int(row.get('Line: Quantity', 1))
        line_price = self._safe_float(row.get('Line: Price', 0))
        line_total = self._safe_float(row.get('Line: Total', line_price * line_quantity))
        
        # Create product handle from title
        product_handle = self._create_handle(line_title)
        
        # Calculate transaction amount (could be line total or separate transaction amount)
        transaction_amount = self._safe_float(row.get('Transaction: Amount', line_total))
        
        # Determine fulfillment status
        fulfillment_status = self._determine_fulfillment_status(row)
        fulfillment_processed_at = self._format_date(row.get('Fulfillment: Processed At', ''))
        tracking_number = str(row.get('Fulfillment: Tracking Number', '')) if pd.notna(row.get('Fulfillment: Tracking Number')) else ''
        shipment_status = str(row.get('Fulfillment: Shipment Status', '')) if pd.notna(row.get('Fulfillment: Shipment Status')) else ''
        
        # Create the full row with all 125 columns
        result = {}
        for col in self.shopify_columns:
            # Initialize with None (completely empty) - only fill if data exists in original
            result[col] = None
        
        # Helper function to only set values if they exist in original data
        def set_if_exists(key, original_key=None, default=None, transform_func=None):
            lookup_key = original_key or key
            if lookup_key in row.index and pd.notna(row[lookup_key]):
                value = row[lookup_key]
                if transform_func:
                    value = transform_func(value)
                result[key] = value
            elif default is not None:
                result[key] = default
        
        # Populate ONLY the columns with available data (leave others as None)
        
        # Required fields that need values for Shopify functionality
        result['Name'] = order_name
        result['Command'] = 'NEW'
        result['Line: Type'] = 'Line Item'
        result['Line: Command'] = 'DEFAULT'
        
        # Conditionally populate other fields only if they exist in original data
        set_if_exists('Send Receipt')
        set_if_exists('Inventory Behaviour')
        set_if_exists('Number')
        set_if_exists('Phone')
        result['Email'] = customer_email  # This comes from email fallback logic
        set_if_exists('Note')
        set_if_exists('Tags')
        set_if_exists('Tags Command')
        set_if_exists('Processed At')
        set_if_exists('Closed At')
        set_if_exists('Currency')
        set_if_exists('Tax: Total', transform_func=self._safe_float)
        set_if_exists('Payment: Status')
        set_if_exists('Additional Details')
        
        # Customer fields
        set_if_exists('Customer: ID')
        result['Customer: Email'] = customer_email  # This comes from email fallback logic
        set_if_exists('Customer: Phone')
        set_if_exists('Customer: First Name')
        set_if_exists('Customer: Last Name')
        
        # Billing fields
        set_if_exists('Billing: First Name')
        set_if_exists('Billing: Last Name')
        set_if_exists('Billing: Phone')
        set_if_exists('Billing: Address 1')
        set_if_exists('Billing: Address 2')
        set_if_exists('Billing: Zip')
        set_if_exists('Billing: City')
        set_if_exists('Billing: Province')
        set_if_exists('Billing: Province Code')
        set_if_exists('Billing: Country')
        set_if_exists('Billing: Country Code')
        
        # Shipping fields
        set_if_exists('Shipping: First Name')
        set_if_exists('Shipping: Last Name')
        set_if_exists('Shipping: Phone')
        set_if_exists('Shipping: Address 1')
        set_if_exists('Shipping: Address 2')
        set_if_exists('Shipping: Zip')
        set_if_exists('Shipping: City')
        set_if_exists('Shipping: Province')
        set_if_exists('Shipping: Province Code')
        set_if_exists('Shipping: Country')
        set_if_exists('Shipping: Country Code')
        
        # Line item fields - set required ones and conditionally set others
        result['Line: Product Handle'] = product_handle
        result['Line: Title'] = line_title
        result['Line: Name'] = line_title
        result['Line: SKU'] = line_sku if line_sku else None
        result['Line: Quantity'] = line_quantity
        result['Line: Price'] = line_price
        set_if_exists('Line: Discount', transform_func=self._safe_float)
        set_if_exists('Line: Grams', transform_func=self._safe_float_to_int)
        set_if_exists('Line: Requires Shipping', transform_func=self._safe_bool)
        set_if_exists('Line: Vendor')
        set_if_exists('Line: Taxable', transform_func=self._safe_bool)
        set_if_exists('Line: Fulfillment Service')
        
        # Transaction fields - set required ones
        result['Transaction: Kind'] = 'sale'
        result['Transaction: Processed At'] = processed_at
        result['Transaction: Amount'] = transaction_amount
        set_if_exists('Transaction: Currency')
        result['Transaction: Status'] = 'success'
        set_if_exists('Transaction: Gateway')
        
        # Fulfillment fields
        result['Fulfillment: Status'] = fulfillment_status if fulfillment_status != 'unfulfilled' else None
        result['Fulfillment: Processed At'] = fulfillment_processed_at if fulfillment_processed_at else None
        result['Fulfillment: Tracking Number'] = tracking_number if tracking_number else None
        result['Fulfillment: Shipment Status'] = shipment_status if shipment_status else None
        
        return result
    
    def _create_generic_line_item(self, row: pd.Series, order_name: str, customer_email: str, processed_at: str) -> Dict[str, Any]:
        """Create a generic line item when no specific line item data exists."""
        
        # Try to extract any available product information
        note = str(row.get('Note', '')) if pd.notna(row.get('Note')) else ''
        
        # Try to extract product info from notes or other fields
        product_title = self._extract_product_from_note(note) or 'Unknown Product'
        product_handle = self._create_handle(product_title)
        
        # Use transaction amount as line total
        transaction_amount = self._safe_float(row.get('Transaction: Amount', 0))
        
        # Create the full row with all 125 columns - initialize as None (completely empty)
        result = {}
        for col in self.shopify_columns:
            result[col] = None
        
        # Helper function to only set values if they exist in original data
        def set_if_exists(key, original_key=None, default=None, transform_func=None):
            lookup_key = original_key or key
            if lookup_key in row.index and pd.notna(row[lookup_key]):
                value = row[lookup_key]
                if transform_func:
                    value = transform_func(value)
                result[key] = value
            elif default is not None:
                result[key] = default
        
        # Populate ONLY required fields and fields that exist in original data
        result['Name'] = order_name
        result['Command'] = 'NEW'
        result['Line: Type'] = 'Line Item'
        result['Line: Command'] = 'DEFAULT'
        
        # Only set if exists in original
        result['Email'] = customer_email
        result['Customer: Email'] = customer_email
        result['Note'] = note if note else None
        result['Processed At'] = processed_at if processed_at else None
        
        # Line item fields
        result['Line: Product Handle'] = product_handle
        result['Line: Title'] = product_title
        result['Line: Name'] = product_title
        result['Line: Quantity'] = 1
        result['Line: Price'] = transaction_amount
        
        # Transaction fields
        result['Transaction: Kind'] = 'sale'
        result['Transaction: Processed At'] = processed_at if processed_at else None
        result['Transaction: Amount'] = transaction_amount
        result['Transaction: Status'] = 'success'
        
        # Fulfillment fields - only if not default unfulfilled
        result['Fulfillment: Status'] = None  # Leave empty instead of 'unfulfilled'
        
        return result
    
    def _format_date(self, date_value: Any) -> str:
        """Format date value to Shopify-compatible format."""
        if pd.isna(date_value) or str(date_value).strip() == '':
            return ''
        
        try:
            # Handle different date formats
            date_str = str(date_value).strip()
            
            # Try parsing common formats
            date_formats = [
                '%Y-%m-%d %H:%M:%S %z',  # With timezone
                '%Y-%m-%d %H:%M:%S',     # Without timezone
                '%Y-%m-%d',              # Date only
                '%m/%d/%Y %H:%M:%S',     # US format with time
                '%m/%d/%Y',              # US format date only
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            
            # If all parsing fails, return the original string
            return date_str
            
        except Exception:
            return ''
    
    def _create_handle(self, title: str) -> str:
        """Create a URL-friendly handle from product title."""
        if not title or pd.isna(title):
            return 'unknown-product'
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        handle = re.sub(r'[^\w\s-]', '', str(title)).strip().lower()
        handle = re.sub(r'[-\s]+', '-', handle)
        
        # Remove leading/trailing hyphens
        handle = handle.strip('-')
        
        return handle if handle else 'unknown-product'
    
    def _extract_product_from_note(self, note: str) -> Optional[str]:
        """Try to extract product information from order notes."""
        if not note or pd.isna(note):
            return None
        
        # Look for patterns like "Stock levels reduced: [Product Name]"
        patterns = [
            r'Stock levels reduced:\s*([^,\n]+)',
            r'Product:\s*([^,\n]+)',
            r'Item:\s*([^,\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, note, re.IGNORECASE)
            if match:
                product_name = match.group(1).strip()
                # Clean up the product name
                product_name = re.sub(r'\s*\d+→\d+\s*$', '', product_name)  # Remove stock numbers
                return product_name
        
        return None
    
    def _determine_fulfillment_status(self, row: pd.Series) -> str:
        """Determine fulfillment status from available data."""
        # Check for explicit fulfillment status
        if pd.notna(row.get('Fulfillment: Status')):
            return str(row.get('Fulfillment: Status')).lower()
        
        # Check tracking number
        if pd.notna(row.get('Fulfillment: Tracking Number')) and str(row.get('Fulfillment: Tracking Number')).strip():
            return 'success'
        
        # Check if order is closed/completed (common WooCommerce pattern)
        if pd.notna(row.get('Closed At')) and str(row.get('Closed At')).strip():
            return 'success'
        
        # Check order notes for completion indicators
        note = str(row.get('Note', '')) if pd.notna(row.get('Note')) else ''
        if 'completed' in note.lower() or 'shipped' in note.lower():
            return 'success'
        
        return 'unfulfilled'
    
    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float."""
        if pd.isna(value) or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_float_to_int(self, value: Any) -> int:
        """Safely convert value to int via float."""
        return int(self._safe_float(value))
    
    def _safe_bool(self, value: Any) -> bool:
        """Safely convert value to boolean."""
        if pd.isna(value):
            return True  # Default to True for shipping requirements
        
        if isinstance(value, bool):
            return value
        
        str_value = str(value).lower().strip()
        return str_value not in ['false', '0', 'no', 'n', '']
    
    def _validate_and_clean_phone_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean phone numbers in the dataframe.
        
        For US numbers (starting with +1), ensure they are exactly 11 digits after the +.
        If invalid, move to Note column and clear the original field.
        Only add invalid phone notes to the first row for each unique Name identifier.
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with cleaned phone numbers and updated notes
        """
        df_copy = df.copy()
        
        # Phone columns to check
        phone_columns = ['Customer: Phone', 'Billing: Phone', 'Shipping: Phone']
        
        # Ensure Note column exists
        if 'Note' not in df_copy.columns:
            df_copy['Note'] = ''
        
        # Initialize phone validation warnings if not already set
        if not hasattr(self, 'phone_validation_warnings'):
            self.phone_validation_warnings = []
        
        # Track which Name identifiers have already had invalid phone notes added
        names_with_notes = set()
        
        for idx, row in df_copy.iterrows():
            invalid_phones = []
            cleaned_phones = []
            order_name = str(row.get('Name', ''))
            
            for phone_col in phone_columns:
                if phone_col in df_copy.columns and pd.notna(row[phone_col]):
                    phone = str(row[phone_col]).strip()
                    
                    if phone and phone.startswith('+1'):
                        # Clean the phone number - remove all non-digit characters except the +
                        cleaned_phone = '+' + re.sub(r'[^\d]', '', phone)
                        
                        # Check if it has exactly 11 digits after the +
                        if len(cleaned_phone) == 12:  # +1 + 10 digits = 12 characters total
                            # Valid phone - update with cleaned version
                            if phone != cleaned_phone:
                                cleaned_phones.append(f"Row {idx+1} {phone_col}: '{phone}' → '{cleaned_phone}'")
                            df_copy.at[idx, phone_col] = cleaned_phone
                        else:
                            # Invalid phone - clear field and potentially add to notes
                            invalid_phones.append(f"Customer phone {phone} was removed from phone fields because it is invalid")
                            df_copy.at[idx, phone_col] = ''
            
            # Add invalid phone notes ONLY to the first row for each unique Name identifier
            if invalid_phones and order_name and order_name not in names_with_notes:
                existing_note = str(row.get('Note', '')) if pd.notna(row.get('Note')) else ''
                if existing_note:
                    existing_note += '\n================\n'
                new_notes = '\n================\n'.join(invalid_phones)
                df_copy.at[idx, 'Note'] = existing_note + new_notes
                
                # Mark this Name identifier as having notes added
                names_with_notes.add(order_name)
            
            # Track cleaned phones for warnings
            if cleaned_phones:
                self.phone_validation_warnings.extend(cleaned_phones)
        
        return df_copy
    
    def _get_customer_email(self, row: pd.Series) -> str:
        """
        Get customer email from primary or fallback columns.
        
        Args:
            row: DataFrame row
            
        Returns:
            Customer email string (empty if none found)
        """
        # Primary email column
        primary_email = row.get('Customer: Email', '')
        if pd.notna(primary_email) and str(primary_email).strip():
            return str(primary_email).strip()
        
        # Fallback email columns (in order of preference)
        fallback_columns = [
            'Metafield: woo._ppcp_paypal_payer_email',
            'Metafield: woo._ppcp_paypal_billing_email', 
            'Metafield: woo.Payer PayPal address'
        ]
        
        for col in fallback_columns:
            if col in row.index and pd.notna(row.get(col)) and str(row.get(col)).strip():
                email = str(row.get(col)).strip()
                # Basic email validation - must contain @ and .
                if '@' in email and '.' in email:
                    return email
        
        # Return empty string if no valid email found
        return ''
    
    def _handle_email_fallbacks(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle email fallbacks when Customer: Email is missing.
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with email fallbacks applied and warnings tracked
        """
        df_copy = df.copy()
        
        # Initialize email fallback warnings if not already set
        if not hasattr(self, 'email_fallback_warnings'):
            self.email_fallback_warnings = []
        
        # Ensure Customer: Email column exists and is object type
        if 'Customer: Email' not in df_copy.columns:
            df_copy['Customer: Email'] = ''
        
        # Ensure Customer: Email is object type to prevent dtype issues
        df_copy['Customer: Email'] = df_copy['Customer: Email'].astype('object')
        
        for idx, row in df_copy.iterrows():
            # Check if Customer: Email is missing or empty
            primary_email = row.get('Customer: Email', '')
            if pd.isna(primary_email) or str(primary_email).strip() == '':
                
                # Look for fallback email
                fallback_email = self._get_customer_email(row)
                if fallback_email:
                    # Find which column provided the fallback email
                    fallback_columns = [
                        'Metafield: woo._ppcp_paypal_payer_email',
                        'Metafield: woo._ppcp_paypal_billing_email', 
                        'Metafield: woo.Payer PayPal address'
                    ]
                    
                    source_column = ''
                    for col in fallback_columns:
                        if (col in row.index and pd.notna(row.get(col)) and 
                            str(row.get(col)).strip() == fallback_email):
                            source_column = col
                            break
                    
                    # Update the Customer: Email column
                    df_copy.at[idx, 'Customer: Email'] = fallback_email
                    
                    # Track the fallback for warnings
                    order_name = row.get('Name', f'Row {idx+1}')
                    self.email_fallback_warnings.append(
                        f"Row {idx+1} Order {order_name}: Used email from '{source_column}' → '{fallback_email}'"
                    )
        
        return df_copy
    
    def _fix_dataframe_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix dataframe column types for Streamlit/PyArrow compatibility.
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with proper column types
        """
        df_copy = df.copy()
        
        # Ensure email columns are always string/object type first
        email_columns = [col for col in df_copy.columns if 'Email' in col]
        for col in email_columns:
            df_copy[col] = df_copy[col].astype('object')
        
        # Numeric columns should be float64 - be very specific about which columns
        numeric_keywords = ['Price', 'Amount', 'Total', 'Rate', 'Grams', 'Weight', 'Discount', 'Quantity']
        numeric_columns = []
        for col in df_copy.columns:
            # Only convert columns that end with or exactly match numeric keywords
            # This prevents false positives like "Line: Fulfillment Service"
            if any(col.endswith(': ' + keyword) or col == keyword for keyword in numeric_keywords):
                # Exclude email columns from numeric conversion
                if 'Email' not in col:
                    numeric_columns.append(col)
        
        # Convert numeric columns to float, but preserve None values (don't fill with 0.0)
        for col in numeric_columns:
            df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
        
        # Boolean columns should be bool - be very specific to avoid false positives
        # Exclude problematic columns like 'Top Row' that shouldn't be boolean
        boolean_keywords = ['Required', 'Included', 'Taxable', 'Gift Card', 'Send Receipt', 'Restock', 'Test']
        boolean_columns = []
        for col in df_copy.columns:
            # Only convert columns that end with boolean keywords or exactly match
            # Exclude 'Top Row' and other non-boolean columns
            if col in ['Top Row', 'Row #']:
                continue  # Skip these columns - they're not boolean
            if any(col.endswith(': ' + keyword) or col == keyword for keyword in boolean_keywords):
                boolean_columns.append(col)
        
        # Convert boolean columns, but preserve None values
        for col in boolean_columns:
            if col in df_copy.columns:
                # Convert to string first, then map to boolean values
                df_copy[col] = df_copy[col].astype(str)
                # Map common boolean representations
                boolean_map = {
                    'true': True, 'false': False, 'True': True, 'False': False,
                    '1': True, '0': False, 'yes': True, 'no': False,
                    'nan': None, 'None': None
                }
                # Apply mapping and use infer_objects to avoid downcasting warning
                df_copy[col] = df_copy[col].map(boolean_map)
                df_copy[col] = df_copy[col].infer_objects(copy=False)
        
        # ID columns should be string (to handle large numbers)
        id_columns = []
        for col in df_copy.columns:
            if 'ID' in col:
                id_columns.append(col)
        
        for col in id_columns:
            df_copy[col] = df_copy[col].astype(str)
        
        return df_copy


def create_sample_order_csv() -> str:
    """Create a sample CSV for testing order transformation."""
    sample_data = {
        'Name': ['1001', '1002'],
        'Customer: Email': ['customer1@example.com', 'customer2@example.com'],
        'Processed At': ['2024-01-15 10:30:00', '2024-01-16 14:20:00'],
        'Line: Title': ['Trading Card Booster Pack', 'Limited Edition Card Set'],
        'Line: SKU': ['TCP-001', 'LEC-002'],
        'Line: Quantity': [2, 1],
        'Line: Price': [19.99, 49.99],
        'Line: Total': [39.98, 49.99],
        'Transaction: Amount': [39.98, 49.99],
        'Fulfillment: Status': ['success', 'unfulfilled'],
        'Fulfillment: Tracking Number': ['1Z999AA1234567890', ''],
    }
    
    df = pd.DataFrame(sample_data)
    filename = f'sample_orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(filename, index=False)
    return filename