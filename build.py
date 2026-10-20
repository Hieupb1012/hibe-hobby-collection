import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "docs"
STORE = "https://blokees.com/en-us/products/"

HEAD = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-title" content="Hibe Hobby">
<meta name="theme-color" content="#0f1216">
<style>
:root { color-scheme: light; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
body { margin: 0; font: 14px/1.4 system-ui, -apple-system, "Segoe UI", sans-serif; }
img { max-width: 100%; }
[hidden] { display: none !important; }
</style>
"""

if DIST.exists():
    shutil.rmtree(DIST)
(DIST / "img" / "gallery").mkdir(parents=True)

catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
details = json.loads((ROOT / "data" / "details.json").read_text(encoding="utf-8"))
seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
firebase_file = ROOT / "data" / "firebase.json"
firebase = json.loads(firebase_file.read_text(encoding="utf-8")) if firebase_file.exists() else None

for kit in catalog:
    detail = details.get(str(kit["n"]), {})
    thumb = f"img/cc{kit['n']:02d}.webp"
    shutil.copy2(ROOT / thumb, DIST / thumb)
    extra = []
    for name in detail.get("gallery", [])[1:]:
        shutil.copy2(ROOT / "img" / "gallery" / name, DIST / "img" / "gallery" / name)
        extra.append(f"img/gallery/{name}")
    kit["img"] = thumb
    kit["gallery"] = [thumb, *extra]
    kit["desc"] = detail.get("desc", "")
    kit["url"] = STORE + kit.pop("handle")

shutil.copy2(ROOT / "icon" / "favicon-64.png", DIST / "favicon.png")
shutil.copy2(ROOT / "icon" / "apple-touch-icon-180.png", DIST / "apple-touch-icon.png")

template = (ROOT / "template.html").read_text(encoding="utf-8")
body = (
    template.replace("__FAVICON__", "favicon.png")
    .replace("__TOUCH_ICON__", "apple-touch-icon.png")
    .replace("__CATALOG__", json.dumps(catalog, ensure_ascii=False))
    .replace("__SEED__", json.dumps(seed, ensure_ascii=False))
    .replace("__FIREBASE__", json.dumps(firebase, ensure_ascii=False))
)
(DIST / "index.html").write_text(HEAD + body + "\n</html>\n", encoding="utf-8")
(DIST / ".nojekyll").write_text("", encoding="utf-8")

size = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
print(f"docs: {len(catalog)} kits, {size // 1024} KB")
