from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import instaloader
import os
import time
from typing import Optional

app = FastAPI(
    title="InstaShuddh API",
    description="Check fake Instagram followers with Instaloader",
    version="1.0"
)

# Allow CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Instaloader
L = instaloader.Instaloader()

# Optional: Proxy Setup (uncomment if needed)
# L.context._session.proxies = {
#     'http': os.getenv('PROXY_URL'),
#     'https': os.getenv('PROXY_URL')
# }

@app.get("/")
def home():
    """Homepage with API instructions"""
    return {
        "message": "Welcome to InstaShuddh API!",
        "endpoint": "/check_fake?username={instagram_username}",
        "example": "https://insta-shuddh-api.onrender.com/check_fake?username=instagram"
    }

@app.get("/check_fake")
async def check_fake(username: str = Query(..., min_length=1)):
    """Check fake followers percentage for a given Instagram username"""
    try:
        # Login to Instagram (credentials from environment variables)
        if os.getenv('INSTA_USERNAME') and os.getenv('INSTA_PASSWORD'):
            L.login(os.getenv('INSTA_USERNAME'), os.getenv('INSTA_PASSWORD'))
            time.sleep(2)  # Avoid rate limiting

        # Fetch profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Calculate fake score (custom logic)
        fake_score = 0
        if profile.followees > 1000:
            fake_score += 30
        if profile.mediacount < 10:
            fake_score += 40
        if profile.followers < 500 and profile.followees > 800:
            fake_score += 50

        # Determine risk level
        risk = "✅ LOW RISK" if fake_score < 40 else \
               "⚠️ MEDIUM RISK" if fake_score < 70 else "❌ HIGH RISK"

        return {
            "username": username,
            "followers": profile.followers,
            "following": profile.followees,
            "posts": profile.mediacount,
            "fake_score": fake_score,
            "risk_level": risk,
            "message": "This is an estimate based on public data"
        }

    except instaloader.exceptions.ProfileNotExistsException:
        raise HTTPException(status_code=404, detail="Profile not found")
    except instaloader.exceptions.QueryReturnedBadRequestException:
        raise HTTPException(status_code=429, detail="Instagram rate limit exceeded. Try later.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For local testing (optional)
if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
