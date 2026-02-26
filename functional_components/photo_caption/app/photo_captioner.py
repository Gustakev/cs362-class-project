import requests

CAPTIONER_URL = "https://brendxnw-photo-captioner.hf.space"

def get_caption(image_path: str) -> str:
    with open(image_path, "rb") as f:
        r = requests.post(f"{CAPTIONER_URL}/caption",
                          files={"image": f},
                          timeout=60)
        r.raise_for_status()
    return r.json()["caption"]