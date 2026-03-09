import os
import os.path

os.environ["DOCKER_ENV"] = "True"

from fastapi import FastAPI
from fastapi.responses import FileResponse
import smog_sim

app = FastAPI()


@app.get("/")
def read_root():
    gif_filename = "smog_symulacja.gif"

    if not os.path.exists(gif_filename):
        print("\n[INFO] Brak gotowego pliku. Rozpoczynam generowanie GIF-a.")
        print("[INFO] To może potrwać od 30 do 90 sekund. PROSZĘ CZEKAĆ...\n")
        smog_sim.main()
        print("\n[INFO] Sukces! Plik wygenerowany.")

    return FileResponse(gif_filename, media_type="image/gif")