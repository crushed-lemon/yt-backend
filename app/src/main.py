
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

AZURE_BLOB_URL = "https://ytstorage2.blob.core.windows.net"
AZURE_CONTAINER_NAME = 'yt-video-processed'
AZURE_BLOB_NAME = '<video_id>.mp4'

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(AZURE_BLOB_URL, credential)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

app = FastAPI()

# Allow frontend origin
origins = [
    "http://localhost:5137",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/video/{video_id}/manifest")
async def video_manifest(video_id: str):
    blobName = f"{video_id}/output.m3u8"
    print("Will try to get manifest" + blobName)
    try :
        blob = container_client.download_blob(blobName)
        return StreamingResponse(blob.chunks(), media_type="application/vnd.apple.mpegurl")
    except Exception as e :
        print(e)
        return PlainTextResponse(str(e), status_code=404)

@app.get("/video/{video_id}/chunk/{filename}")
async def video_chunk(video_id: str, filename: str):
    blobName = f"{video_id}/{filename}"
    print("Will try to get chunk " + blobName)
    try :
        blob = container_client.download_blob(blobName)
        return StreamingResponse(blob.chunks(), media_type="video/MP2T")
    except Exception as e :
        print(e)
        return PlainTextResponse(str(e), status_code=404)
