# 🛡️ Aegis AI — Insurance Underwriting Tool

AI-powered life insurance underwriting. Upload a proposal form PDF and get instant EMR scoring, risk flags, and premium breakdown.

---

## 🚀 Deploy & Share (Streamlit Community Cloud — Free)

### Step 1 — Push to GitHub
1. Create a new GitHub repo (public or private)
2. Upload all files: `app.py`, `requirements.txt`, `.streamlit/secrets.toml`

### Step 2 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app** → select your repo → set main file to `app.py`
4. Under **Advanced settings → Secrets**, add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxx"
   ```
5. Click **Deploy** — your shareable URL will be ready in ~60 seconds

### Step 3 — Share the link
Your app will be live at:
```
https://<your-app-name>.streamlit.app
```
Share this URL with anyone — no installation needed.

---

## 🏃 Run Locally

```bash
pip install -r requirements.txt

# Create secrets file
mkdir -p .streamlit
echo 'ANTHROPIC_API_KEY = "sk-ant-your-key"' > .streamlit/secrets.toml

# Run
streamlit run app.py
```

---

## ✨ Features

- **PDF Upload** — Drop any proposal form PDF; Claude AI extracts all fields automatically
- **Manual Entry** — Skip PDF and enter details directly
- **Review & Edit** — Verify/correct AI-extracted data before computing
- **EMR Engine** — Full mortality rating with BMI, family history, health conditions, habits, occupation
- **Flag System** — DECLINE / MANUAL_UW / WARNING / INFO flags with reasons
- **Premium Breakdown** — Life, CIR, Accident premiums with class loading
- **Shareable** — Single URL, no login required for end users

---

## 🔑 API Key

Get your key at [console.anthropic.com](https://console.anthropic.com)
