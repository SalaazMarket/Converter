import streamlit as st
import pandas as pd
import json
import io
import base64
from typing import Dict, List, Any, Optional, Tuple
import re
import os

# Page configuration
st.set_page_config(
    page_title="Salaaz CSV Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SalaazConverter:
    """
    Main converter class for transforming e-commerce CSV/Excel files 
    to Salaaz marketplace bulk upload format.
    """
    
    def __init__(self):
        self.SALAAZ_REQUIRED_COLUMNS = [
            'name', 'description', 'price', 'brand', 'category_id'
        ]
        
        self.SALAAZ_OPTIONAL_COLUMNS = [
            'sub_category_id', 'sub_sub_category_id', 'certification',
            'country_of_origin', 'details', 'care', 'size_fit',
            'variant_attributes', 'variant_quantity', 'image_urls'
        ]
        
        self.ALL_SALAAZ_COLUMNS = self.SALAAZ_REQUIRED_COLUMNS + self.SALAAZ_OPTIONAL_COLUMNS
        
        # Load category mappings
        self.categories_df = None
        self.sub_categories_df = None
        self.sub_sub_categories_df = None
        self._load_category_mappings()
        
        # Common e-commerce platform mappings
        self.PLATFORM_MAPPINGS = {
            'shopify': {
                'name': ['Title', 'Product Title', 'title'],
                'description': ['Body (HTML)', 'Description', 'body_html'],
                'price': ['Variant Price', 'Price', 'price'],
                'brand': ['Vendor', 'Brand', 'vendor'],
                'variant_attributes': ['Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value'],
                'variant_quantity': ['Variant Inventory Qty', 'Inventory Quantity', 'inventory_quantity'],
                'image_urls': ['Image Src', 'Image URL', 'image_src'],
                'category_source': ['Product Category', 'Type', 'Tags', 'Category']
            },
            'amazon': {
                'name': ['Product Name', 'Title', 'item-name'],
                'description': ['Product Description', 'Description', 'product-description'],
                'price': ['Price', 'Standard Price', 'standard-price'],
                'brand': ['Brand Name', 'Brand', 'brand-name'],
                'variant_attributes': ['Color', 'Size', 'Style'],
                'variant_quantity': ['Quantity', 'Stock Quantity', 'quantity'],
                'image_urls': ['Main Image URL', 'Image URL', 'main-image-url'],
                'category_source': ['Category', 'Product Type', 'Department']
            },
            'woocommerce': {
                'name': ['Name', 'Product Name', 'post_title'],
                'description': ['Description', 'Product Description', 'post_content'],
                'price': ['Regular Price', 'Price', 'regular_price'],
                'brand': ['Brand', 'Manufacturer', 'brand'],
                'variant_attributes': ['Attribute 1 name', 'Attribute 1 value(s)'],
                'variant_quantity': ['Stock', 'Stock Quantity', 'stock'],
                'image_urls': ['Images', 'Gallery Images', 'images'],
                'category_source': ['Categories', 'Product categories', 'Category']
            }
        }
    
    def detect_platform(self, columns: List[str]) -> Optional[str]:
        """Detect the e-commerce platform based on column names."""
        column_set = set([col.lower() for col in columns])
        
        scores = {}
        for platform, mappings in self.PLATFORM_MAPPINGS.items():
            score = 0
            total_possible = 0
            
            for salaaz_field, possible_columns in mappings.items():
                total_possible += 1
                for possible_col in possible_columns:
                    if possible_col.lower() in column_set:
                        score += 1
                        break
            
            scores[platform] = score / total_possible if total_possible > 0 else 0
        
        # Return platform with highest score if above threshold
        best_platform = max(scores.items(), key=lambda x: x[1])
        return best_platform[0] if best_platform[1] > 0.3 else None
    
    def suggest_mapping(self, source_columns: List[str], platform: Optional[str] = None) -> Dict[str, str]:
        """Suggest column mapping from source to Salaaz format."""
        mapping = {}
        source_lower = [col.lower() for col in source_columns]
        
        # Use platform-specific mappings if detected
        if platform and platform in self.PLATFORM_MAPPINGS:
            platform_mappings = self.PLATFORM_MAPPINGS[platform]
            
            for salaaz_field, possible_columns in platform_mappings.items():
                for possible_col in possible_columns:
                    if possible_col.lower() in source_lower:
                        original_col = source_columns[source_lower.index(possible_col.lower())]
                        mapping[salaaz_field] = original_col
                        break
        
        # Fallback to fuzzy matching for unmapped fields
        for salaaz_field in self.ALL_SALAAZ_COLUMNS:
            if salaaz_field not in mapping:
                best_match = self._fuzzy_match_column(salaaz_field, source_columns)
                if best_match:
                    mapping[salaaz_field] = best_match
        
        return mapping
    
    def _fuzzy_match_column(self, target: str, source_columns: List[str]) -> Optional[str]:
        """Find the best fuzzy match for a column name."""
        target_lower = target.lower()
        
        # Exact match
        for col in source_columns:
            if col.lower() == target_lower:
                return col
        
        # Partial match
        for col in source_columns:
            if target_lower in col.lower() or col.lower() in target_lower:
                return col
        
        # Keyword matching
        keywords = {
            'name': ['title', 'name', 'product'],
            'description': ['description', 'body', 'content', 'details'],
            'price': ['price', 'cost', 'amount'],
            'brand': ['brand', 'vendor', 'manufacturer'],
            'category_id': ['category', 'type', 'classification'],
            'variant_quantity': ['quantity', 'stock', 'inventory', 'qty'],
            'image_urls': ['image', 'photo', 'picture', 'url'],
            'category_source': ['category', 'type', 'tags', 'classification', 'department']
        }
        
        if target in keywords:
            for keyword in keywords[target]:
                for col in source_columns:
                    if keyword in col.lower():
                        return col
        
        return None
    
    def _load_category_mappings(self):
        """Load category mapping CSV files."""
        try:
            # Load main categories
            if os.path.exists('categories.csv'):
                self.categories_df = pd.read_csv('categories.csv', header=None,
                                               names=['id', 'name', 'description', 'active', 'created_at', 'updated_at'])
            
            # Load sub-categories
            if os.path.exists('sub_categories.csv'):
                self.sub_categories_df = pd.read_csv('sub_categories.csv', header=None,
                                                   names=['id', 'name', 'description', 'active', 'created_at', 'updated_at', 'category_id'])
            
            # Load sub-sub-categories
            if os.path.exists('sub_sub_categories.csv'):
                self.sub_sub_categories_df = pd.read_csv('sub_sub_categories.csv', header=None,
                                                       names=['id', 'name', 'description', 'active', 'created_at', 'updated_at', 'sub_category_id'])
        except Exception as e:
            st.warning(f"Could not load category mapping files: {str(e)}")
    
    def parse_shopify_category(self, category_string: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse Shopify nested category string into individual category levels.
        
        Args:
            category_string: String like "Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing"
            
        Returns:
            Tuple of (category, sub_category, sub_sub_category) names
        """
        if not category_string or pd.isna(category_string):
            return None, None, None
        
        # Split by " > " separator
        parts = [part.strip() for part in str(category_string).split(' > ')]
        
        # Return up to 3 levels
        category = parts[0] if len(parts) > 0 else None
        sub_category = parts[1] if len(parts) > 1 else None
        sub_sub_category = parts[2] if len(parts) > 2 else None
        
        return category, sub_category, sub_sub_category
    
    def find_category_ids(self, category_name: str, sub_category_name: Optional[str] = None,
                         sub_sub_category_name: Optional[str] = None) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Find category IDs based on category names using fuzzy matching.
        
        Args:
            category_name: Main category name
            sub_category_name: Sub-category name (optional)
            sub_sub_category_name: Sub-sub-category name (optional)
            
        Returns:
            Tuple of (category_id, sub_category_id, sub_sub_category_id)
        """
        category_id = None
        sub_category_id = None
        sub_sub_category_id = None
        
        # Find main category
        if category_name and self.categories_df is not None:
            category_id = self._find_best_match(category_name, self.categories_df, 'name', 'id')
        
        # Find sub-category
        if sub_category_name and self.sub_categories_df is not None:
            # Filter by parent category if found
            if category_id:
                filtered_df = self.sub_categories_df[self.sub_categories_df['category_id'] == category_id]
            else:
                filtered_df = self.sub_categories_df
            
            sub_category_id = self._find_best_match(sub_category_name, filtered_df, 'name', 'id')
        
        # Find sub-sub-category
        if sub_sub_category_name and self.sub_sub_categories_df is not None:
            # Filter by parent sub-category if found
            if sub_category_id:
                filtered_df = self.sub_sub_categories_df[self.sub_sub_categories_df['sub_category_id'] == sub_category_id]
            else:
                filtered_df = self.sub_sub_categories_df
            
            sub_sub_category_id = self._find_best_match(sub_sub_category_name, filtered_df, 'name', 'id')
        
        return category_id, sub_category_id, sub_sub_category_id
    
    def _find_best_match(self, search_term: str, df: pd.DataFrame, search_column: str, return_column: str) -> Optional[int]:
        """
        Find the best matching category using fuzzy string matching.
        
        Args:
            search_term: Term to search for
            df: DataFrame to search in
            search_column: Column to search in
            return_column: Column to return value from
            
        Returns:
            Best matching ID or None
        """
        if df.empty or not search_term:
            return None
        
        search_term_lower = search_term.lower().strip()
        
        # Exact match first
        exact_matches = df[df[search_column].str.lower() == search_term_lower]
        if not exact_matches.empty:
            return int(exact_matches.iloc[0][return_column])
        
        # Partial match - search term contains category name
        for _, row in df.iterrows():
            category_name = str(row[search_column]).lower().strip()
            if category_name in search_term_lower or search_term_lower in category_name:
                return int(row[return_column])
        
        # Keyword matching for common mappings
        keyword_mappings = {
            'apparel': ['clothing', 'clothes'],
            'clothing': ['apparel', 'clothes', 'fashion'],
            'accessories': ['jewelry', 'jewellery', 'watches'],
            'traditional': ['ceremonial', 'cultural'],
            'health': ['beauty', 'wellness'],
            'home': ['house', 'living', 'decor'],
            'electronics': ['tech', 'digital'],
            'books': ['literature', 'reading']
        }
        
        # Check if search term matches any keywords
        for _, row in df.iterrows():
            category_name = str(row[search_column]).lower().strip()
            
            # Direct keyword matching
            for keyword, synonyms in keyword_mappings.items():
                if keyword in search_term_lower:
                    if any(synonym in category_name for synonym in synonyms + [keyword]):
                        return int(row[return_column])
                
                if keyword in category_name:
                    if any(synonym in search_term_lower for synonym in synonyms + [keyword]):
                        return int(row[return_column])
        
        return None
    
    def map_shopify_categories(self, df: pd.DataFrame, category_column: str) -> pd.DataFrame:
        """
        Map Shopify category strings to Salaaz category IDs.
        
        Args:
            df: DataFrame containing Shopify data
            category_column: Name of the column containing category information
            
        Returns:
            DataFrame with additional columns for category IDs
        """
        result_df = df.copy()
        
        # Initialize category ID columns
        result_df['category_id'] = None
        result_df['sub_category_id'] = None
        result_df['sub_sub_category_id'] = None
        
        if category_column not in df.columns:
            st.warning(f"Category column '{category_column}' not found. Using default category ID.")
            result_df['category_id'] = 1  # Default category
            return result_df
        
        # Process each row
        for idx, row in df.iterrows():
            category_string = row[category_column]
            
            # Parse nested category
            category, sub_category, sub_sub_category = self.parse_shopify_category(category_string)
            
            # Find matching IDs
            category_id, sub_category_id, sub_sub_category_id = self.find_category_ids(
                category, sub_category, sub_sub_category
            )
            
            # Set the IDs
            result_df.at[idx, 'category_id'] = category_id if category_id else 1  # Default to category 1
            result_df.at[idx, 'sub_category_id'] = sub_category_id if sub_category_id else 1
            result_df.at[idx, 'sub_sub_category_id'] = sub_sub_category_id if sub_sub_category_id else 1
        
        return result_df
    
    def transform_data(self, df: pd.DataFrame, mapping: Dict[str, str], platform: Optional[str] = None) -> pd.DataFrame:
        """Transform source data to Salaaz format using the provided mapping."""
        result_data = {}
        
        # Initialize all Salaaz columns
        for col in self.ALL_SALAAZ_COLUMNS:
            result_data[col] = [None] * len(df)
        
        # Map the data
        for salaaz_col, source_col in mapping.items():
            if source_col and source_col in df.columns:
                result_data[salaaz_col] = df[source_col].tolist()
        
        # Create result DataFrame
        result_df = pd.DataFrame(result_data)
        
        # Handle category mapping for supported platforms
        if platform and platform in self.PLATFORM_MAPPINGS:
            category_source_candidates = self.PLATFORM_MAPPINGS[platform].get('category_source', [])
            category_source_col = None
            
            # Find the first available category source column
            for candidate in category_source_candidates:
                if candidate in df.columns:
                    category_source_col = candidate
                    break
            
            # Apply category mapping if we found a category source column
            if category_source_col:
                try:
                    mapped_df = self.map_shopify_categories(df, category_source_col)
                    # Update result_df with category IDs
                    if 'category_id' in mapped_df.columns:
                        result_df['category_id'] = mapped_df['category_id']
                    if 'sub_category_id' in mapped_df.columns:
                        result_df['sub_category_id'] = mapped_df['sub_category_id']
                    if 'sub_sub_category_id' in mapped_df.columns:
                        result_df['sub_sub_category_id'] = mapped_df['sub_sub_category_id']
                except Exception as e:
                    st.warning(f"Category mapping failed: {str(e)}. Using default category.")
        
        # Post-processing
        result_df = self._post_process_data(result_df, df, mapping)
        
        return result_df
    
    def _post_process_data(self, result_df: pd.DataFrame, source_df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """Post-process the transformed data for Salaaz compatibility."""
        
        # Clean and validate price column
        if 'price' in result_df.columns:
            result_df['price'] = result_df['price'].apply(self._clean_price)
        
        # Handle variant attributes
        result_df = self._process_variant_attributes(result_df, source_df, mapping)
        
        # Clean image URLs
        if 'image_urls' in result_df.columns:
            result_df['image_urls'] = result_df['image_urls'].apply(self._clean_image_urls)
        
        # Set default values for required fields
        result_df = self._set_default_values(result_df)
        
        # Remove rows with missing name or description (required fields)
        if 'name' in result_df.columns and 'description' in result_df.columns:
            # Filter out rows where name or description is missing/empty
            result_df = result_df[
                (result_df['name'].notna()) &
                (result_df['name'].astype(str).str.strip() != '') &
                (result_df['description'].notna()) &
                (result_df['description'].astype(str).str.strip() != '')
            ]
        
        # Remove completely empty rows
        result_df = result_df.dropna(how='all')
        
        return result_df
    
    def _clean_price(self, price_value) -> Optional[str]:
        """Clean and validate price values."""
        if pd.isna(price_value):
            return None
        
        # Remove currency symbols and extra whitespace
        price_str = str(price_value).strip()
        price_str = re.sub(r'[^\d.,]', '', price_str)
        
        # Handle different decimal separators
        if ',' in price_str and '.' in price_str:
            # Assume comma is thousands separator
            price_str = price_str.replace(',', '')
        elif ',' in price_str:
            # Assume comma is decimal separator
            price_str = price_str.replace(',', '.')
        
        try:
            return str(float(price_str))
        except (ValueError, TypeError):
            return None
    
    def _process_variant_attributes(self, result_df: pd.DataFrame, source_df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """Process variant attributes into JSON format."""
        
        # Look for common variant attribute columns in source data
        variant_columns = []
        for col in source_df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['color', 'size', 'style', 'option', 'variant', 'attribute']):
                variant_columns.append(col)
        
        if variant_columns:
            variant_attrs = []
            for idx, row in source_df.iterrows():
                attrs = {}
                for col in variant_columns:
                    value = row[col]
                    if pd.notna(value) and str(value).strip():
                        # Create a clean attribute name
                        attr_name = col.lower().replace(' ', '_')
                        attr_name = re.sub(r'[^\w]', '', attr_name)
                        attrs[attr_name] = str(value).strip()
                
                variant_attrs.append(json.dumps(attrs) if attrs else None)
            
            result_df['variant_attributes'] = variant_attrs
        
        return result_df
    
    def _clean_image_urls(self, image_value) -> Optional[str]:
        """Clean and format image URLs."""
        if pd.isna(image_value):
            return None
        
        image_str = str(image_value).strip()
        if not image_str:
            return None
        
        # Split multiple URLs by common separators
        urls = re.split(r'[;,\|\n]', image_str)
        
        # Clean and validate URLs
        clean_urls = []
        for url in urls:
            url = url.strip()
            if url and (url.startswith('http') or url.startswith('https')):
                clean_urls.append(url)
        
        return ','.join(clean_urls) if clean_urls else None
    
    def _set_default_values(self, result_df: pd.DataFrame) -> pd.DataFrame:
        """Set default values for required fields when missing."""
        
        # Set default category_id if missing (you may want to customize this)
        if 'category_id' in result_df.columns:
            result_df['category_id'] = result_df['category_id'].fillna('1')  # Default category
        
        # Set default variant quantity
        if 'variant_quantity' in result_df.columns:
            result_df['variant_quantity'] = result_df['variant_quantity'].fillna('0')
        
        return result_df
    
    def validate_salaaz_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the converted data against Salaaz requirements."""
        issues = []
        warnings = []
        
        # Check required columns
        for col in self.SALAAZ_REQUIRED_COLUMNS:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
            else:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    issues.append(f"Column '{col}' has {missing_count} missing values")
        
        # Validate data types and formats
        if 'price' in df.columns:
            invalid_prices = 0
            for price in df['price'].dropna():
                try:
                    float(price)
                except (ValueError, TypeError):
                    invalid_prices += 1
            if invalid_prices > 0:
                warnings.append(f"{invalid_prices} rows have invalid price format")
        
        if 'category_id' in df.columns:
            invalid_categories = 0
            for cat_id in df['category_id'].dropna():
                try:
                    int(cat_id)
                except (ValueError, TypeError):
                    invalid_categories += 1
            if invalid_categories > 0:
                warnings.append(f"{invalid_categories} rows have invalid category_id format")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_rows': len(df),
            'complete_rows': len(df.dropna(subset=self.SALAAZ_REQUIRED_COLUMNS))
        }


def main():
    """Main Streamlit application."""
    
    st.title("🔄 Salaaz CSV Converter")
    st.markdown("Convert your e-commerce CSV/Excel files to Salaaz marketplace bulk upload format")
    
    # Initialize converter
    converter = SalaazConverter()
    
    # Sidebar for instructions and platform info
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Upload** your CSV or Excel file
        2. **Review** detected mappings
        3. **Adjust** mappings if needed
        4. **Preview** converted data
        5. **Download** Salaaz format file
        """)
        
        st.header("🏪 Supported Platforms")
        st.markdown("""
        - **Shopify** - Product exports
        - **Amazon** - Inventory files  
        - **WooCommerce** - Product exports
        - **Custom** - Any CSV/Excel format
        """)
        
        st.header("📊 Salaaz Format")
        with st.expander("Required Fields"):
            for field in converter.SALAAZ_REQUIRED_COLUMNS:
                st.code(field)
        
        with st.expander("Optional Fields"):
            for field in converter.SALAAZ_OPTIONAL_COLUMNS:
                st.code(field)
        
        st.header("🚀 Next Steps")
        if st.button("📋 View Upload Instructions", use_container_width=True):
            st.session_state.show_next_steps = True
        
        # Next Steps Modal
        if st.session_state.get('show_next_steps', False):
            with st.container():
                st.markdown("### 📤 After Converting Your File")
                st.markdown("""
                **Follow these steps to upload your products to Salaaz:**
                
                1. **Visit the Vendor Portal**
                   Go to [vendor.salaaz.com](https://vendor.salaaz.com) and log into your account
                
                2. **Select Bulk Upload**
                   Navigate to the product bulk upload option in your dashboard
                
                3. **Upload Your File**
                   Use the CSV or Excel file generated by this converter
                
                4. **Edit Products**
                   The products will be editable in the Salaaz platform after upload
                
                **Note:** This converter is designed to format your data correctly for the Salaaz platform.
                """)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✅ Got it!", key="close_modal"):
                        st.session_state.show_next_steps = False
                        st.rerun()
                with col2:
                    if st.button("🔗 Open Vendor Portal", key="open_portal"):
                        st.markdown('[Open vendor.salaaz.com](https://vendor.salaaz.com)')
    
    # File upload
    st.header("📁 Step 1: Upload Your File")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your product data file from Shopify, Amazon, or any e-commerce platform"
    )
    
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
            
            # Display file preview
            with st.expander("📊 File Preview", expanded=True):
                st.dataframe(df.head(10))
            
            # Detect platform
            detected_platform = converter.detect_platform(df.columns.tolist())
            if detected_platform:
                st.info(f"🎯 Detected platform: **{detected_platform.title()}**")
            else:
                st.warning("🤔 Could not auto-detect platform. Manual mapping required.")
            
            # Column mapping section
            st.header("🗺️ Step 2: Column Mapping")
            
            # Get suggested mapping
            suggested_mapping = converter.suggest_mapping(df.columns.tolist(), detected_platform)
            
            # Create mapping interface
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Salaaz Fields")
            with col2:
                st.subheader("Your File Columns")
            
            # Initialize session state for mapping
            if 'column_mapping' not in st.session_state:
                st.session_state.column_mapping = suggested_mapping
            
            mapping = {}
            
            # Required fields mapping
            st.markdown("### ⚡ Required Fields")
            for salaaz_field in converter.SALAAZ_REQUIRED_COLUMNS:
                col1, col2 = st.columns(2)
                with col1:
                    st.code(salaaz_field)
                with col2:
                    current_mapping = st.session_state.column_mapping.get(salaaz_field, "")
                    options = [""] + df.columns.tolist()
                    
                    try:
                        default_index = options.index(current_mapping) if current_mapping in options else 0
                    except ValueError:
                        default_index = 0
                    
                    selected = st.selectbox(
                        f"Map to:",
                        options,
                        index=default_index,
                        key=f"mapping_{salaaz_field}"
                    )
                    if selected:
                        mapping[salaaz_field] = selected
            
            # Optional fields mapping
            with st.expander("🔧 Optional Fields Mapping"):
                for salaaz_field in converter.SALAAZ_OPTIONAL_COLUMNS:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.code(salaaz_field)
                    with col2:
                        current_mapping = st.session_state.column_mapping.get(salaaz_field, "")
                        options = [""] + df.columns.tolist()
                        
                        try:
                            default_index = options.index(current_mapping) if current_mapping in options else 0
                        except ValueError:
                            default_index = 0
                        
                        selected = st.selectbox(
                            f"Map to:",
                            options,
                            index=default_index,
                            key=f"mapping_optional_{salaaz_field}"
                        )
                        if selected:
                            mapping[salaaz_field] = selected
            
            # Update session state
            st.session_state.column_mapping = mapping
            
            # Transform data
            if mapping:
                st.header("🔄 Step 3: Data Transformation")
                
                with st.spinner("Transforming data..."):
                    transformed_df = converter.transform_data(df, mapping, detected_platform)
                
                # Validate transformed data
                validation_result = converter.validate_salaaz_data(transformed_df)
                
                # Display validation results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", validation_result['total_rows'])
                with col2:
                    st.metric("Complete Rows", validation_result['complete_rows'])
                with col3:
                    valid_percentage = (validation_result['complete_rows'] / validation_result['total_rows']) * 100
                    st.metric("Valid %", f"{valid_percentage:.1f}%")
                
                # Show validation issues
                if validation_result['issues']:
                    st.error("❌ Validation Issues:")
                    for issue in validation_result['issues']:
                        st.write(f"• {issue}")
                
                if validation_result['warnings']:
                    st.warning("⚠️ Warnings:")
                    for warning in validation_result['warnings']:
                        st.write(f"• {warning}")
                
                if validation_result['valid']:
                    st.success("✅ Data validation passed!")
                
                # Preview transformed data
                st.header("👀 Step 4: Preview Converted Data")
                
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    show_all_columns = st.checkbox("Show all columns", value=False)
                with col2:
                    preview_rows = st.slider("Rows to preview", 5, 50, 10)
                
                if show_all_columns:
                    preview_df = transformed_df.head(preview_rows)
                else:
                    # Show only mapped columns
                    mapped_columns = [col for col in converter.ALL_SALAAZ_COLUMNS if col in mapping.keys()]
                    preview_df = transformed_df[mapped_columns].head(preview_rows)
                
                st.dataframe(preview_df)
                
                # Download section
                st.header("💾 Step 5: Download Converted File")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV download
                    csv_buffer = io.StringIO()
                    transformed_df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📄 Download as CSV",
                        data=csv_data,
                        file_name=f"salaaz_products_{uploaded_file.name.split('.')[0]}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Excel download
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        transformed_df.to_excel(writer, index=False, sheet_name='Products')
                    
                    st.download_button(
                        label="📊 Download as Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"salaaz_products_{uploaded_file.name.split('.')[0]}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # Statistics
                with st.expander("📈 Conversion Statistics"):
                    st.json({
                        "Original Columns": len(df.columns),
                        "Mapped Columns": len(mapping),
                        "Required Fields Mapped": len([k for k in mapping.keys() if k in converter.SALAAZ_REQUIRED_COLUMNS]),
                        "Optional Fields Mapped": len([k for k in mapping.keys() if k in converter.SALAAZ_OPTIONAL_COLUMNS]),
                        "Rows Processed": len(transformed_df),
                        "Platform Detected": detected_platform or "Unknown"
                    })
            
            else:
                st.warning("⚠️ Please map at least the required fields to proceed.")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Please ensure your file is a valid CSV or Excel format.")
    
    else:
        # Show example formats when no file is uploaded
        st.header("📝 Example File Formats")
        
        tab1, tab2, tab3 = st.tabs(["Shopify", "Amazon", "WooCommerce"])
        
        with tab1:
            st.subheader("Shopify Product Export Format")
            shopify_example = pd.DataFrame({
                'Title': ['Cotton T-Shirt', 'Denim Jeans'],
                'Body (HTML)': ['Comfortable cotton t-shirt', 'Classic denim jeans'],
                'Vendor': ['Fashion Brand', 'Denim Co'],
                'Variant Price': ['29.99', '79.99'],
                'Option1 Name': ['Color', 'Size'],
                'Option1 Value': ['Red', '32'],
                'Variant Inventory Qty': ['10', '5'],
                'Image Src': ['https://example.com/img1.jpg', 'https://example.com/img2.jpg']
            })
            st.dataframe(shopify_example)
        
        with tab2:
            st.subheader("Amazon Inventory Format")
            amazon_example = pd.DataFrame({
                'Product Name': ['Wireless Headphones', 'Phone Case'],
                'Product Description': ['High-quality wireless headphones', 'Protective phone case'],
                'Brand Name': ['Audio Tech', 'Case Pro'],
                'Standard Price': ['99.99', '19.99'],
                'Color': ['Black', 'Clear'],
                'Quantity': ['25', '100'],
                'Main Image URL': ['https://example.com/headphones.jpg', 'https://example.com/case.jpg']
            })
            st.dataframe(amazon_example)
        
        with tab3:
            st.subheader("WooCommerce Export Format")
            woo_example = pd.DataFrame({
                'Name': ['Yoga Mat', 'Water Bottle'],
                'Description': ['Non-slip yoga mat', 'Insulated water bottle'],
                'Regular Price': ['39.99', '24.99'],
                'Brand': ['Yoga Pro', 'Hydro'],
                'Stock': ['15', '50'],
                'Images': ['https://example.com/mat.jpg', 'https://example.com/bottle.jpg']
            })
            st.dataframe(woo_example)


if __name__ == "__main__":
    main()