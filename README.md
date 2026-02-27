# DoC Technology Maturity Assessment

50-state analysis of education technology infrastructure readiness across US Departments of Corrections.

## Setup

### Local Development

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and set your password
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select this repo
4. Set `app.py` as the main file
5. In **Advanced Settings > Secrets**, add:
   ```toml
   password = "your-chosen-password"
   ```
6. Deploy

### Password Protection

The app requires a password to access. Set it via:
- **Local**: `.streamlit/secrets.toml` (not committed to git)
- **Streamlit Cloud**: App settings > Secrets

## Data Sources

All data is estimated based on publicly available sources:
- Bureau of Justice Statistics (BJS)
- US Department of Education (ED.gov)
- State DoC publications and strategic plans
- State procurement portals

**This is a proof of concept. Data is for demonstration and planning purposes only.**
