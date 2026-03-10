import os
import os.path

os.environ["DOCKER_ENV"] = "True"

from fastapi import FastAPI
from fastapi.responses import FileResponse
from app import smog_sim

app = FastAPI()

@app.get("/")
def read_root():
    gif_filename = "smog_symulacja.gif"

    if not os.path.exists(gif_filename):
        smog_sim.main()

    return FileResponse(gif_filename, media_type="image/gif")