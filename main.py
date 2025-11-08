# main.py
import os
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from starlette.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Optional Gemini (for outreach). Safe to omit if no key.
try:
    from google import genai  # google-genai >= 0.5.x
except Exception:
    genai = None

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH", "./data/influencers_top1000.csv")
EMB_MODEL = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

app = FastAPI(
    title="🌍 Influencer Fit Agent (CSV: person_name,email,followers,platform,category,country,hashtags)"
)

# CORS so Streamlit (localhost or deployed) can call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production (e.g., to your frontend host)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    brief: str
    continent: Optional[str] = None
    platform: Optional[str] = None
    category: Optional[str] = None
    max_followers: Optional[int] = 1_000_000
    top_k: Optional[int] = 5
    user_name: Optional[str] = None
    company_name: Optional[str] = None

class EmailRequest(BaseModel):
    recipients: List[Dict[str, str]]  # List of {"name": "...", "email": "...", "message": "..."}
    subject: str
    campaign_brief: Optional[str] = None

# ---- Load model & dataset once ----
_model = SentenceTransformer(EMB_MODEL)
_df: Optional[pd.DataFrame] = None
_embeddings: Optional[np.ndarray] = None  # shape: (N, D) float32

_CONTINENT_MAP = {
    "usa":"North America","united states":"North America","canada":"North America","mexico":"North America",
    "brazil":"South America","argentina":"South America","chile":"South America","colombia":"South America","peru":"South America",
    "uk":"Europe","united kingdom":"Europe","england":"Europe","ireland":"Europe","france":"Europe","germany":"Europe",
    "italy":"Europe","spain":"Europe","netherlands":"Europe","belgium":"Europe","portugal":"Europe","sweden":"Europe",
    "norway":"Europe","denmark":"Europe","poland":"Europe",
    "india":"Asia","japan":"Asia","singapore":"Asia","uae":"Asia","united arab emirates":"Asia","china":"Asia","south korea":"Asia",
    "indonesia":"Asia","malaysia":"Asia",
    "australia":"Oceania","new zealand":"Oceania",
    "south africa":"Africa","nigeria":"Africa","egypt":"Africa","kenya":"Africa","morocco":"Africa",
}

def _country_to_continent(country: str) -> str:
    if not isinstance(country, str):
        return "Other"
    return _CONTINENT_MAP.get(country.strip().lower(), "Other")

def _build_texts(df: pd.DataFrame) -> List[str]:
    # text used for embeddings (no bio/engagement in this schema)
    # Make sure to handle NaNs cleanly
    cols = {c: df.get(c, pd.Series(dtype=str)).fillna("").astype(str)
            for c in ["category", "hashtags", "platform"]}
    texts = (cols["category"] + " " + cols["hashtags"] + " " + cols["platform"]).tolist()
    # Edge-case: empty strings (still OK for encoder)
    return texts

