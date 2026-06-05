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
