import logging

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from azure.storage.blob import BlobClient
from azure.identity import DefaultAzureCredential
import io

AZURE_BLOB_URL = "https://ytstorage2.blob.core.windows.net"
AZURE_CONTAINER_NAME = 'yt-video-processed'
AZURE_BLOB_NAME = '<video_id>.mp4'

app = FastAPI()

# Allow frontend origin
origins = [
    "http://localhost:5137"
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

@app.get("/videos/{video_id}")
async def videos(request: Request, video_id: str):
    blobClient = getBlobClient(video_id)

    range_header = request.headers.get("Range")
    if not range_header:
        return PlainTextResponse(content="Range header not found.", status_code=400)

    print(blobClient.get_blob_properties())
    video_total_size = blobClient.get_blob_properties().size
    offset, end, length = getOffsetAndLength(range_header, video_total_size)

    blob_stream = blobClient.download_blob(offset=offset, length=length).readall()
    response_headers = getResponseHeaders(offset, end, video_total_size, length)

    return StreamingResponse(io.BytesIO(blob_stream), status_code=206, headers=response_headers)

def getBlobClient(video_id: str):
    blob_name = AZURE_BLOB_NAME.replace("<video_id>", video_id)
    credential = DefaultAzureCredential()
    print(blob_name)
    return BlobClient(account_url=AZURE_BLOB_URL,
                      container_name=AZURE_CONTAINER_NAME,
                      blob_name=blob_name,
                      credential=credential)

def getOffsetAndLength(range_header, video_total_size):
    range = range_header.strip().lower().replace("bytes=","")
    start_str, end_str = range.split("-")
    start = int(start_str)
    end = int(end_str) if end_str else video_total_size - 1
    length = end - start + 1
    return start, end, length

def getResponseHeaders(start, end, total_size, length):
    return {
        "Content-Range": f"bytes {start}-{end}/{total_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
        "Content-Type": "video/mp4"
    }
