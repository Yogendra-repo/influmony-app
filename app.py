# app.py
import os, json, time
from pathlib import Path
import requests
import streamlit as st
import pandas as pd
import bcrypt

# ----------------- Page setup -----------------
st.set_page_config(page_title="🌍 Influmony!", layout="wide")

# Backend URL (FastAPI/Railway)
BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# ----------------- Global Styles (Treact-ish glass UI) -----------------
BG_URL = "https://media.licdn.com/dms/image/v2/C4D12AQFVxGkx714_oA/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1534840658881?e=2147483647&v=beta&t=3vthWXnw1iqVQqOLCeq2HemiBCiYSa9UYQHtOwtec8E"
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, .stApp {{ height: 100%; }}
.stApp {{
  background:
    linear-gradient(rgba(255,255,255,0.86), rgba(255,255,255,0.86)),
    url("{BG_URL}") center/cover fixed no-repeat;
  color: #0f172a;
  font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
}}
.card {{
  background: rgba(255,255,255,0.72);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.6);
  border-radius: 20px;
  padding: 22px 24px;
  box-shadow: 0 20px 50px rgba(2, 6, 23, 0.08);
  margin-bottom: 20px;
  transition: transform .2s ease, box-shadow .2s ease;
}}
/* subtle lift on hover */
.card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 25px 60px rgba(0,0,0,0.10);
}}

.stButton > button, .stDownloadButton > button {{
  background: linear-gradient(90deg, #2563EB, #3B82F6);
  color: #fff !important;
  font-weight: 700;
  border-radius: 12px;
  border: none;
  padding: 0.6rem 1rem;
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.25);
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  background: linear-gradient(90deg, #1E40AF, #1D4ED8);
  transform: translateY(-1px);
}}

.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1180px; }}
.badge {{
  display:inline-block; padding: 2px 10px; font-size: 12px; font-weight: 600;
  border-radius: 999px; background: rgba(37,99,235,0.12); color: #1E3A8A;
}}
hr {{ border: none; height: 1px; background: rgba(15,23,42,0.08); margin: 6px 0 18px; }}

/* ================================
   🔲 Black-bordered input styling
   (login, signup, campaign forms)
   ================================ */
.stTextInput > div > div > input,
.stTextArea  > div > textarea,
.stSelectbox > div > div {{
  border-radius: 12px !important;
  border: 2px solid rgba(0,0,0,0.65) !important;
  box-shadow: 0 0 5px rgba(0,0,0,0.15);
  background-color: rgba(255,255,255,0.92);
  color: #0f172a !important;
  font-weight: 500;
  padding: 12px 14px !important;
  font-size: 0.95rem !important;
}}

/* focus state: stronger black + slight glow */
.stTextInput > div > div > input:focus,
.stTextArea  > div > textarea:focus,
.stSelectbox > div > div:focus {{
  border-color: #000 !important;
  box-shadow: 0 0 8px rgba(0,0,0,0.30);
  background-color: rgba(255,255,255,0.98);
  outline: none !important;
}}

/* Professional placeholder look */
.stTextInput > div > div > input::placeholder,
.stTextArea  > div > textarea::placeholder {{
  color: #64748B;
  font-weight: 500;
  letter-spacing: 0.2px;
  opacity: 1;
}}

