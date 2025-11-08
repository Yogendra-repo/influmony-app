# Influencer Fit Agent (Software 3.0)

Find & rank micro-influencers for SMB campaigns using embeddings + multi-factor scoring.
Tech: FastAPI, Streamlit, sentence-transformers, FAISS (optional), Gemini (optional).

## ✨ Features

- 🔍 **Smart Search**: Find influencers using semantic search and multi-factor scoring
- 📊 **Top Influencers**: Get ranked results based on relevance and follower fit
- 🤖 **AI Outreach**: Generate personalized messages with Gemini AI
- 📧 **Email Campaign**: Send bulk emails to selected influencers directly from the app
- 🔐 **User Authentication**: Secure login system with bcrypt encryption
- 🎨 **Modern UI**: Beautiful glass-morphism design with Streamlit

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials:
# - GEMINI_API_KEY (optional - for AI outreach generation)
# - SMTP_EMAIL and SMTP_PASSWORD (required - for sending emails)
```

## 📧 Email Configuration

To send emails to influencers, you need to configure SMTP settings in `.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**For Gmail users**: Create an App Password at https://myaccount.google.com/apppasswords

📖 **Detailed setup guide**: See [EMAIL_SETUP.md](EMAIL_SETUP.md)

## Run
Terminal 1:
```bash
uvicorn main:app --reload
```

Terminal 2:
```bash
streamlit run app.py
```

## API
POST /match
```json
{
  "brief":"Men's grooming in India",
  "country":"India",
  "niche":"mens_grooming",
  "max_followers":50000,
  "top_k":3
}
```

## Dataset
Edit `./data/influencers_sample.csv` or replace with your own.
Required columns:
name, platform, followers, engagement_rate, bio, hashtags, est_post_cost, country, niche
