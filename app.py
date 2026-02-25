import streamlit as st
import google.generativeai as genai
import base64
import json
import re
from datetime import date, datetime
from typing import Optional

# ─── PAGE CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="Aegis AI — Underwriting",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Epilogue:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --gold: #c88a00;
    --gold2: #e0a020;
    --green: #1a9455;
    --red: #d93251;
    --amber: #cc7a00;
    --blue: #2b76cc;
    --teal: #008f7c;
    --muted: #6b7fa3;
    --text: #1a2236;
    --border: #dce3ee;
    --surface: #f8f9fc;
}

/* Global reset */
html, body, [class*="css"] {
    font-family: 'Epilogue', sans-serif;
    color: #1a2236;
}

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Header */
.aegis-header {
    background: linear-gradient(180deg, #f4f7ff 0%, rgba(255,255,255,0.9) 100%);
    border-bottom: 1px solid #dce3ee;
    padding: 20px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
}

.aegis-logo {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #1a2236;
}

.aegis-logo .accent { color: #c88a00; }

.aegis-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #6b7fa3;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}

/* Steps bar */
.steps-bar {
    display: flex;
    background: #f8f9fc;
    border: 1px solid #dce3ee;
    border-radius: 6px;
    overflow: hidden;
    margin: 24px 0 20px 0;
}

.step-item {
    flex: 1;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-right: 1px solid #dce3ee;
    opacity: 0.35;
}

.step-item:last-child { border-right: none; }
.step-item.active { opacity: 1; }
.step-item.done { opacity: 0.65; }

.step-num {
    width: 30px; height: 30px;
    border-radius: 50%;
    border: 1.5px solid #6b7fa3;
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace; font-size: 12px;
    flex-shrink: 0;
}

.step-item.active .step-num { border-color: #c88a00; color: #c88a00; background: rgba(200,138,0,.1); }
.step-item.done .step-num { border-color: #1a9455; color: #1a9455; background: rgba(26,148,85,.1); }
.step-label { font-size: 13px; font-weight: 500; color: #1a2236; }
.step-sub { font-size: 11px; color: #6b7fa3; }

/* Metric cards */
.metric-card {
    background: #f8f9fc;
    border: 1px solid #dce3ee;
    border-radius: 8px;
    padding: 18px 16px;
    text-align: center;
}

.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 1.5px;
    text-transform: uppercase; color: #6b7fa3;
    margin-bottom: 8px;
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 700;
    color: #1a2236;
}

.metric-sub { font-size: 11px; color: #6b7fa3; margin-top: 4px; }

/* Decision card */
.decision-card {
    border-radius: 8px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 24px;
    border: 1px solid;
}

.decision-card.standard { background: rgba(26,148,85,.07); border-color: rgba(26,148,85,.3); }
.decision-card.loading  { background: rgba(204,122,0,.07); border-color: rgba(204,122,0,.3); }
.decision-card.decline  { background: rgba(217,50,81,.07);  border-color: rgba(217,50,81,.3); }

/* Flag items */
.flag-item {
    display: flex; gap: 10px;
    padding: 10px 12px; border-radius: 4px;
    margin-bottom: 8px; font-size: 12px;
    border-left: 3px solid;
}

.flag-DECLINE   { background: rgba(217,50,81,.08);  border-color: #d93251; }
.flag-MANUAL_UW { background: rgba(204,122,0,.08);  border-color: #cc7a00; }
.flag-WARNING   { background: rgba(200,138,0,.08);  border-color: #c88a00; }
.flag-INFO      { background: rgba(43,118,204,.08); border-color: #2b76cc; }

/* Premium blocks */
.prem-block {
    background: #f8f9fc;
    border: 1px solid #dce3ee;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 12px;
}

.prem-head {
    display: flex; justify-content: space-between;
    padding: 10px 16px;
    background: rgba(200,138,0,.06);
    border-bottom: 1px solid #dce3ee;
    font-size: 12px; font-weight: 600;
}

.prem-line {
    display: flex; justify-content: space-between;
    padding: 8px 16px; font-size: 12px;
    border-top: 1px solid rgba(200,210,230,.7);
}

.prem-total {
    background: rgba(200,138,0,.06);
    font-weight: 600; font-size: 13px;
}

/* Grand total */
.grand-total {
    background: linear-gradient(135deg, #f8f9fc 0%, #e8eef8 100%);
    border: 2px solid #c88a00;
    border-radius: 8px;
    padding: 28px 36px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 24px;
}

.gt-name { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; }
.gt-label { color: #6b7fa3; font-size: 14px; margin-top: 4px; }
.gt-amount { font-family: 'Syne', sans-serif; font-size: 42px; font-weight: 800; color: #c88a00; text-align: right; }
.gt-sub { font-size: 12px; color: #6b7fa3; text-align: right; margin-top: 4px; }

/* EMR rows */
.emr-row {
    display: flex; justify-content: space-between;
    padding: 7px 0; font-size: 13px;
    border-bottom: 1px solid rgba(200,210,230,.7);
}

.emr-row:last-child { border-bottom: none; }
.ep { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.pos-pt { color: #d93251; }
.neg-pt { color: #1a9455; }
.neu-pt { color: #4a5a7a; }

/* Upload box */
.upload-box {
    border: 2px dashed #c8d3e6;
    border-radius: 8px;
    padding: 64px 40px;
    text-align: center;
    background: #f8f9fc;
    transition: all .25s;
}

/* Section headers */
.section-hdr {
    font-family: 'Syne', sans-serif;
    font-size: 18px; font-weight: 700;
    color: #1a2236;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #c88a00;
    display: inline-block;
}

/* Policy badge */
.policy-badge {
    display: flex; align-items: center; gap: 14px;
    padding: 8px 18px 8px 12px;
    background: #f8f9fc;
    border: 1px solid #dce3ee;
    border-radius: 50px;
}

.profile-circle {
    width: 42px; height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, #c88a00, #e0a020);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    border: 2px solid #c88a00;
}

.live-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #c88a00;
    display: inline-block;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%,100%{opacity:1;transform:scale(1)}
    50%{opacity:.4;transform:scale(.7)}
}

/* Streamlit overrides */
div[data-testid="stFileUploader"] { border: none !important; }
div[data-testid="stFileUploader"] > div { background: #f8f9fc !important; border: 2px dashed #c8d3e6 !important; border-radius: 8px !important; }

button[kind="primary"] {
    background-color: #c88a00 !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
}

.stExpander { border: 1px solid #dce3ee !important; border-radius: 6px !important; }

div[data-testid="stMetric"] {
    background: #f8f9fc;
    border: 1px solid #dce3ee;
    border-radius: 8px;
    padding: 16px;
}

/* Hide streamlit default elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── UNDERWRITING TABLES ────────────────────────────────────────
BMI_T = [(0,18,10),(19,23,0),(24,28,5),(29,33,10),(34,38,15),(39,9999,20)]
FAM_E = {"both_above_65": -10, "one_above_65": -5, "both_below_65": 10}
H_E   = {"thyroid":[2.5,5,7.5,10],"asthma":[5,7.5,10,12.5],"hypertension":[5,7.5,10,15],"diabetes":[10,15,20,25],"gut_disorder":[5,10,15,20]}
CO_M  = {2:20, 3:40}
HAB_E = {"smoking":{"occasionally":5,"moderate":10,"high":15},"alcohol":{"occasionally":5,"moderate":10,"high":15},"tobacco":{"occasionally":5,"moderate":10,"high":15}}
HAB_C = {2:20, 3:40}
OCC_E = {"athlete":2,"pilot":6,"driver":2,"merchant_navy":3,"oil_gas":3}
L_RAT = [(20,35,"I",1),(40,60,"II",2),(65,85,"III",3),(90,120,"IV",4),(125,170,"V",6),(175,225,"VI",8),(230,275,"VII",10),(280,350,"VIII",12),(355,450,"IX",16),(455,550,"X",20)]
C_RAT = [(0,20,"Std",0),(21,35,"I",1),(36,60,"II",2),(61,75,"III",3),(76,100,"IV",4)]
P_RAT = [(18,35,1.5,1.0,3.0),(36,40,3.0,1.0,6.0),(41,45,4.5,1.0,12.0),(46,50,6.0,1.0,15.0),(51,55,7.5,1.5,20.0),(56,60,9.0,1.5,25.0),(61,65,10.5,1.5,None)]
FIN_T = [(0,35,25),(36,45,20),(46,50,15),(51,55,15),(56,999,10)]

CL = {"thyroid":"Thyroid","asthma":"Asthma","hypertension":"Hypertension","diabetes":"Diabetes Mellitus","gut_disorder":"Gut Disorder"}
HL = {"smoking":"Smoking","alcohol":"Alcohol","tobacco":"Tobacco"}
OL = {"pilot":"Commercial Pilot","athlete":"Professional Athlete","driver":"Public Carrier Driver","merchant_navy":"Merchant Navy","oil_gas":"Oil & Gas Onshore"}

# ─── HELPER FUNCTIONS ───────────────────────────────────────────
def calc_age(dob: date) -> int:
    today = date.today()
    age = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return age

def calc_bmi(weight_kg: float, height_cm: float) -> float:
    return round(weight_kg / ((height_cm / 100) ** 2), 1)

def lookup_bmi_points(b: float) -> float:
    for lo, hi, pts in BMI_T:
        if lo <= b <= hi:
            return pts
    return 20

def lookup_life_rating(emr: float):
    for lo, hi, cls, fac in L_RAT:
        if lo <= emr <= hi:
            return {"cls": cls, "fac": fac}
    return None

def lookup_cir_rating(emr: float):
    for lo, hi, cls, fac in C_RAT:
        if lo <= emr <= hi:
            return {"cls": cls, "fac": fac}
    return None

def lookup_premium_rates(age: int):
    for lo, hi, *rates in P_RAT:
        if lo <= age <= hi:
            return rates
    return None

def lookup_financial_multiple(age: int) -> int:
    for lo, hi, m in FIN_T:
        if lo <= age <= hi:
            return m
    return 10

def fmt_inr(amount: float) -> str:
    return f"₹ {int(round(amount)):,}"

def fmt_pts(pts: float) -> str:
    return f"+{pts:.1f}" if pts >= 0 else f"{pts:.1f}"

# ─── UNDERWRITING ENGINE ────────────────────────────────────────
def compute_underwriting(d: dict) -> dict:
    dob = datetime.strptime(d["dob"], "%Y-%m-%d").date() if isinstance(d["dob"], str) else d["dob"]
    A = calc_age(dob)
    B = calc_bmi(d["weight_kg"], d["height_cm"])

    e_bmi = lookup_bmi_points(B)
    e_fam = FAM_E.get(d.get("parent_health_status", ""), 0)

    # Health conditions
    h_brk = {}
    active_conds = []
    for c, sev in (d.get("health_conditions") or {}).items():
        sev = int(sev)
        if sev > 0 and c in H_E:
            h_brk[c] = H_E[c][sev - 1]
            active_conds.append(c)
        else:
            h_brk[c] = 0

    n_conds = len(active_conds)
    co_m = CO_M.get(min(n_conds, 3), 0) if n_conds >= 2 else 0
    e_health = sum(h_brk.values()) + co_m

    # Habits
    hab_brk = {}
    active_habs = []
    for h, freq in (d.get("habits") or {}).items():
        if freq and freq != "none":
            pts = (HAB_E.get(h) or {}).get(freq, 0)
            hab_brk[h] = pts
            if pts > 0:
                active_habs.append(h)
        else:
            hab_brk[h] = 0

    n_habs = len(active_habs)
    hab_c = HAB_C.get(min(n_habs, 3), 0) if n_habs >= 2 else 0
    e_hab = sum(hab_brk.values()) + hab_c

    EMR = e_bmi + e_fam + e_health + e_hab
    LR = lookup_life_rating(EMR)
    CR = lookup_cir_rating(EMR)

    # Verdict
    if A < 18 or A > 65 or EMR > 550:
        verdict, dcl = "Policy Declined", "decline"
    elif EMR < 20:
        verdict, dcl = "Standard Acceptance", "standard"
    else:
        verdict, dcl = "Acceptance with Loading", "loading"

    # Flags
    flags = []
    if A < 18: flags.append({"s":"DECLINE","m":f"Age {A} below minimum insurable age of 18."})
    if A > 65: flags.append({"s":"DECLINE","m":f"Age {A} exceeds maximum insurable age of 65."})
    if A > 60 and A <= 65: flags.append({"s":"WARNING","m":"CIR unavailable above age 60 — CIR will be declined."})
    if B < 18: flags.append({"s":"MANUAL_UW","m":f"BMI {B} below 18 (underweight) — manual medical review required."})
    if B > 38: flags.append({"s":"MANUAL_UW","m":f"BMI {B} above 38 — not in standard table, manual review needed."})
    if n_conds >= 4: flags.append({"s":"MANUAL_UW","m":f"{n_conds} conditions found. Table covers max 3 — manual UW required."})
    for c, sev in (d.get("health_conditions") or {}).items():
        if int(sev) == 4:
            flags.append({"s":"MANUAL_UW","m":f"{CL.get(c,c)} at Severity Level 4 — medical officer review required."})
    if EMR > 550: flags.append({"s":"DECLINE","m":f"Total EMR {EMR:.1f} exceeds ratable maximum of 550."})
    if EMR > 100 and d.get("cir_cover",0) > 0:
        flags.append({"s":"WARNING","m":f"EMR {EMR:.1f} exceeds CIR ceiling of 100 — CIR will be declined."})
    fin_mult = lookup_financial_multiple(A)
    fin_limit = d.get("yearly_income", 0) * fin_mult
    if d.get("base_cover", 0) > fin_limit:
        flags.append({"s":"MANUAL_UW","m":f"Life cover {fmt_inr(d['base_cover'])} exceeds financial UW limit ({fin_mult}× income = {fmt_inr(fin_limit)})."})
    if len(d.get("risky_occupations", [])) > 1:
        flags.append({"s":"MANUAL_UW","m":"Multiple risky occupations declared — manual review required."})

    # Premiums
    rates = lookup_premium_rates(A)
    occ_pm = sum(OCC_E.get(o, 0) for o in (d.get("risky_occupations") or []))

    l_B = a_B = c_B = {}
    l_T = a_T = c_T = 0.0

    if rates and 18 <= A <= 65:
        lr, ar, cr = rates
        # Life
        lb = (lr * d.get("base_cover", 0)) / 1000
        lf = LR["fac"] if LR else 0
        ll = 0.25 * lf * lb
        lo = (occ_pm * d.get("base_cover", 0)) / 1000
        l_T = lb + ll + lo
        l_B = {"base": lb, "fac": lf, "load": ll, "occ": lo, "total": l_T, "cls": LR["cls"] if LR else None, "rate": lr}

        # Accident
        ab = (ar * d.get("accident_cover", 0)) / 1000
        ao = (occ_pm * d.get("accident_cover", 0)) / 1000
        a_T = ab + ao
        a_B = {"base": ab, "occ": ao, "total": a_T, "rate": ar}

        # CIR
        if A > 60 or EMR > 100 or not cr:
            c_B = {"declined": True, "reason": "CIR not available above age 60" if A > 60 else f"EMR {EMR:.1f} exceeds CIR max of 100"}
        else:
            cb = (cr * d.get("cir_cover", 0)) / 1000
            cf = CR["fac"] if CR else 0
            cl = 0.30 * cf * cb
            c_T = cb + cl
            c_B = {"base": cb, "fac": cf, "load": cl, "total": c_T, "cls": CR["cls"] if CR else None, "rate": cr}

    return {
        "A": A, "B": B, "EMR": EMR, "LR": LR, "CR": CR,
        "verdict": verdict, "dcl": dcl, "flags": flags,
        "e_bmi": e_bmi, "e_fam": e_fam, "h_brk": h_brk, "co_m": co_m,
        "e_health": e_health, "hab_brk": hab_brk, "hab_c": hab_c, "e_hab": e_hab,
        "l_B": l_B, "a_B": a_B, "c_B": c_B,
        "grand": l_T + a_T + c_T,
        "n_active_conds": n_conds
    }

# ─── AI EXTRACTION ──────────────────────────────────────────────
def extract_from_pdf(pdf_bytes: bytes) -> dict:
    genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", ""))
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = """You are an expert insurance underwriter. Extract ALL fields from this life insurance proposal form PDF.

Return ONLY a valid JSON object with EXACTLY these keys (no markdown, no backticks, just raw JSON):

{
  "name": "string",
  "gender": "Male or Female",
  "dob": "YYYY-MM-DD",
  "height_cm": number,
  "weight_kg": number,
  "yearly_income": number,
  "source_of_income": "salary|business|profession|other",
  "base_cover": number,
  "cir_cover": number,
  "accident_cover": number,
  "parent_health_status": "both_above_65|one_above_65|both_below_65",
  "health_conditions": {
    "thyroid": 0,
    "asthma": 0,
    "hypertension": 0,
    "diabetes": 0,
    "gut_disorder": 0
  },
  "habits": {
    "smoking": "none",
    "alcohol": "none",
    "tobacco": "none"
  },
  "risky_occupations": [],
  "extraction_notes": ""
}

Rules:
- health_conditions severity: 0=not present, 1=sev1, 2=sev2, 3=sev3, 4=sev4
- habits: none|occasionally|moderate|high
- risky_occupations: array with values from: pilot, athlete, driver, merchant_navy, oil_gas
- Return ONLY the JSON. Nothing else."""

    pdf_part = {"mime_type": "application/pdf", "data": pdf_bytes}
    response = model.generate_content([pdf_part, prompt])

    raw = response.text
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

# ─── SESSION STATE ──────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 1
if "data" not in st.session_state:
    st.session_state.data = None
if "result" not in st.session_state:
    st.session_state.result = None
if "policy_no" not in st.session_state:
    st.session_state.policy_no = "PQ-2025-00187"

# ─── HEADER ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="aegis-header">
  <div>
    <div class="aegis-logo">Aegis<span class="accent">AI</span></div>
    <div class="aegis-sub">AI-Powered Life Insurance Underwriting</div>
  </div>
  <div style="display:flex;align-items:center;gap:16px;">
    <div style="display:flex;align-items:center;gap:8px;background:rgba(200,138,0,.08);border:1px solid rgba(200,138,0,.25);padding:8px 16px;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#c88a00;letter-spacing:1px;">
      <span class="live-dot"></span>AEGIS AI · LIVE ENGINE
    </div>
    <div class="policy-badge">
      <div class="profile-circle">👤</div>
      <div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#6b7fa3;">Policy Quote No.</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:600;color:#1a2236;">{st.session_state.policy_no}</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── MAIN CONTAINER ─────────────────────────────────────────────
st.markdown('<div style="max-width:1300px;margin:0 auto;padding:32px 48px 80px;">', unsafe_allow_html=True)

# ─── STEPS BAR ──────────────────────────────────────────────────
step = st.session_state.step

def step_html(num, label, sub):
    cls = "active" if num == step else ("done" if num < step else "")
    num_display = "✓" if num < step else str(num)
    return f'<div class="step-item {cls}"><div class="step-num">{num_display}</div><div><div class="step-label">{label}</div><div class="step-sub">{sub}</div></div></div>'

st.markdown(f"""
<div class="steps-bar">
  {step_html(1, "Upload PDF", "Proposal Form")}
  {step_html(2, "AI Extraction", "Reading document")}
  {step_html(3, "Review Data", "Verify & correct")}
  {step_html(4, "Underwriting", "EMR + Premium")}
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# STEP 1 — UPLOAD
# ═══════════════════════════════════════════════════════════════
if step == 1:
    st.markdown('<div class="section-hdr">Upload Proposal Form</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded = st.file_uploader(
            "Drop your PDF here or click to browse",
            type=["pdf"],
            help="Upload the insurance proposal form PDF (max 20MB)"
        )

        if uploaded:
            if uploaded.size > 20 * 1024 * 1024:
                st.error("File too large. Please use a PDF under 20MB.")
            else:
                st.success(f"✅ **{uploaded.name}** — {uploaded.size/1024:.1f} KB")
                if st.button("🚀  Extract with Aegis AI", use_container_width=True, type="primary"):
                    with st.spinner(""):
                        st.markdown("""
                        <div style="background:#f8f9fc;border:1px solid #dce3ee;border-radius:8px;padding:32px;text-align:center;margin-top:16px;">
                          <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;margin-bottom:8px;color:#1a2236;">Aegis AI Reading Proposal Form…</div>
                          <div style="color:#6b7fa3;font-size:13px;">Extracting fields, conditions, habits & occupational disclosures</div>
                        </div>
                        """, unsafe_allow_html=True)

                        progress = st.progress(0)
                        status = st.empty()
                        logs = [
                            "Connecting to Aegis AI engine...",
                            "Sending PDF document...",
                            "Parsing document layout...",
                            "Extracting personal details...",
                            "Reading health conditions & severity...",
                            "Identifying habits & frequency...",
                            "Checking occupational disclosures...",
                            "Validating cover & financial data...",
                            "Finalising extraction..."
                        ]
                        import time
                        for i, log in enumerate(logs[:3]):
                            status.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;color:#008f7c;padding:4px 0;">> {log}</div>', unsafe_allow_html=True)
                            progress.progress((i + 1) / 9)
                            time.sleep(0.3)

                        try:
                            extracted = extract_from_pdf(uploaded.read())
                            for i, log in enumerate(logs[3:], 3):
                                status.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;color:#008f7c;padding:4px 0;">> {log}</div>', unsafe_allow_html=True)
                                progress.progress((i + 1) / 9)
                                time.sleep(0.2)

                            st.session_state.data = extracted
                            st.session_state.step = 3
                            st.rerun()
                        except Exception as e:
                            st.error(f"Extraction failed: {str(e)}")
                            progress.empty()
                            status.empty()

    # Manual entry option
    st.markdown("<div style='text-align:center;margin-top:24px;color:#6b7fa3;font-size:13px;'>— or —</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✍️  Enter Details Manually", use_container_width=True):
            st.session_state.data = {
                "name": "", "gender": "Male", "dob": "1985-01-01",
                "height_cm": 170, "weight_kg": 70, "yearly_income": 1000000,
                "source_of_income": "salary", "base_cover": 10000000,
                "cir_cover": 2000000, "accident_cover": 2000000,
                "parent_health_status": "both_above_65",
                "health_conditions": {"thyroid":0,"asthma":0,"hypertension":0,"diabetes":0,"gut_disorder":0},
                "habits": {"smoking":"none","alcohol":"none","tobacco":"none"},
                "risky_occupations": [], "extraction_notes": ""
            }
            st.session_state.step = 3
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# STEP 3 — REVIEW & EDIT
# ═══════════════════════════════════════════════════════════════
elif step == 3:
    d = st.session_state.data

    st.markdown('<div class="section-hdr">Review & Verify Extracted Data</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#6b7fa3;font-size:13px;margin-bottom:24px;">Edit any field before computing underwriting</div>', unsafe_allow_html=True)

    if d.get("extraction_notes"):
        st.warning(f"⚠️ **Extraction Notes:** {d['extraction_notes']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**👤 Personal Details**")
        name = st.text_input("Full Name", value=d.get("name", ""), key="name")
        gender = st.selectbox("Gender", ["Male", "Female"], index=0 if d.get("gender","Male") == "Male" else 1)

        dob_default = datetime.strptime(d["dob"], "%Y-%m-%d").date() if d.get("dob") else date(1985, 1, 1)
        dob = st.date_input("Date of Birth", value=dob_default, min_value=date(1940,1,1), max_value=date(2010,1,1))

        age_computed = calc_age(dob)
        st.markdown(f'<div style="background:#f8f9fc;border:1px solid #dce3ee;border-radius:4px;padding:8px 12px;font-family:\'JetBrains Mono\',monospace;font-size:12px;color:#1a9455;margin-bottom:8px;">Age: <strong>{age_computed} years</strong></div>', unsafe_allow_html=True)

        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=int(d.get("height_cm", 170)))
        weight = st.number_input("Weight (kg)", min_value=30, max_value=250, value=int(d.get("weight_kg", 70)))

        if height and weight:
            bmi_val = calc_bmi(weight, height)
            bmi_color = "#d93251" if bmi_val > 30 or bmi_val < 18 else "#1a9455"
            st.markdown(f'<div style="background:#f8f9fc;border:1px solid #dce3ee;border-radius:4px;padding:8px 12px;font-family:\'JetBrains Mono\',monospace;font-size:12px;color:{bmi_color};margin-bottom:8px;">BMI: <strong>{bmi_val}</strong></div>', unsafe_allow_html=True)

        st.markdown("**💰 Financial**")
        income = st.number_input("Yearly Income (₹)", min_value=0, value=int(d.get("yearly_income", 1000000)), step=50000)
        income_src = st.selectbox("Income Source", ["salary","business","profession","other"],
            index=["salary","business","profession","other"].index(d.get("source_of_income","salary")))

        st.markdown("**🛡️ Cover Required**")
        base_cover = st.number_input("Life Cover (₹)", min_value=0, value=int(d.get("base_cover", 10000000)), step=500000)
        cir_cover = st.number_input("CIR Cover (₹)", min_value=0, value=int(d.get("cir_cover", 2000000)), step=500000)
        acc_cover = st.number_input("Accident Cover (₹)", min_value=0, value=int(d.get("accident_cover", 2000000)), step=500000)

    with col2:
        st.markdown("**👨‍👩‍👧 Family History**")
        fam_opts = {"both_above_65": "Both parents alive/died > age 65", "one_above_65": "Only one parent > age 65", "both_below_65": "Both died < age 65"}
        fam_val = d.get("parent_health_status", "both_above_65")
        fam_sel = st.radio("Parent Health Status", options=list(fam_opts.keys()),
            format_func=lambda x: fam_opts[x], index=list(fam_opts.keys()).index(fam_val))

        st.markdown("**⚙️ Risky Occupations**")
        occ_map = {"pilot":"Commercial Pilot (₹6/mille)","athlete":"Professional Athlete (₹2/mille)",
                   "driver":"Public Carrier Driver (₹2/mille)","merchant_navy":"Merchant Navy (₹3/mille)","oil_gas":"Oil & Gas Onshore (₹3/mille)"}
        cur_occs = d.get("risky_occupations", [])
        selected_occs = []
        for occ_key, occ_label in occ_map.items():
            if st.checkbox(occ_label, value=occ_key in cur_occs, key=f"occ_{occ_key}"):
                selected_occs.append(occ_key)

    with col3:
        st.markdown("**🏥 Health Conditions**")
        sev_opts = ["None", "Severity 1", "Severity 2", "Severity 3", "Severity 4"]
        conds = d.get("health_conditions", {})
        new_conds = {}
        for c_key, c_label in CL.items():
            cur_sev = int(conds.get(c_key, 0))
            sel = st.selectbox(c_label, sev_opts, index=cur_sev, key=f"cond_{c_key}")
            new_conds[c_key] = sev_opts.index(sel)

        st.markdown("**🚬 Personal Habits**")
        hab_opts = ["none", "occasionally", "moderate", "high"]
        hab_labels = ["None", "Occasionally", "Moderate", "High"]
        habits = d.get("habits", {})
        new_habits = {}
        for h_key, h_label in HL.items():
            cur_hab = habits.get(h_key, "none")
            cur_idx = hab_opts.index(cur_hab) if cur_hab in hab_opts else 0
            sel = st.selectbox(h_label, hab_opts, index=cur_idx, format_func=lambda x: x.capitalize() if x != "none" else "None", key=f"hab_{h_key}")
            new_habits[h_key] = sel

    st.markdown("---")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        if st.button("⚡  Compute Underwriting & Premium", use_container_width=True, type="primary"):
            updated_data = {
                "name": name, "gender": gender,
                "dob": dob.strftime("%Y-%m-%d"),
                "height_cm": height, "weight_kg": weight,
                "yearly_income": income, "source_of_income": income_src,
                "base_cover": base_cover, "cir_cover": cir_cover, "accident_cover": acc_cover,
                "parent_health_status": fam_sel,
                "health_conditions": new_conds, "habits": new_habits,
                "risky_occupations": selected_occs
            }
            st.session_state.data = updated_data
            st.session_state.result = compute_underwriting(updated_data)
            st.session_state.step = 4
            st.rerun()
    with col_b:
        if st.button("↩  Upload New PDF", use_container_width=True):
            st.session_state.step = 1
            st.session_state.data = None
            st.session_state.result = None
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# STEP 4 — RESULTS
# ═══════════════════════════════════════════════════════════════
elif step == 4:
    r = st.session_state.result
    d = st.session_state.data

    # Decision card
    ico_map = {"standard": "✅", "loading": "⚡", "decline": "🚫"}
    color_map = {"standard": "#1a9455", "loading": "#cc7a00", "decline": "#d93251"}
    dcl_color = color_map[r["dcl"]]
    ico = ico_map[r["dcl"]]

    st.markdown(f"""
    <div class="decision-card {r['dcl']}">
      <div style="font-size:52px;">{ico}</div>
      <div>
        <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:{dcl_color};">{r['verdict']}</div>
        <div style="font-size:14px;color:#1a2236;opacity:.8;margin-top:4px;">
          {d.get('name','—')} &nbsp;·&nbsp; Age {r['A']} &nbsp;·&nbsp; BMI {r['B']} &nbsp;·&nbsp;
          Total EMR: <strong>{r['EMR']:.1f} pts</strong>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric row
    emr_color = "#d93251" if r["EMR"] > 175 else "#cc7a00" if r["EMR"] > 85 else "#1a9455"
    flags_color = "#cc7a00" if r["flags"] else "#1a9455"
    has_decline = any(f["s"] == "DECLINE" for f in r["flags"])
    flag_sub = "Includes DECLINE" if has_decline else (f"{len(r['flags'])} issues" if r["flags"] else "All clear")
    lr = r["LR"]
    cr = r["CR"]
    cB = r["c_B"]

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        (col1, "Total EMR", f"{r['EMR']:.1f}", "Mortality Points", emr_color),
        (col2, "Life Class", f"Class {lr['cls']}" if lr else "Std", f"Factor × {lr['fac'] if lr else '—'}", "#1a2236"),
        (col3, "CIR Class", "N/A" if cB.get("declined") else (f"Class {cr['cls']}" if cr else "Std"), "Declined" if cB.get("declined") else f"Factor × {cr['fac'] if cr else '—'}", "#1a2236"),
        (col4, "Active Conditions", str(r["n_active_conds"]), "of 5 declared", "#d93251" if r["n_active_conds"] >= 3 else "#1a2236"),
        (col5, "UW Flags", str(len(r["flags"])), flag_sub, flags_color),
    ]

    for col, label, val, sub, color in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value" style="color:{color};">{val}</div>
              <div class="metric-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

    # Three columns: EMR breakdown | Flags | Premium
    col1, col2, col3 = st.columns([1.2, 1, 1])

    with col1:
        st.markdown("**📊 EMR Breakdown**")
        with st.container():
            h_brk = r["h_brk"]
            hab_brk = r["hab_brk"]

            rows_html = ""
            bmi_color = "pos-pt" if r["e_bmi"] > 0 else "neg-pt" if r["e_bmi"] < 0 else "neu-pt"
            rows_html += f'<div class="emr-row"><span>BMI Loading ({r["B"]})</span><span class="ep {bmi_color}">{fmt_pts(r["e_bmi"])}</span></div>'

            fam_color = "pos-pt" if r["e_fam"] > 0 else "neg-pt" if r["e_fam"] < 0 else "neu-pt"
            rows_html += f'<div class="emr-row"><span>Family History</span><span class="ep {fam_color}">{fmt_pts(r["e_fam"])}</span></div>'

            rows_html += '<div class="emr-row" style="padding-bottom:0;border-bottom:none;"><span><strong>Health Conditions</strong></span></div>'
            for c, pts in h_brk.items():
                if pts != 0:
                    rows_html += f'<div class="emr-row emr-sub" style="padding-left:16px;opacity:.8;"><span>{CL.get(c,c)}</span><span class="ep pos-pt">{fmt_pts(pts)}</span></div>'
            if r["co_m"] > 0:
                rows_html += f'<div class="emr-row" style="padding-left:16px;font-style:italic;"><span>↳ Co-morbidity extra</span><span class="ep pos-pt">{fmt_pts(r["co_m"])}</span></div>'

            rows_html += '<div class="emr-row" style="padding-bottom:0;border-bottom:none;margin-top:6px;"><span><strong>Personal Habits</strong></span></div>'
            for h, pts in hab_brk.items():
                if pts != 0:
                    rows_html += f'<div class="emr-row" style="padding-left:16px;opacity:.8;"><span>{HL.get(h,h)}</span><span class="ep pos-pt">{fmt_pts(pts)}</span></div>'
            if r["hab_c"] > 0:
                rows_html += f'<div class="emr-row" style="padding-left:16px;font-style:italic;"><span>↳ Co-existence extra</span><span class="ep pos-pt">{fmt_pts(r["hab_c"])}</span></div>'

            emr_c = "#d93251" if r["EMR"] > 175 else "#cc7a00" if r["EMR"] > 85 else "#008f7c"
            rows_html += f'<div class="emr-row" style="border-top:2px solid #dce3ee;margin-top:8px;padding-top:12px;font-weight:700;"><span>TOTAL EMR</span><span class="ep" style="font-size:16px;font-weight:700;color:{emr_c};">{fmt_pts(r["EMR"])}</span></div>'

            st.markdown(f'<div style="background:#f8f9fc;border:1px solid #dce3ee;border-radius:6px;padding:16px 18px;">{rows_html}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("**🚩 UW Flags & Edge Cases**")
        fi_map = {"DECLINE": "🔴", "MANUAL_UW": "🟠", "WARNING": "🟡", "INFO": "🔵"}
        if r["flags"]:
            for f in r["flags"]:
                sev_colors = {"DECLINE":"#d93251","MANUAL_UW":"#cc7a00","WARNING":"#c88a00","INFO":"#2b76cc"}
                sev_col = sev_colors.get(f["s"], "#6b7fa3")
                st.markdown(f"""
                <div class="flag-item flag-{f['s']}">
                  <div style="font-size:16px;flex-shrink:0;">{fi_map.get(f['s'],'⚪')}</div>
                  <div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1px;text-transform:uppercase;color:{sev_col};margin-bottom:2px;">{f['s']}</div>
                    <div style="font-size:12px;">{f['m']}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#6b7fa3;font-size:13px;padding:8px 0;">No underwriting flags raised.</div>', unsafe_allow_html=True)

    with col3:
        st.markdown("**💰 Premium Breakdown**")
        lB, aB, cB2 = r["l_B"], r["a_B"], r["c_B"]

        if lB.get("total"):
            st.markdown(f"""
            <div class="prem-block">
              <div class="prem-head"><span>🏦 Life Insurance (Term)</span><span style="color:#6b7fa3;">{fmt_inr(d.get('base_cover',0))}</span></div>
              <div class="prem-line"><span>Base (₹{lB['rate']}/mille)</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(lB['base'])}</span></div>
              <div class="prem-line"><span>Class {lB.get('cls','—')}, loading</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(lB['load'])}</span></div>
              <div class="prem-line"><span>Occupational extra</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(lB['occ'])}</span></div>
              <div class="prem-line prem-total"><span>Life Total</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(lB['total'])}</span></div>
            </div>
            """, unsafe_allow_html=True)

        if aB.get("total"):
            st.markdown(f"""
            <div class="prem-block">
              <div class="prem-head"><span>🚑 Accident Rider</span><span style="color:#6b7fa3;">{fmt_inr(d.get('accident_cover',0))}</span></div>
              <div class="prem-line"><span>Base (₹{aB['rate']}/mille)</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(aB['base'])}</span></div>
              <div class="prem-line"><span>Occupational extra</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(aB['occ'])}</span></div>
              <div class="prem-line prem-total"><span>Accident Total</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(aB['total'])}</span></div>
            </div>
            """, unsafe_allow_html=True)

        if cB2.get("declined"):
            st.markdown(f"""
            <div class="prem-block">
              <div class="prem-head"><span>🏥 CIR</span></div>
              <div class="prem-line" style="color:#d93251;font-style:italic;">⚠️ {cB2['reason']}</div>
            </div>
            """, unsafe_allow_html=True)
        elif cB2.get("total"):
            st.markdown(f"""
            <div class="prem-block">
              <div class="prem-head"><span>🏥 Critical Illness Rider</span><span style="color:#6b7fa3;">{fmt_inr(d.get('cir_cover',0))}</span></div>
              <div class="prem-line"><span>Base (₹{cB2['rate']}/mille)</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(cB2['base'])}</span></div>
              <div class="prem-line"><span>Class {cB2.get('cls','—')}, loading</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(cB2['load'])}</span></div>
              <div class="prem-line prem-total"><span>CIR Total</span><span style="font-family:'JetBrains Mono',monospace;color:#c88a00;">{fmt_inr(cB2['total'])}</span></div>
            </div>
            """, unsafe_allow_html=True)

    # Grand total
    today_str = date.today().strftime("%-d %b %Y")
    st.markdown(f"""
    <div class="grand-total">
      <div>
        <div class="gt-name">{d.get('name','—')}</div>
        <div class="gt-label">Grand Total Annual Premium</div>
      </div>
      <div>
        <div class="gt-amount">{fmt_inr(r['grand'])}</div>
        <div class="gt-sub">per annum · all covers · {today_str}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("↩  Upload Another Proposal Form", use_container_width=True):
            st.session_state.step = 1
            st.session_state.data = None
            st.session_state.result = None
            st.rerun()
    with col_b:
        if st.button("✏️  Edit & Recompute", use_container_width=True):
            st.session_state.step = 3
            st.session_state.result = None
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
