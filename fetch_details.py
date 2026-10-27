import html
import io
import json
import re
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
IMG = ROOT / "img"
GALLERY = IMG / "gallery"
POSTERS = IMG / "poster"
MAX_IMAGES = 8
THUMB_SIZE = 560
SIZE = 480
CATALOGS = ["catalog.json", "defender.json"]
SKIP = {("champion-class", "transformers"), ("defender", "transformers"), ("defender", "batman"), ("defender", "astral-rally")}


def fetch(url):
    url = url.replace("https://blokees.com/cdn/shop/files/", "https://cdn.shopify.com/s/files/1/0679/6538/6990/files/")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(8):
        try:
            return urllib.request.urlopen(req, timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"rate limited: {url}")


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


def entries():
    for catalog_name in CATALOGS:
        for kit in json.loads((ROOT / "data" / catalog_name).read_text(encoding="utf-8")):
            yield kit_code(kit).lower(), kit["handle"]
    for line in json.loads((ROOT / "data" / "lines.json").read_text(encoding="utf-8"))["lines"]:
        for fr in line["franchises"]:
            if (line["slug"], fr["slug"]) in SKIP:
                continue
            for item in fr["items"]:
                yield item["key"], item["handle"]


products = json.loads(fetch("https://blokees.com/en-us/products.json?limit=250"))["products"]
by_handle = {p["handle"]: p for p in products}
(ROOT / "data" / "blokees-store-products.json").write_text(json.dumps({"products": products}, ensure_ascii=False), encoding="utf-8")

GALLERY.mkdir(parents=True, exist_ok=True)
details_file = ROOT / "data" / "details.json"
details = json.loads(details_file.read_text(encoding="utf-8")) if details_file.exists() else {}

for count, (key, handle) in enumerate(entries(), 1):
    product = by_handle.get(handle)
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
    if count % 10 == 0:
        details_file.write_text(json.dumps(details, ensure_ascii=False, indent=1), encoding="utf-8")
details_file.write_text(json.dumps(details, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"details: {len(details)}")

posters_file = ROOT / "data" / "posters.json"
if posters_file.exists():
    for key, url in json.loads(posters_file.read_text(encoding="utf-8")).items():
        if any(POSTERS.glob(f"{key}-source.*")):
            continue
        ext = url.rsplit(".", 1)[-1].split("?")[0]
        (POSTERS / f"{key}-source.{ext}").write_bytes(fetch(url))
        print(f"poster {key}")
