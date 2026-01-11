## 🩺 Early Sepsis Risk Monitoring Dashboard

This project is a Streamlit-based clinical decision-support tool developed during a hackathon. 
It helps identify early sepsis risk using rule-based qSOFA screening and patient vital trends.

⚠️ This tool is for educational and decision-support purposes only. It does NOT provide medical diagnosis.

### Features
- qSOFA-based sepsis risk scoring
- Patient-wise monitoring dashboard
- Time-series visualization of vitals
- Audio alert for high-risk patients
- Simple, explainable clinical rules

### Input
- CSV file containing patient vitals and lab data

### Tech Stack
- Python
- Streamlit
- Pandas
- Matplotlib

### How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
