# 🔄 Salaaz CSV Converter

A standalone Streamlit application for converting CSV/Excel files from various e-commerce platforms (Shopify, Amazon, WooCommerce, etc.) to the Salaaz marketplace bulk upload format.

## 🚀 Quick Start

### Option 1: Direct Launch (Recommended)
```bash
# Navigate to the converter directory
cd streamlit_converter

# Run the launch script (installs dependencies automatically)
python launch.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app.py
```

## 📋 Features

### ✨ Core Functionality
- **Multi-format Support**: CSV and Excel (.xlsx, .xls) files
- **Platform Detection**: Auto-detects Shopify, Amazon, and WooCommerce formats
- **Smart Mapping**: Intelligent column mapping with manual override options
- **Data Validation**: Comprehensive validation against Salaaz requirements
- **Preview & Download**: Preview converted data before downloading

### 🏪 Supported Platforms
- **Shopify**: Product export files
- **Amazon**: Inventory and product files
- **WooCommerce**: Product export files
- **Custom**: Any CSV/Excel format with manual mapping

### 📊 Salaaz Format Output

#### Required Fields
- `name` - Product name
- `description` - Product description
- `price` - Product price (decimal)
- `brand` - Product brand
- `category_id` - Category ID (integer)

#### Optional Fields
- `sub_category_id` - Sub-category ID (integer)
- `sub_sub_category_id` - Sub-sub-category ID (integer)
- `certification` - Product certification
- `country_of_origin` - Country where product was made
- `details` - Additional product details
- `care` - Care instructions
- `size_fit` - Size and fit information
- `variant_attributes` - JSON object with variant attributes
- `variant_quantity` - Available quantity for the variant
- `image_urls` - Comma-separated list of image URLs

## 🔧 How It Works

### 1. File Upload
- Upload your CSV or Excel file from any e-commerce platform
- Supports files up to 10MB in size
- Automatic format detection and validation

### 2. Platform Detection
The app automatically detects common e-commerce platforms based on column names:
- **Shopify**: Looks for columns like "Title", "Body (HTML)", "Vendor"
- **Amazon**: Identifies "Product Name", "Brand Name", "Standard Price"
- **WooCommerce**: Detects "Name", "Regular Price", "Description"

### 3. Column Mapping
- **Automatic Mapping**: Smart suggestions based on detected platform
- **Manual Override**: Adjust mappings for any column
- **Required Field Validation**: Ensures all mandatory Salaaz fields are mapped

### 4. Data Transformation
- **Price Cleaning**: Removes currency symbols and formats decimals
- **Variant Processing**: Converts attributes to JSON format
- **Image URL Handling**: Parses multiple URLs from various formats
- **Data Validation**: Comprehensive validation against Salaaz requirements

### 5. Export Options
- **CSV Format**: Standard comma-separated values
- **Excel Format**: Native Excel file with proper formatting
- **Validation Report**: Detailed feedback on data quality

## 📝 Usage Examples

### Shopify Product Export
```csv
Title,Body (HTML),Vendor,Variant Price,Option1 Name,Option1 Value,Variant Inventory Qty,Image Src
Cotton T-Shirt,Comfortable cotton t-shirt,Fashion Brand,29.99,Color,Red,10,https://example.com/img1.jpg
```

### Amazon Inventory File
```csv
Product Name,Product Description,Brand Name,Standard Price,Color,Quantity,Main Image URL
Wireless Headphones,High-quality wireless headphones,Audio Tech,99.99,Black,25,https://example.com/headphones.jpg
```

### Custom CSV Format
Any CSV with product data can be converted using manual column mapping.

## 🎯 Best Practices

### File Preparation
1. **Clean Data**: Remove empty rows and ensure consistent formatting
2. **Required Fields**: Ensure you have product name, description, price, and brand
3. **Category IDs**: Know your Salaaz category IDs or use default (category_id: 1)
4. **Image URLs**: Use direct HTTP/HTTPS URLs for product images

### Column Mapping Tips
1. **Review Suggestions**: Check auto-detected mappings before proceeding
2. **Required Fields First**: Focus on mapping all required fields correctly
3. **Variant Attributes**: Combine color, size, style fields into variant_attributes
4. **Image Handling**: Multiple image URLs can be comma-separated

### Data Quality
1. **Price Format**: Ensure prices are numeric (currency symbols will be removed)
2. **Variant Quantities**: Use integers for inventory quantities
3. **Image URLs**: Verify all image URLs are accessible
4. **Category Validation**: Use valid Salaaz category IDs

## 🏷️ Category Mapping

### Shopify Category Format
The converter now supports automatic mapping of Shopify nested categories to Salaaz category IDs. Shopify categories are typically formatted as nested hierarchies using the `>` separator:

