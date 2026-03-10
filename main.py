import os
import os.path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from app import smog_sim

os.environ["DOCKER_ENV"] = "True"


@asynccontextmanager
async def lifespan(app: FastAPI):
    gif_filename = "smog_symulacja.gif"

    if not os.path.exists(gif_filename):
        smog_sim.main()

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return FileResponse("smog_symulacja.gif", media_type="image/gif")