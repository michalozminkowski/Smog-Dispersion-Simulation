import os
import os.path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from app import smog_sim

os.environ["DOCKER_ENV"] = "True"


@asynccontextmanager
async def lifespan(app: FastAPI):
    gif_filename = "smog_symulacja.gif"

    if not os.path.exists(gif_filename):
        print("[INFO] Start serwera: Rozpoczynam generowanie mapy smogu...")
        smog_sim.main()
        print("[INFO] Start serwera: Plik wygenerowany pomyślnie!")

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smog Dispersion Simulation</title>
        <style>
            body {
                background-color: #121212; /* Ciemne tło jak z profesjonalnego dasha */
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            img {
                width: 90vw; /* Rozciąga obraz na 90% szerokości okna przeglądarki */
                max-width: 1400px; /* Maksymalna szerokość na wielkich monitorach */
                box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.8); /* Lekki cień */
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <img src="/smog_symulacja.gif" alt="Smog Simulation">
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/smog_symulacja.gif")
def get_gif():
    return FileResponse("smog_symulacja.gif", media_type="image/gif")