```
"Apparel & Accessories > Clothing > Traditional & Ceremonial Clothing"
```

### How Category Mapping Works
1. **Automatic Detection**: The converter automatically detects category columns in Shopify exports
2. **Parsing**: Nested categories are split into main category, sub-category, and sub-sub-category levels
3. **Fuzzy Matching**: Each level is matched against your category CSV files using intelligent fuzzy matching
4. **ID Assignment**: Matching category IDs are automatically assigned to the appropriate Salaaz fields

### Category CSV Files Required
The converter requires three CSV files in the project directory:
- `categories.csv` - Main categories with IDs
- `sub_categories.csv` - Sub-categories linked to main categories
- `sub_sub_categories.csv` - Sub-sub-categories linked to sub-categories

### Supported Category Sources
The converter looks for category information in these Shopify columns (in order of preference):
- Product Category
- Type
- Tags
- Category

### Category Matching Features
- **Exact Match**: Direct name matching for precise categories
- **Partial Match**: Substring matching for related categories
- **Keyword Mapping**: Intelligent mapping using synonyms:
  - "Apparel" ↔ "Clothing"
  - "Accessories" ↔ "Jewelry"
  - "Health" ↔ "Beauty"
  - "Home" ↔ "Living"

### Example Category Mapping
```csv
Input: "Apparel & Accessories > Clothing > Men's Clothing"
Output:
- category_id: 175 (Clothing)
- sub_category_id: 869 (Men's Clothing)
- sub_sub_category_id: null
```

### Data Quality Requirements
- **Required Fields**: Products without name or description are automatically excluded from the output
- **Default Values**: Missing categories default to category_id: 1
- **Validation**: All category IDs are validated as integers

## ⚠️ Common Issues & Solutions

### File Upload Issues
- **File too large**: Compress or split files larger than 10MB
- **Format not supported**: Convert to CSV or Excel (.xlsx) format
- **Encoding problems**: Save CSV files with UTF-8 encoding

### Mapping Problems
- **Missing required fields**: Ensure all required Salaaz fields are mapped
- **Multiple candidates**: Choose the most relevant column for each mapping
- **No suitable columns**: Create default values or split your data

### Data Validation Errors
- **Invalid prices**: Check for non-numeric values in price columns
- **Missing data**: Review rows with incomplete information
- **Category IDs**: Ensure category IDs are valid integers

## 🔄 Integration with Salaaz

### Upload Process
1. Convert your data using this app
2. Download the Salaaz-formatted file
3. Log into your Salaaz vendor dashboard
4. Use the bulk upload feature with your converted file

### Category Management
- Contact Salaaz support for category ID mappings
- Use category_id: 1 as default for uncategorized products
- Plan your product categorization strategy

### Variant Handling
The converter transforms variant data into the JSON format expected by Salaaz:
```json
{
  "color": "Red",
  "size": "Large",
  "material": "Cotton"
}
```

## 🛠️ Technical Details

### Dependencies
- **Streamlit**: Web interface framework
- **Pandas**: Data manipulation and analysis
- **OpenPyXL**: Excel file handling
- **XLRD**: Legacy Excel file support

### Architecture
- **Standalone Application**: Completely separate from Django backend
- **No Database**: All processing in memory for security
- **Local Processing**: No data sent to external servers
- **Platform Agnostic**: Works on Windows, macOS, and Linux

### Performance
- **Batch Processing**: Handles large files efficiently
- **Memory Optimization**: Streaming data processing
- **Error Recovery**: Graceful handling of malformed data

## 📞 Support

### Getting Help
1. **Check Examples**: Review the built-in format examples
2. **Validation Messages**: Read error messages for specific guidance
3. **Documentation**: Refer to this README for detailed instructions

### Common Questions
- **Q**: What's the maximum file size?
  **A**: 10MB for optimal performance

- **Q**: Can I convert multiple files at once?
  **A**: Currently single file processing only

- **Q**: Are my files uploaded anywhere?
  **A**: No, all processing is local on your machine

- **Q**: What if my platform isn't supported?
  **A**: Use manual mapping - any CSV format can be converted

## 🔐 Security & Privacy

- **Local Processing**: All data processing happens on your local machine
- **No Data Storage**: Files are not saved or transmitted anywhere
- **No External Calls**: No internet connection required for processing
- **Memory Only**: Data is only held in memory during processing

## 📈 Version History

### v1.0.0 (Current)
- Initial release with Shopify, Amazon, and WooCommerce support
- Smart column mapping and data validation
- CSV and Excel export capabilities
- Comprehensive error handling and user feedback

---

**Built for Salaaz Marketplace** - Helping vendors efficiently manage bulk product uploads 🚀