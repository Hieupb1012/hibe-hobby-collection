import html
import io
import json
import re
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
IMG = ROOT / "img"
GALLERY = IMG / "gallery"
MAX_IMAGES = 8
THUMB_SIZE = 560
SIZE = 480
CATALOGS = ["catalog.json", "defender.json"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req).read()


def plain_text(body):
    text = re.sub(r"<br\s*/?>|</p>", "\n", body or "")
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def kit_code(kit):
    if "code" in kit:
        return kit["code"]
    return ("CH" if kit["line"] == "champion" else "CC") + f"{kit['n']:02d}"


def save_image(url, target, size, quality):
    im = Image.open(io.BytesIO(fetch(url))).convert("RGBA")
    im.thumbnail((size, size))
    im.save(target, "WEBP", quality=quality)


products = json.loads(fetch("https://blokees.com/en-us/products.json?limit=250"))["products"]
by_handle = {p["handle"]: p for p in products}
(ROOT / "data" / "blokees-store-products.json").write_text(json.dumps({"products": products}, ensure_ascii=False), encoding="utf-8")

GALLERY.mkdir(parents=True, exist_ok=True)
details_file = ROOT / "data" / "details.json"
details = json.loads(details_file.read_text(encoding="utf-8")) if details_file.exists() else {}

for catalog_name in CATALOGS:
    for kit in json.loads((ROOT / "data" / catalog_name).read_text(encoding="utf-8")):
        key = kit_code(kit).lower()
        product = by_handle.get(kit["handle"])
        if not product:
            print(f"{key}: not found on store")
            continue
        images = product["images"][:MAX_IMAGES]
        thumb = IMG / f"{key}.webp"
        if not thumb.exists() and images:
            save_image(images[0]["src"], thumb, THUMB_SIZE, 82)
        files = []
        for i, image in enumerate(images, 1):
            name = f"{key}-{i}.webp"
            if i > 1 and not (GALLERY / name).exists():
                save_image(image["src"], GALLERY / name, SIZE, 70)
            files.append(name)
        details[key] = {"desc": plain_text(product["body_html"]), "gallery": files}
        print(f"{key}: {len(files)} images")

details_file.write_text(json.dumps(details, ensure_ascii=False, indent=1), encoding="utf-8")
