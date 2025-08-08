# How to Run the Refactored WooCommerce to Shopify Transformer

## 🚀 **Quick Start**

### 1. **Navigate to Project Directory:**
```bash
cd /Users/nigelfinley/Documents/Unfiltered_Projects/Card_Giants/wc_shopify_transform
```

### 2. **Activate Virtual Environment:**
```bash
source streamlit_env/bin/activate
```
*If you don't have a virtual environment set up yet:*
```bash
python3 -m venv streamlit_env
source streamlit_env/bin/activate
pip install -r requirements.txt
```

### 3. **Run the App:**
```bash
streamlit run src/app.py
```

## 📁 **File Structure**

The app is now organized into clean, modular components:

```
src/
├── app.py           # Main Streamlit application
├── transformer.py   # Core transformation logic
├── config.py       # Settings and constants
├── utils.py        # UI utility functions
└── __init__.py     # Package initialization
```

## 🔄 **Alternative Run Methods**

**From the src directory:**
```bash
cd src
streamlit run app.py
```

## ✅ **Testing the Setup**

To verify everything is working correctly:
```bash
python test_imports.py
```

This will test that all imports are working properly.

## 🐛 **Troubleshooting**

**Import Errors:**
- Make sure you're in the virtual environment: `source streamlit_env/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**Module Not Found:**
- Run from the root project directory, not from inside `src/`
- Use: `streamlit run src/app_clean.py`

**Port Issues:**
- If port 8501 is busy, Streamlit will automatically find another port
- Or specify a port: `streamlit run src/app_clean.py --server.port 8502`

## 🎯 **Benefits of the Refactored Version**

- **Cleaner Code**: Separated concerns and modular design
- **Easier Testing**: Each component can be tested independently
- **Better Maintainability**: Changes are isolated to specific modules
- **Type Safety**: Added type hints throughout
- **Error Handling**: Better error messages and validation