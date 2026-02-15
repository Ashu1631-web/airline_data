import os
import requests

LOGO_URLS = {
    "IndiGo": "https://logos-world.net/wp-content/uploads/2023/01/IndiGo-Logo.png",
    "SpiceJet": "https://logos-world.net/wp-content/uploads/2023/01/SpiceJet-Logo.png",
    "Air India": "https://logos-world.net/wp-content/uploads/2023/01/Air-India-Logo.png",
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
