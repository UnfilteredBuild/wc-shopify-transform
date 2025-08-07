# Streamlit Deployment Guide

## 🌐 Deploy to Streamlit Community Cloud (FREE)

### Prerequisites
- GitHub account
- This project pushed to a GitHub repository

### Step-by-Step Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Add Streamlit WooCommerce to Shopify transformer"
   git remote add origin https://github.com/yourusername/wc-shopify-transform.git
   git push -u origin main
   ```

2. **Deploy on Streamlit**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub account
   - Select your repository: `wc-shopify-transform`
   - Set main file path: `app.py`
   - Click "Deploy!"

3. **Your app will be live at:**
   `https://yourusername-wc-shopify-transform-app-xyz123.streamlit.app`

### 🔧 Local Development

```bash
# Create virtual environment
python3 -m venv streamlit_env
source streamlit_env/bin/activate  # On Windows: streamlit_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

### 🎛️ Configuration Options

Create `.streamlit/config.toml` for custom settings:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
maxUploadSize = 200  # MB
```

### 📊 Analytics & Monitoring
- Streamlit Community Cloud provides basic analytics
- Monitor app performance in the Streamlit dashboard
- View logs and debug information

### 🔒 Environment Variables (if needed)
- Add secrets via Streamlit dashboard
- Access with `st.secrets["key_name"]`

### 💡 Tips for Better Performance
- Keep requirements.txt minimal
- Cache expensive operations with `@st.cache_data`
- Handle errors gracefully with try/except blocks