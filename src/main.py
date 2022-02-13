from typing import Optional

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, Response
import uuid
from src.resample_mp3 import Mp3Resampler
from io import BytesIO

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/uploadmp3/")
async def create_upload_file(file: UploadFile):
    path = f"files/{str(uuid.uuid4())}.mp3"
    file_new = open(path, "wb")
    file_new.write(file.file.read())
    file_new.close()

    return {"filename": path}


@app.get("/get_file/{file_path}")
def get_file(file_path: str):
    file = open(f"files/{file_path}", "rb")
    resampler = Mp3Resampler(
        input_file=BytesIO(file.read()),
        expected_sampling_rate=44100,
        output_file_path=None,
    )
    file.close()
    sampled_file = resampler.resample_mp3_file()

    return Response(content=sampled_file.read(), media_type="audio/mpeg")
