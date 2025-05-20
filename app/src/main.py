from fastapi import FastAPI

app = FastAPI()

# For health checks
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/home")
async def home():
    return {"videos": [
        {"id" : "video1", "video_name": "How to make lemon juice", "channel_name": "Best channel", "video_snapshot": "", "channel_icon": "", "video_link": ""},
        {"id" : "video2", "video_name": "The best lime sode center", "channel_name": "Best channel", "video_snapshot": "", "channel_icon": "", "video_link": ""},
    ]}

@app.get("/videos/:video_id")
async def videos(video_id: str):
    return {"message": "Hello " + video_id}