/* make selectbox text darker and consistent */
.stSelectbox label, .stSelectbox span {{
  color: #0f172a !important;
}}
</style>
""", unsafe_allow_html=True)

# ----------------- Reusable results renderer (UI only) -----------------
def render_matches_table(matches: list, *, key: str = "results"):
    # Guard
    if not matches:
        st.warning("No results to display")
        return

    # Always bind df first
    df = pd.DataFrame(matches).copy()

    # Extract subscores (display only)
    if "subscores" in df.columns:
        df["relevance"] = df["subscores"].apply(
            lambda x: float(x.get("relevance", 0)) if isinstance(x, dict) else None
        )
        df["follower_fit"] = df["subscores"].apply(
            lambda x: float(x.get("follower_fit", 0)) if isinstance(x, dict) else None
        )

    # Hashtag chips
    if "hashtags" in df.columns:
        df["hashtags"] = (
            df["hashtags"].fillna("").astype(str).str.split().apply(lambda xs: [x for x in xs if x][:8])
        )

    # Column order for display
    base_order = [
        "person_name","email","platform","followers",
        "continent","country","category","hashtags",
        "fit_score","relevance","follower_fit","outreach_message"
    ]
    show_cols = [c for c in base_order if c in df.columns] + [c for c in df.columns if c not in base_order]
    df = df[show_cols]

    # Summary metrics
    cols = st.columns(4)
    with cols[0]:
        st.metric("Results", len(df))
    with cols[1]:
        st.metric("Best Fit", f"{df['fit_score'].max():.2f}%")
    with cols[2]:
        st.metric("Avg Fit", f"{df['fit_score'].mean():.2f}%")
    with cols[3]:
        if "relevance" in df.columns and pd.notnull(df["relevance"]).any():
            st.metric("Avg Relevance", f"{df['relevance'].mean():.0f}%")

    # Table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=560,
        column_config={
            "person_name": st.column_config.TextColumn("Influencer", width="medium", help="Creator's display name"),
            "email": st.column_config.TextColumn("Email", width="large"),
            "platform": st.column_config.TextColumn("Platform", width="small"),
            "followers": st.column_config.NumberColumn("Followers", format="%,d", help="Total follower count"),
            "continent": st.column_config.TextColumn("Continent", width="small"),
            "country": st.column_config.TextColumn("Country", width="small"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "hashtags": st.column_config.ListColumn("Hashtags"),
            "fit_score": st.column_config.ProgressColumn("Fit Score", min_value=0, max_value=100, format="%.2f%%"),
            "relevance": st.column_config.ProgressColumn("Relevance", min_value=0, max_value=100, format="%.0f%%"),
            "follower_fit": st.column_config.ProgressColumn("Follower Fit", min_value=0, max_value=100, format="%.0f%%"),
            "outreach_message": st.column_config.TextColumn("Outreach Message", width="large"),
        },
    )

    # Safe CSV export with unique key
    try:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download as CSV",
            data=csv_bytes,
            file_name="influmony_matches.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"download_csv_{key}",
        )
    except Exception as e:
        st.caption(f"CSV export unavailable: {e}")

# ----------------- Simple local auth (bcrypt + JSON) -----------------
USERS_PATH = Path("data/local_users.json")
USERS_PATH.parent.mkdir(parents=True, exist_ok=True)

# Seed with your two users on first run (using your provided bcrypt hashes)
SEED_USERS = {
    "admin": {
        "email": "admin@example.com",
        "password_hash": "$2b$12$QVLx2ilNwSaXHg51PXTu5umgUXpqJO08rrgxxTsWDYVLH633ADbzC",  # admin
        "created_at": int(time.time())
    },
    "demo": {
        "email": "demo@example.com",
        "password_hash": "$2b$12$tcvPDDZBxjUd8CzFKSb8f.8y2oZNFyt8GmF5/OTkTeMRoyx3Y.IXW",  # demo
        "created_at": int(time.time())
    }
}

def _load_users() -> dict:
    if not USERS_PATH.exists():
        USERS_PATH.write_text(json.dumps({"users": SEED_USERS}, indent=2))
    try:
        data = json.loads(USERS_PATH.read_text())
        if "users" not in data or not isinstance(data["users"], dict):
            data = {"users": SEED_USERS}
            USERS_PATH.write_text(json.dumps(data, indent=2))
        return data
    except Exception:
        USERS_PATH.write_text(json.dumps({"users": SEED_USERS}, indent=2))
        return {"users": SEED_USERS}

def _save_users(data: dict):
    USERS_PATH.write_text(json.dumps(data, indent=2))

def add_user(username: str, email: str, password: str) -> None:
    username = (username or "").strip()
    email = (email or "").strip()
    if not username or not password:
        raise ValueError("Username and password required.")
    users = _load_users()
    if username in users["users"]:
        raise ValueError("Username already exists.")
    hashed = bcrypt.hashpw(password.strip().encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users["users"][username] = {"email": email, "password_hash": hashed, "created_at": int(time.time())}
    _save_users(users)

def verify_user(username: str, password: str) -> bool:
    users = _load_users()["users"]
    user = users.get((username or "").strip())
    if not user:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))
    except Exception:
        return False

# Session keys
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None
if "search_results" not in st.session_state:
    st.session_state["search_results"] = None
if "campaign_brief" not in st.session_state:
    st.session_state["campaign_brief"] = ""
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "company_name" not in st.session_state:
    st.session_state["company_name"] = ""

# ----------------- Auth functions -----------------
def do_login(username: str, password: str):
    if verify_user(username, password):
        st.session_state["auth_user"] = username
        st.success(f"Welcome, {username}!")
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()
    else:
        st.error("Invalid username or password.")

def do_logout():
    st.session_state["auth_user"] = None
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# ----------------- Sidebar (Backend health + logout if logged in) -----------------
with st.sidebar:
    st.header("⚙️ Backend")
    st.code(BACKEND, language="bash")
    if st.button("Health Check"):
        try:
            st.success(requests.get(f"{BACKEND}/health", timeout=6).json())
        except Exception as e:
            st.error(e)

    if st.session_state["auth_user"]:
        st.success(f"Logged in as {st.session_state['auth_user']}")
        st.button("Logout", on_click=do_logout)

# ----------------- Header -----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.title("🌍 Influmony App")
st.caption("Welcome to Influmony an user friendly Influencer Fit agent !!.")
st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Auth (Login + Signup) -----------------
if not st.session_state["auth_user"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔐 Access")
    st.markdown('<span class="badge">Secure Area</span>  Log in or create a test account to continue.', unsafe_allow_html=True)
    lc1, lc2 = st.columns(2)

    with lc1:
        st.markdown("### Login")
        u = st.text_input("Username", key="login_user", placeholder="Enter your username")
        p = st.text_input("Password", type="password", key="login_pwd", placeholder="Enter your password")
        if st.button("Login"):
            if not u or not p:
                st.warning("Enter username & password")
            else:
                do_login(u, p)

    with lc2:
        st.markdown("### Signup (local)")
        su = st.text_input("New username", key="signup_user", placeholder="Create a unique username")
        se = st.text_input("Email", key="signup_email", placeholder="name@company.com")
        sp = st.text_input("Password", type="password", key="signup_pwd", placeholder="Minimum 8 characters")
        if st.button("Create account"):
            try:
                add_user(su, se, sp)
                st.success("Account created. Please log in.")
            except Exception as e:
                st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ----------------- Campaign UI (only if logged in) -----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🧠 Describe your ")

# User and Company Name inputs
uc1, uc2 = st.columns(2)
with uc1:
    user_name = st.text_input(
        "Your Name",
        value=st.session_state.get("user_name", ""),
        placeholder="e.g., Yogendra A.",
        help="Your name will be used in the outreach messages"
    )
    if user_name:
        st.session_state["user_name"] = user_name
with uc2:
    company_name = st.text_input(
        "Company Name",
        value=st.session_state.get("company_name", ""),
        placeholder="e.g., Influmony Labs",
        help="Your company name will be used in the outreach messages"
    )
    if company_name:
        st.session_state["company_name"] = company_name

try:
    meta = requests.get(f"{BACKEND}/meta", timeout=8).json()
    platforms  = ["Any"] + meta.get("platforms", [])
    categories = ["Any"] + meta.get("categories", [])
    continents = ["Any"] + meta.get("continents", [])
    follower_min = meta.get("follower_min", 0)
    follower_max = int(meta.get("follower_max", 10_000_000))
except Exception:
    platforms, categories, continents = ["Any"], ["Any"], ["Any"]
    follower_min, follower_max = 0, 10_000_000

brief = st.text_area(
    "Brief",
    placeholder="Summarize the campaign goal, target audience, and tone (2–3 lines)."
)
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1])
with c1:
    continent = st.selectbox("Continent", options=continents, index=0)
with c2:
    platform = st.selectbox("Platform", options=platforms, index=0)
with c3:
    category = st.selectbox("Category", options=categories, index=0)
with c4:
    top_k = st.slider("Top K", 1, 10, 5)

max_followers = st.slider(
    "Max followers",
    int(follower_min), int(follower_max),
    min(int(follower_max*0.2), 1_000_000),
    step=int(max(1, (follower_max - follower_min) / 50))
)
st.markdown('</div>', unsafe_allow_html=True)

if st.button("🔍 Find Influencers", type="primary", use_container_width=True):
    if not brief.strip():
        st.error("Please enter a campaign brief.")
    elif not user_name.strip():
        st.error("Please enter your name.")
    elif not company_name.strip():
        st.error("Please enter your company name.")
    else:
        payload = {
            "brief": brief,
            "continent": None if continent == "Any" else continent,
            "platform": None if platform == "Any" else platform,
            "category": None if category == "Any" else category,
            "max_followers": int(max_followers),
            "top_k": int(top_k),
            "user_name": user_name,
            "company_name": company_name,
        }
        with st.spinner("Finding best influencers…"):
            try:
                r = requests.post(f"{BACKEND}/match", json=payload, timeout=60)
                if r.status_code >= 400:
                    try:
                        st.error(r.json().get("detail", r.text))
                    except Exception:
                        st.error(r.text)
                else:
                    data = r.json()
                    matches = data.get("matches", [])
                    if not matches:
                        st.warning(data.get("explanations", "No results"))
                        st.session_state["search_results"] = None
                    else:
                        st.success(data.get("explanations"))
                        st.session_state["search_results"] = matches
                        st.session_state["campaign_brief"] = brief
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        render_matches_table(matches, key="search")
                        st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(str(e))

# Display results and send email button if we have results
if st.session_state.get("search_results"):
    matches = st.session_state["search_results"]

    # Only show the dataframe if we just got results (not after email send)
    if "just_searched" not in st.session_state:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        render_matches_table(matches, key="saved")
        st.markdown('</div>', unsafe_allow_html=True)

    # Email sending section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📧 Send Outreach Emails")

    col1, col2 = st.columns([3, 1])
    with col1:
        email_subject = st.text_input(
            "Email Subject",
            value=f"Collaboration Opportunity - {st.session_state.get('campaign_brief', 'Campaign')[:50]}",
            key="email_subject",
            placeholder="Enter a concise and compelling subject"
        )
    with col2:
        st.write("")
        st.write("")

    st.info(f"📊 Ready to send emails to **{len(matches)}** top influencer(s)")

    if st.button("📨 Send Emails to All Influencers", type="primary", use_container_width=True):
        if not email_subject.strip():
            st.error("Please enter an email subject.")
        else:
            recipients = []
            for match in matches:
                recipients.append({
                    "name": match.get("person_name", ""),
                    "email": match.get("email", ""),
                    "message": match.get("outreach_message", "")
                })

            email_payload = {
                "recipients": recipients,
                "subject": email_subject,
                "campaign_brief": st.session_state.get("campaign_brief", "")
            }

            with st.spinner("Sending emails..."):
                try:
                    r = requests.post(f"{BACKEND}/send-emails", json=email_payload, timeout=120)
                    if r.status_code >= 400:
                        error_detail = r.json().get("detail", r.text) if r.headers.get("content-type") == "application/json" else r.text
                        st.error(f"❌ Failed to send emails: {error_detail}")
                    else:
                        result = r.json()

                        if result["success"] > 0:
                            st.success(f"✅ Successfully sent {result['success']} email(s)!")

                        if result["failed"] > 0:
                            st.warning(f"⚠️ Failed to send {result['failed']} email(s)")

                        with st.expander("📋 View Email Sending Details"):
                            for res in result["results"]:
                                if res["status"] == "sent":
                                    st.write(f"✅ {res['name']} ({res['email']})")
                                else:
                                    st.write(f"❌ {res['email']}: {res.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)
