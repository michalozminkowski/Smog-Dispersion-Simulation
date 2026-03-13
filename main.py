import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

os.environ["DOCKER_ENV"] = "True"

app = FastAPI()

@app.get("/")
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smog Dispersion Simulation</title>
        <style>
            body {
                background-color: #121212;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            img {
                width: 90vw;
                max-width: 1400px;
                box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.8);
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
    # Serwer po prostu podaje plik, który wygenerował się wcześniej na GitHubie
    return FileResponse("smog_symulacja.gif", media_type="image/gif")