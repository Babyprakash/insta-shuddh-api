from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import instaloader

app = FastAPI()

# Allow CORS (Blogger से requests आने के लिए)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/check_fake")
async def check_fake(username: str = Query(...)):
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        fake_score = 0
        if profile.followees > 1000:
            fake_score += 30
        if profile.mediacount < 10:
            fake_score += 40
        if profile.followers < 500 and profile.followees > 800:
            fake_score += 50
        return {
            "username": username,
            "followers": profile.followers,
            "following": profile.followees,
            "posts": profile.mediacount,
            "fake_score": fake_score
        }
    except Exception as e:
        return {"error": str(e)}
