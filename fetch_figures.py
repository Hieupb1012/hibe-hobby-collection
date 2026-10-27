import io
import json
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
OUT = ROOT / "img" / "fig"
SIZE = 480


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(8):
        try:
            return urllib.request.urlopen(req, timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"rate limited: {url}")


series = {k["code"].lower(): k for k in json.loads((ROOT / "data" / "defender.json").read_text(encoding="utf-8"))}
products = {p["handle"]: p for p in json.loads((ROOT / "data" / "blokees-store-products.json").read_text(encoding="utf-8"))["products"]}
figures = json.loads((ROOT / "data" / "figures.json").read_text(encoding="utf-8"))

OUT.mkdir(parents=True, exist_ok=True)
for key, items in figures.items():
    gallery = products[series[key]["handle"]]["images"]
    for i, fig in enumerate(items, 1):
        target = OUT / f"{key}-{i:02d}.webp"
        if target.exists():
            continue
        src = fig["img"]
        if src.startswith("gallery:"):
            src = gallery[int(src.split(":")[1]) - 1]["src"]
        im = Image.open(io.BytesIO(fetch(src))).convert("RGBA")
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
        im.thumbnail((SIZE, SIZE))
        im.save(target, "WEBP", quality=78)
    print(f"{key}: {len(items)} figures")