def _load_dataset():
    global _df, _embeddings
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}.")

    df = pd.read_csv(DATA_PATH)

    # Required columns per your generator
    required = {"person_name", "email", "followers", "platform", "category", "country", "hashtags"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")

    # Clean/standardize dtypes
    df["person_name"] = df["person_name"].fillna("").astype(str)
    df["email"] = df["email"].fillna("").astype(str)
    df["platform"] = df["platform"].fillna("").astype(str)
    df["category"] = df["category"].fillna("").astype(str)
    df["country"] = df["country"].fillna("").astype(str)
    df["hashtags"] = df["hashtags"].fillna("").astype(str)

    # followers may come as float/string; coerce to int
    df["followers"] = pd.to_numeric(df["followers"], errors="coerce").fillna(0).astype(int)

    # derive continent
    df["continent"] = df["country"].apply(_country_to_continent)

    # Build texts for embedding
    texts = _build_texts(df)

    # Encode to float32 (saves memory, plenty precise for cosine)
    emb = _model.encode(texts, normalize_embeddings=True)
    emb = np.asarray(emb, dtype=np.float32)

    _df = df.reset_index(drop=True)
    _embeddings = emb
    print(f"✅ Loaded {len(df)} rows from {DATA_PATH}")

_load_dataset()

def _gemini_client():
    if not GEMINI_API_KEY or genai is None:
        return None
    try:
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        return None

# ---- Utility endpoints ----
@app.get("/health")
def health():
    return {
        "status": "ok",
        "rows": int(_df.shape[0]) if _df is not None else 0,
        "dataset": DATA_PATH,
        "embeddings_shape": None if _embeddings is None else list(_embeddings.shape),
        "model": EMB_MODEL,
    }

@app.get("/meta")
def meta():
    platforms = sorted(map(str, _df["platform"].dropna().unique().tolist()))
    categories = sorted(map(str, _df["category"].dropna().unique().tolist()))
    continents = sorted(map(str, _df["continent"].dropna().unique().tolist()))
    return {
        "platforms": platforms,
        "categories": categories,
        "continents": continents,
        "follower_min": int(_df["followers"].min()),
        "follower_max": int(_df["followers"].max()),
    }

# ---- Scoring (similarity + follower fit) ----
def _compute_scores(brief, continent, platform, category, max_followers, top_k):
    df = _df
    mask = np.ones(df.shape[0], dtype=bool)
    if continent:
        mask &= (df["continent"].values == continent)
    if platform:
        mask &= (df["platform"].values == platform)
    if category:
        mask &= (df["category"].values == category)

    idxs = np.nonzero(mask)[0]
    if len(idxs) == 0:
        return []

    # semantic similarity
    q_emb = _model.encode([brief], normalize_embeddings=True)[0].astype(np.float32)
    sim = np.dot(_embeddings[idxs], q_emb)  # cosine-like since normalized

    # follower fit: prefer <= max_followers
    foll = df.loc[idxs, "followers"].astype(float).to_numpy()
    if max_followers and max_followers > 0:
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.divide(max_followers, foll, out=np.full_like(foll, 1.0, dtype=float), where=foll > 0)
        foll_score = np.where(foll <= max_followers, 1.0, np.clip(ratio, 0.1, 1.0))
    else:
        foll_score = np.ones_like(foll, dtype=float)

    # final score: emphasize semantic match
    score = 0.75 * sim + 0.25 * foll_score

    k = int(min(max(1, top_k or 5), score.size))
    top_local = np.argsort(-score)[:k]
    sel = idxs[top_local]

    top = df.loc[sel].copy()
    top["FitScore"] = (score[top_local] * 100).round(2)
    top["_relevance"] = (sim[top_local] * 100).round(2)
    top["_follower_fit"] = (foll_score[top_local] * 100).round(2)
    return top

def _outreach(brief: str, row: Dict[str, Any], user_name: str = None, company_name: str = None) -> str:
    client = _gemini_client()
    
    # Use provided names or defaults
    sender_name = user_name if user_name else "[Your Name]"
    sender_company = company_name if company_name else "[Your Company]"
    
    if client:
        prompt = f"""
Write a short promotional outreach email (<120 words), warm and professional.
Use the brand brief, mention platform & category, and end with a clear CTA.
The email should be from {sender_name} representing {sender_company}.

Brief: {brief}

Sender:
Name: {sender_name}
Company: {sender_company}

Influencer:
Name: {row['person_name']}
Email: {row['email']}
Platform: {row['platform']}
Followers: {row['followers']}
Country: {row['country']} (Continent: {row.get('continent','')})
Category: {row['category']}
Hashtags: {row['hashtags']}
"""
        try:
            # Try modern style
            resp = None
            if hasattr(client, "responses"):
                resp = client.responses.generate(model=GEMINI_MODEL, input=prompt)
                text = getattr(resp, "output_text", None)
                if text:
                    return text.strip()
            # Try legacy style
            if hasattr(client, "models"):
                resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
                text = getattr(resp, "text", None)
                if text:
                    return text.strip()
        except Exception:
            pass
    # Fallback
    return (
        f"Hi {row['person_name']},\n\n"
        f"I'm {sender_name} from {sender_company}. We love your {row['category']} content on {row['platform']} "
        f"and think you'd be a great fit for our upcoming campaign.\n\n"
        f"Can we share the brief and timelines?\n\n"
        f"Best regards,\n{sender_name}\n{sender_company}"
    )

@app.post("/match")
def match(req: MatchRequest):
    if not req.brief or not req.brief.strip():
        raise HTTPException(400, "Brief is required.")

    top = _compute_scores(
        req.brief, req.continent, req.platform, req.category, req.max_followers, req.top_k
    )
    if len(top) == 0:
        return {"matches": [], "explanations": "No influencers found for those filters."}

    results = []
    for _, r in top.iterrows():
        row_dict = r.to_dict()
        results.append({
            "person_name": r["person_name"],
            "email": r["email"],
            "platform": r["platform"],
            "followers": int(r["followers"]),
            "country": r["country"],
            "continent": r["continent"],
            "category": r["category"],
            "hashtags": r["hashtags"],
            "fit_score": float(r["FitScore"]),
            "subscores": {
                "relevance": float(r["_relevance"]),
                "follower_fit": float(r["_follower_fit"]),
            },
            "outreach_message": _outreach(req.brief, row_dict, req.user_name, req.company_name),
        })
    return {"matches": results, "explanations": "Ranked by semantic relevance + follower fit."}

def _send_email(recipient_email: str, recipient_name: str, subject: str, message: str) -> bool:
    """Send email to a single recipient"""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise HTTPException(500, "Email credentials not configured. Please set SMTP_EMAIL and SMTP_PASSWORD in .env")
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = subject
        
        # Create HTML and plain text versions
        text = message
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #2563EB;">Hello {recipient_name}!</h2>
              <div style="white-space: pre-wrap;">{message}</div>
              <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
              <p style="color: #666; font-size: 12px;">
                This is an automated outreach message from Influmony.
              </p>
            </div>
          </body>
        </html>
        """
        
        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {str(e)}")
        raise HTTPException(500, f"Failed to send email: {str(e)}")

@app.post("/send-emails")
def send_emails(req: EmailRequest):
    """Send emails to multiple influencers"""
    if not req.recipients:
        raise HTTPException(400, "No recipients provided")
    
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise HTTPException(500, "Email service not configured. Please set SMTP_EMAIL and SMTP_PASSWORD in environment variables.")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for recipient in req.recipients:
        try:
            name = recipient.get("name", "")
            email = recipient.get("email", "")
            message = recipient.get("message", "")
            
            if not email or not message:
                results.append({
                    "email": email or "unknown",
                    "status": "failed",
                    "error": "Missing email or message"
                })
                failed_count += 1
                continue
            
            _send_email(email, name, req.subject, message)
            results.append({
                "email": email,
                "name": name,
                "status": "sent"
            })
            success_count += 1
            
        except Exception as e:
            results.append({
                "email": recipient.get("email", "unknown"),
                "status": "failed",
                "error": str(e)
            })
            failed_count += 1
    
    return {
        "total": len(req.recipients),
        "success": success_count,
        "failed": failed_count,
        "results": results
    }

