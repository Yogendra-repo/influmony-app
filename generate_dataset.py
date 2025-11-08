# generate_dataset.py
import pandas as pd
import numpy as np
import random
from pathlib import Path

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)

# Number of influencers to generate
N = 1000  

# Possible attribute values
platforms = ["Instagram", "YouTube", "TikTok", "Twitter", "LinkedIn"]
countries = ["USA", "India", "UK", "Brazil", "Germany", "Canada", "France", "Japan", "Australia", "Italy", "Spain", "Mexico", "UAE", "Singapore", "Netherlands"]
categories = ["fashion", "tech", "fitness", "food", "travel", "beauty", "music", "gaming", "education", "finance"]

first_names = ["Alex","Jordan","Taylor","Chris","Jamie","Casey","Morgan","Cameron","Sam","Avery","Riley","Dakota","Rowan","Harper","Reese","Peyton","Devin","Skyler","Elliot"]
last_names  = ["Smith","Johnson","Brown","Lee","Martinez","Davis","Garcia","Miller","Wilson","Anderson","Moore","Lopez","Clark","Lewis","Walker","Hall","Young","King","Green"]

# Function to generate random influencer name and email
def make_person():
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    username = name.lower().replace(" ", ".")
    email_domain = random.choice(["gmail.com", "outlook.com", "yahoo.com", "influencerhub.io"])
    email = f"{username}@{email_domain}"
    return name, email

# Generate dataset
rows = []
for _ in range(N):
    name, email = make_person()
    platform = random.choices(platforms, weights=[34,26,22,10,8], k=1)[0]
    country = random.choice(countries)
    category = random.choice(categories)

    # Generate followers (bounded lognormal)
    followers = int(np.clip(np.random.lognormal(mean=12, sigma=0.7), 1e4, 2.5e7))

    hashtags = " ".join([f"#{category}", "#influencer", "#trending"])

    rows.append({
        "person_name": name,
        "email": email,
        "followers": followers,
        "platform": platform,
        "category": category,
        "country": country,
        "hashtags": hashtags
    })

# Save to CSV
df = pd.DataFrame(rows)
Path("data").mkdir(parents=True, exist_ok=True)
output_path = Path("data/influencers_top1000.csv")
df.to_csv(output_path, index=False)

print(f"✅ Generated {len(df)} influencer records -> {output_path}")
