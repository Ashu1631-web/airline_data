import os
import requests

LOGO_URLS = {
    "IndiGo": "https://upload.wikimedia.org/wikipedia/commons/5/5d/IndiGo_Logo.svg",
    "SpiceJet": "https://upload.wikimedia.org/wikipedia/commons/5/5c/SpiceJet_logo.svg",
    "Air India": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Air_India_Logo.svg",
    "GoAir": "https://upload.wikimedia.org/wikipedia/commons/7/7b/GoAir_logo.svg",
}

def fetch_logo(airline):
    folder = "airline_logos"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"{airline}.png")

    if airline in LOGO_URLS and not os.path.exists(file_path):
        url = LOGO_URLS[airline]
        r = requests.get(url)

        if r.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(r.content)

    return file_path
