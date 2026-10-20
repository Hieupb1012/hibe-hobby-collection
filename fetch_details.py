import html
import io
import json
import re
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
GALLERY = ROOT / "img" / "gallery"
MAX_IMAGES = 8
SIZE = 480


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req).read()


def plain_text(body):
    text = re.sub(r"<br\s*/?>|</p>", "\n", body or "")
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


products = json.loads(fetch("https://blokees.com/en-us/products.json?limit=250"))["products"]
by_handle = {p["handle"]: p for p in products}
(ROOT / "data" / "blokees-store-products.json").write_text(json.dumps({"products": products}, ensure_ascii=False), encoding="utf-8")

catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
GALLERY.mkdir(parents=True, exist_ok=True)
details = {}
for kit in catalog:
    product = by_handle.get(kit["handle"])
    if not product:
        print(f"CC{kit['n']:02d}: not found on store")
        continue
    files = []
    for i, image in enumerate(product["images"][:MAX_IMAGES], 1):
        name = f"cc{kit['n']:02d}-{i}.webp"
        target = GALLERY / name
        if not target.exists():
            im = Image.open(io.BytesIO(fetch(image["src"]))).convert("RGBA")
            im.thumbnail((SIZE, SIZE))
            im.save(target, "WEBP", quality=70)
        files.append(name)
    details[str(kit["n"])] = {"desc": plain_text(product["body_html"]), "gallery": files}
    print(f"CC{kit['n']:02d}: {len(files)} images")

(ROOT / "data" / "details.json").write_text(json.dumps(details, ensure_ascii=False, indent=1), encoding="utf-8")
