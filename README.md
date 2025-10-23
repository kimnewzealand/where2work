# Where2Work - Quick Start Guide

## ✅ Your App is Running!

The application is currently running at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://192.168.68.105:8501

## 🎯 What's Been Built

### Features Implemented:
1. ✅ **Data Loading** - Loads company_data.csv with validation
2. ✅ **Interactive Filters** - 4 filter controls in sidebar:
   - Entity Type (Company/Partnership)
   - Headquarters Location (Cities)
   - Employee Band Size (1-5, 6-19, 20-49)
   - Primary ANZSIC Code (Industry codes)
3. ✅ **Bubble Chart Visualization** - Interactive scatter plot at bottom of page
   - X-axis: Employee band size (smallest to largest)
   - Bubbles: Each company
   - Hover: Shows company details
4. ✅ **Metrics Dashboard** - Shows total companies, filtered count, and match percentage
5. ✅ **Hot Reload** - Automatic refresh on code changes

### Tech Stack:
- **Framework**: Streamlit (Python web framework)
- **Visualization**: Plotly (interactive charts)
- **Data Processing**: Pandas
- **Package Manager**: uv (ultra-fast Python package installer)

## 🚀 Running the App

### Current Session:
The app is already running! Just open http://localhost:8501 in your browser.

### To Restart:
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the app
streamlit run app.py
```

### To Stop:
Press `Ctrl+C` in the terminal where Streamlit is running.

## 🌐 Deploy to Streamlit Cloud (Free!)

**Summary**:
1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect GitHub and select your repo
4. Click "Deploy"
5. Get your free URL: `https://your-app.streamlit.app`

## 📊 Data Format

The app expects CSV with these columns:
- `Entity_Legal_Name` - Company name
- `Entity_Type` - Type of entity
- `Headquarters_Location` - City location
- `Estimated_Employee_Band` - Employee count range
- `Estimated_Employee_Band_Code` - Band code
- `Primary_ANZSIC_Code` - Industry classification

## 🎨 Customization Ideas

- **Add more filters**: Edit the sidebar section in `app.py`
- **Change colors**: Modify `.streamlit/config.toml`
- **Add charts**: Use Plotly Express (already imported)
- **Export data**: Add download button with `st.download_button()`

## 🐛 Troubleshooting

**App won't start?**
```bash
# Reinstall dependencies
uv pip install -r requirements.txt

# Check if port 8501 is in use
# Windows: netstat -ano | findstr :8501
```

**Data not loading?**
- Check that `company_data.csv` is in the same directory as `app.py`
- Verify CSV has the required columns

**Filters not working?**
- Clear browser cache
- Click "Clear All Filters" button
- Refresh the page

## 📝 Next Steps

1. ✅ Test locally (DONE!)
2. ⏭️ Deploy to Streamlit Cloud (see DEPLOYMENT.md)
3. ⏭️ Share URL with users for testing
4. ⏭️ Gather feedback and iterate

---

**Need Help?**
- Streamlit Docs: https://docs.streamlit.io/
- Plotly Docs: https://plotly.com/python/

