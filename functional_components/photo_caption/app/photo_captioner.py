import requests
import sys


CAPTIONER_URL = "https://brendxnw-photo-captioner.hf.space"

def get_caption(image_path: str) -> str:
    with open(image_path, "rb") as f:
        r = requests.post(f"{CAPTIONER_URL}/caption",
                          files={"image": f},
                          timeout=60)
        r.raise_for_status()
    return r.json()["caption"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py path/to/image.jpg")
        exit(1)

    image_path = sys.argv[1]
    caption = get_caption(image_path)
    print("Caption:", caption)