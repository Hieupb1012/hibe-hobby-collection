import html
import json
import shutil
from pathlib import Path

from PIL import Image

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

DEFENDER = json.loads((Path(__file__).parent / "data" / "defender.json").read_text(encoding="utf-8"))
FRANCHISES = [
    ("defender-transformers", "transformers", "Transformers", "Defender Version", "Tìm series hoặc mã (vd: Battle Stars, TF08)"),
    ("defender-batman", "batman", "Batman", "DC Defender Version", "Tìm series hoặc mã (vd: Arkham, DC03)"),
    ("defender-astral-rally", "astral-rally", "Astral Rally", "Defender Version", "Tìm series hoặc mã (vd: First Light, AR01)"),
]


def series_of(line):
    return sorted((s for s in DEFENDER if s["line"] == line), key=lambda s: s["code"])


def latest_of(line):
    return max(series_of(line), key=lambda s: s["date"])["code"].lower()


def series_codes(line):
    return ", ".join(s["code"] for s in series_of(line))


CC_FILMS = ["Rise of the Beasts", "Transformers (2007)", "Transformers One", "Dark of the Moon", "Bumblebee (2018)"]

CC_SCOPE = """    <h2>Phạm vi danh sách</h2>
    <p>Chỉ gồm các kit đang có trên store quốc tế blokees.com/en-us, đối chiếu ngày 20/10/2026. Đã loại các bản chỉ phát hành nội địa Trung Quốc:</p>
    <ul>
      <li>Các bộ combo A–F (kèm cảnh chiến đấu, diorama).</li>
      <li>Biến thể EX Edition, Damage Limited, Luminous Night, Frozen Limited.</li>
      <li>Bộ giới hạn Universal Studios Beijing.</li>
      <li>Bản mẫu chưa sơn và bản trắng từ cuộc thi BFC.</li>
      <li>EX Elite Bumblebee (giới hạn 5.000 hộp, chỉ bán theo sự kiện).</li>
    </ul>
    <p>Từ số 26, Blokees đổi tên dòng này thành Champion Class nhưng vẫn đánh số tiếp. Các số 30–31 đã được công bố nhưng chưa lên store quốc tế, nên chưa có trong danh sách.</p>
    <p>Ngày ra mắt là tháng kit lên store quốc tế. Ở Trung Quốc, nhiều kit ra sớm hơn vài tháng.</p>"""


def defender_scope(series):
    return f"""    <h2>Phạm vi danh sách</h2>
    <p>Mỗi thẻ là một series hộp mù Defender Version đang bán trên store quốc tế blokees.com/en-us. Hiện mới có {series}. Các series khác sẽ được thêm sau.</p>
    <p>Ngày ra mắt là tháng series lên store quốc tế.</p>"""


def checklist(path, crumb, title, h1, eyebrow, lede, hint, page, lines):
    return {"kind": "checklist", "path": path, "crumb": crumb, "title": title, "h1": h1, "eyebrow": eyebrow,
            "lede": lede, "hint": hint, "page": page, "lines": lines}


PAGES = [
    {"kind": "hub", "path": "", "crumb": "Hibe Hobby", "title": "Hibe Hobby's Collection", "brand": True,
     "eyebrow": "Blokees · Bản quốc tế", "h1": "Hibe Hobby's<br>Collection",
     "lede": "Bộ sưu tập Blokees của Hibe Hobby. Chọn một dòng sản phẩm để xem checklist.",
     "cards": [
         {"href": "champion-class/", "kicker": "Model kit lắp ráp", "title": "Champion Class", "desc": "Gồm Classic Class 01–25 và các số Champion Class nối tiếp.", "lines": ["classic", "champion"], "img": "cc01"},
         {"href": "defender/", "kicker": "Hộp mù theo series", "title": "Defender", "desc": "Transformers, Batman và Astral Rally.", "lines": ["defender-transformers", "defender-batman", "defender-astral-rally"], "img": latest_of("defender-transformers")},
     ]},
    {"kind": "hub", "path": "champion-class/", "crumb": "Champion Class", "title": "Champion Class · Hibe Hobby",
     "eyebrow": "Hibe Hobby's Collection", "h1": "Champion Class",
     "lede": "Dòng model kit lắp ráp Champion Class (trước đây là Classic Class) của Blokees.",
     "cards": [
         {"href": "transformers/", "kicker": "CC01–CC25 · CH26+", "title": "Transformers", "desc": "Rise of the Beasts, Transformers One, Dark of the Moon, Bumblebee...", "lines": ["classic", "champion"], "img": "cc01"},
     ]},
    checklist("champion-class/transformers/", "Transformers", "Champion Class Transformers · Hibe Hobby", "Champion Class<br>Transformers",
              "Hibe Hobby's Collection · Blokees × Transformers",
              "Đủ 25 kit Classic Class từ CC01 đến CC25 đang bán quốc tế trên store chính thức của Blokees, cộng các số tiếp theo đã đổi tên thành Champion Class. Bấm vào ảnh hoặc tên để xem chi tiết. Tick ô \"Đã có\" và \"Đã làm video\" để theo dõi bộ sưu tập.",
              "Tìm nhân vật, phim hoặc mã (vd: Megatron, One, CC21)",
              {"films": CC_FILMS, "primaryLines": ["classic"], "unit": "kit Classic Class",
               "secondary": {"line": "champion", "label": "Champion Class"},
               "groups": [*({"title": f, "line": "classic", "film": f, "range": True} for f in CC_FILMS),
                          {"title": "Champion Class · nối tiếp từ số 26", "line": "champion",
                           "note": "Cùng dòng sản phẩm, cùng kích thước và hệ đánh số, chỉ đổi tên từ số 26. Không tính vào tiến độ 25 kit Classic Class ở trên."}],
               "noResultHint": "Thử tên nhân vật (Optimus), tên phim (One) hoặc mã (CC21).", "scope": CC_SCOPE},
              ["classic", "champion"]),
    {"kind": "hub", "path": "defender/", "crumb": "Defender", "title": "Defender · Hibe Hobby",
     "eyebrow": "Hibe Hobby's Collection", "h1": "Defender",
     "lede": "Các series hộp mù Defender Version của Blokees, chia theo thương hiệu.",
     "cards": [
         *({"href": f"{slug}/", "kicker": kicker, "title": label, "desc": f"{series_codes(line)}.", "lines": [line], "img": latest_of(line)}
           for line, slug, label, kicker, _ in FRANCHISES),
     ]},
]

for line, slug, label, _, hint in FRANCHISES:
    series = series_codes(line)
    PAGES.append(checklist(
        f"defender/{slug}/", label, f"Defender {label} · Hibe Hobby", f"Defender<br>{label}",
        "Hibe Hobby's Collection · Blokees Defender Version",
        f"Các series hộp mù {label} Defender Version đang bán quốc tế. Bấm vào ảnh hoặc tên để xem chi tiết. Tick ô \"Đã có\" và \"Đã làm video\" để theo dõi bộ sưu tập.",
        hint,
        {"films": [], "primaryLines": [line], "unit": "series", "secondary": None,
         "groups": [{"title": f"{label} Defender Version", "line": line}],
         "noResultHint": "Thử tên series hoặc mã series.", "scope": defender_scope(series)},
        [line]))

SERIES_FRANCHISE = {"defender-transformers": "transformers", "defender-batman": "batman", "defender-astral-rally": "astral-rally"}
FIGURE_SCOPE = """    <h2>Phạm vi danh sách</h2>
    <p>Danh sách nhân vật, ảnh và tỉ lệ lấy từ trang sản phẩm chính thức trên store quốc tế blokees.com/en-us. Một hộp đủ (display box) có 12 hộp mù, không trùng nhân vật thường.</p>
    <p>Các bản hiếm không có trong bảng nhân vật của store (Special Armor Type, Secret, Star Secret, Chase của Hercules) được lấy từ ảnh sản phẩm và thông tin công bố. Tên các bản này được ghép theo ảnh nên có thể chưa chính xác tuyệt đối.</p>"""

figures = json.loads((ROOT / "data" / "figures.json").read_text(encoding="utf-8"))
for series in DEFENDER:
    key = series["code"].lower()
    PAGES.append(checklist(
        f"defender/{SERIES_FRANCHISE[series['line']]}/{key}/", series["name"],
        f"{series['code']} {series['name']} · Hibe Hobby", f"{series['code']}<br>{html.escape(series['name'])}",
        f"Hibe Hobby's Collection · {series['film']} Defender Version",
        f"Từng nhân vật trong series {series['name']}. Tick ô \"Đã có\" và \"Đã làm video\" cho từng nhân vật.",
        "Tìm tên nhân vật (vd: Optimus, Batman)",
        {"films": [], "primaryLines": ["regular"], "unit": "nhân vật thường",
         "secondary": {"line": "chase", "label": "bản hiếm"},
         "groups": [{"title": "Nhân vật thường", "line": "regular"},
                    {"title": "Bản hiếm · Chase / Secret", "line": "chase",
                     "note": "Không tính vào tiến độ nhân vật thường ở trên."}],
         "noResultHint": "Thử tên nhân vật, ví dụ Optimus hoặc Batman.", "scope": FIGURE_SCOPE},
        [f"fig-{key}"]))

GENERIC_SCOPE = """    <h2>Phạm vi danh sách</h2>
    <p>Gồm các sản phẩm đang có trên store quốc tế blokees.com/en-us, đối chiếu ngày 27/10/2026. Ảnh, tên và tỉ lệ nhân vật lấy từ trang sản phẩm chính thức.</p>
    <p>Ngày ra mắt là tháng sản phẩm lên store quốc tế.</p>"""

LINES = json.loads((ROOT / "data" / "lines.json").read_text(encoding="utf-8"))["lines"]
KNOWN_SKUS = {k["sku"] for name in ["catalog.json", "defender.json"] for k in json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))}
GENERIC_ITEMS = []
GENERIC_LINE_LABELS = {}
hubs = {p["path"]: p for p in PAGES if p["kind"] == "hub"}
pages_by_path = {p["path"]: p for p in PAGES}


def code_range(items):
    return items[0]["code"] + (f"–{items[-1]['code']}" if len(items) > 1 else "")


for line in LINES:
    lpath = f"{line['slug']}/"
    frs = [{**f, "items": [i for i in f["items"] if i["sku"] not in KNOWN_SKUS]} for f in line["franchises"]]
    frs = [f for f in frs if f["items"]]
    if not frs:
        continue
    if lpath in hubs:
        home_card = next((c for c in hubs[""]["cards"] if c["href"] == lpath), None)
        if home_card:
            home_card["lines"] += [f"{line['slug']}-{f['slug']}" for f in frs]
            if line["slug"] == "champion-class":
                home_card["desc"] = "Transformers, " + ", ".join(f["label"] for f in frs) + "."
    if lpath not in hubs:
        hub = {"kind": "hub", "path": lpath, "crumb": line["label"], "title": f"{line['label']} · Hibe Hobby",
               "eyebrow": "Hibe Hobby's Collection", "h1": line["label"],
               "lede": f"{line['kicker']} của Blokees. Chọn thương hiệu để xem checklist.", "cards": []}
        PAGES.append(hub)
        hubs[lpath] = hub
        pages_by_path[lpath] = hub
        newest = max((i for f in frs for i in f["items"]), key=lambda i: i["date"])
        hubs[""]["cards"].append({"href": lpath, "kicker": line["kicker"], "title": line["label"],
                                  "desc": ", ".join(f["label"] for f in frs) + ".",
                                  "lines": [f"{line['slug']}-{f['slug']}" for f in frs], "img": newest["key"]})
    for fr in frs:
        lid = f"{line['slug']}-{fr['slug']}"
        GENERIC_LINE_LABELS[lid] = line["label"]
        fpath = f"{lpath}{fr['slug']}/"
        existing = pages_by_path.get(fpath)
        if existing:
            extra = f"{existing['lines'][0]}-extra"
            GENERIC_LINE_LABELS[extra] = line["label"]
            existing["lines"].append(extra)
            existing["page"]["groups"].append({"title": "Phụ kiện và bản đặc biệt", "line": extra})
            GENERIC_ITEMS.extend({**i, "line": extra, "film": fr["label"]} for i in fr["items"])
            continue
        GENERIC_ITEMS.extend({**i, "line": lid, "film": fr["label"]} for i in fr["items"])
        newest = max(fr["items"], key=lambda i: i["date"])
        hubs[lpath]["cards"].append({"href": f"{fr['slug']}/", "kicker": line["label"], "title": fr["label"],
                                     "desc": code_range(fr["items"]) + ".", "lines": [lid], "img": newest["key"]})
        page = checklist(
            fpath, fr["label"], f"{line['label']} {fr['label']} · Hibe Hobby", f"{html.escape(line['label'])}<br>{html.escape(fr['label'])}",
            f"Hibe Hobby's Collection · Blokees {line['label']}",
            f"Các sản phẩm {fr['label']} thuộc dòng {line['label']} đang bán quốc tế. Bấm vào ảnh hoặc tên để xem chi tiết. Tick ô \"Đã có\" và \"Đã làm video\" để theo dõi bộ sưu tập.",
            "Tìm tên hoặc mã sản phẩm",
            {"films": [], "primaryLines": [lid], "unit": "mẫu", "secondary": None,
             "groups": [{"title": f"{fr['label']} {line['label']}", "line": lid}],
             "noResultHint": "Thử tên sản phẩm hoặc mã.", "scope": GENERIC_SCOPE},
            [lid])
        PAGES.append(page)
        pages_by_path[fpath] = page
        for item in fr["items"]:
            if item["key"] not in figures:
                continue
            PAGES.append(checklist(
                f"{fpath}{item['code'].lower()}/", item["name"],
                f"{item['code']} {item['name']} · Hibe Hobby", f"{item['code']}<br>{html.escape(item['name'])}",
                f"Hibe Hobby's Collection · {fr['label']} {line['label']}",
                f"Từng nhân vật trong {item['name']}. Tick ô \"Đã có\" và \"Đã làm video\" cho từng nhân vật.",
                "Tìm tên nhân vật",
                {"films": [], "primaryLines": ["regular"], "unit": "nhân vật thường",
                 "secondary": {"line": "chase", "label": "bản hiếm"},
                 "groups": [{"title": "Nhân vật thường", "line": "regular"},
                            {"title": "Bản hiếm · Chase / Secret", "line": "chase",
                             "note": "Không tính vào tiến độ nhân vật thường ở trên."}],
                 "noResultHint": "Thử tên nhân vật.", "scope": FIGURE_SCOPE},
                [f"fig-{item['key']}"]))

CRUMBS = {p["path"]: p["crumb"] for p in PAGES}

LINE_LABELS = {"classic": "Classic Class", "champion": "Champion Class", "defender-transformers": "Defender Version",
               "defender-batman": "DC Defender Version", "defender-astral-rally": "Defender Version", **GENERIC_LINE_LABELS}


def crumbs(path):
    parts = [p for p in path.split("/") if p]
    if not parts:
        return ""
    items = []
    for i in range(len(parts) + 1):
        sub = "/".join(parts[:i]) + ("/" if i else "")
        label = html.escape(CRUMBS[sub])
        if i == len(parts):
            items.append(f'<span aria-current="page">{label}</span>')
        else:
            items.append(f'<a href="{"../" * (len(parts) - i)}">{label}</a>')
    return '<nav class="crumbs" aria-label="Đường dẫn">' + "<span>›</span>".join(items) + "</nav>"


def kit_code(kit):
    return kit.get("code") or ("CH" if kit["line"] == "champion" else "CC") + f"{kit['n']:02d}"


if DIST.exists():
    shutil.rmtree(DIST)
(DIST / "img" / "gallery").mkdir(parents=True)
(DIST / "img" / "poster").mkdir(parents=True)
shutil.copy2(ROOT / "icon" / "apple-touch-icon-180.png", DIST / "img" / "brand.png")

POSTERS = ROOT / "img" / "poster"
for source in sorted(POSTERS.glob("*-source.*")):
    target = POSTERS / (source.name.split("-source")[0] + ".webp")
    if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
        im = Image.open(source).convert("RGB")
        im.thumbnail((900, 900))
        im.save(target, "WEBP", quality=82)
for poster in POSTERS.glob("*.webp"):
    if "-source" in poster.name:
        continue
    shutil.copy2(poster, DIST / "img" / "poster" / poster.name)


def card_image(key):
    return f"img/poster/{key}.webp" if (POSTERS / f"{key}.webp").exists() else f"img/{key}.webp"


details = json.loads((ROOT / "data" / "details.json").read_text(encoding="utf-8"))
seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
firebase_file = ROOT / "data" / "firebase.json"
firebase = json.loads(firebase_file.read_text(encoding="utf-8")) if firebase_file.exists() else None

kits = []


def add_kit(kit, key, fig_key, href):
    detail = details.get(key, {})
    thumb = ROOT / "img" / f"{key}.webp"
    if thumb.exists():
        shutil.copy2(thumb, DIST / "img" / f"{key}.webp")
    extra = []
    for g in detail.get("gallery", [])[1:]:
        if (ROOT / "img" / "gallery" / g).exists():
            shutil.copy2(ROOT / "img" / "gallery" / g, DIST / "img" / "gallery" / g)
            extra.append(f"img/gallery/{g}")
    kit["lineLabel"] = LINE_LABELS[kit["line"]]
    kit["img"] = card_image(key) if (POSTERS / f"{key}.webp").exists() or thumb.exists() else "img/brand.png"
    kit["poster"] = kit["img"].startswith("img/poster/") or kit["line"].startswith("defender-") or fig_key in figures
    kit["gallery"] = [kit["img"], *([f"img/{key}.webp"] if kit["img"] != f"img/{key}.webp" and thumb.exists() else []), *extra]
    kit["desc"] = detail.get("desc", "")
    kit["url"] = STORE + kit.pop("handle")
    kits.append(kit)
    if fig_key not in figures:
        return
    kit["href"] = href
    kit["children"] = []
    (DIST / "img" / "fig").mkdir(exist_ok=True)
    for i, fig in enumerate(figures[fig_key], 1):
        name_img = f"{fig_key}-{i:02d}.webp"
        has_img = (ROOT / "img" / "fig" / name_img).exists()
        if has_img:
            shutil.copy2(ROOT / "img" / "fig" / name_img, DIST / "img" / "fig" / name_img)
        rare = fig["line"] == "chase"
        sku = f"{kit['sku']}-{i:02d}"
        kit["children"].append(sku)
        img = f"img/fig/{name_img}" if has_img else "img/brand.png"
        kits.append({
            "n": i, "code": f"{kit['code']}-{i:02d}", "name": fig["name"], "film": kit["name"],
            "line": fig["line"], "page": f"fig-{fig_key}", "sku": sku, "skuLabel": kit["sku"],
            "date": kit["date"], "odds": fig["odds"],
            "lineLabel": ("Bản hiếm" if rare else "Nhân vật thường") + (" · " + fig["odds"] if fig["odds"] else ""),
            "img": img, "gallery": [img], "desc": "", "url": kit["url"],
        })


for name in ["catalog.json", "defender.json"]:
    for kit in json.loads((ROOT / "data" / name).read_text(encoding="utf-8")):
        key = kit_code(kit).lower()
        kit["code"] = kit_code(kit)
        add_kit(kit, key, key, f"{key}/")

for item in GENERIC_ITEMS:
    kit = {"n": item["n"], "code": item["code"], "name": item["name"], "film": item["film"], "line": item["line"],
           "sku": item["sku"], "date": item["date"], "handle": item["handle"]}
    add_kit(kit, item["key"], item["key"], f"{item['code'].lower()}/")

shutil.copy2(ROOT / "icon" / "favicon-64.png", DIST / "favicon.png")
shutil.copy2(ROOT / "icon" / "apple-touch-icon-180.png", DIST / "apple-touch-icon.png")

checklist_tpl = (ROOT / "template.html").read_text(encoding="utf-8")
hub_tpl = (ROOT / "hub.html").read_text(encoding="utf-8")


def with_prefix(kit, prefix):
    out = dict(kit)
    out["img"] = prefix + kit["img"]
    out["gallery"] = [prefix + g for g in kit["gallery"]]
    return out


def common(tpl, page, prefix):
    title = html.escape(page["title"])
    return (tpl.replace("<title>Hibe Hobby's Collection</title>", f"<title>{title}</title>")
            .replace("__TITLE__", title)
            .replace("__FAVICON__", prefix + "favicon.png")
            .replace("__TOUCH_ICON__", prefix + "apple-touch-icon.png")
            .replace("__CRUMBS__", crumbs(page["path"]))
            .replace("__EYEBROW__", html.escape(page["eyebrow"]))
            .replace("__H1__", page["h1"])
            .replace("__LEDE__", html.escape(page["lede"])))


for page in PAGES:
    prefix = "../" * len([p for p in page["path"].split("/") if p])
    if page["kind"] == "hub":
        cards = []
        for c in page["cards"]:
            n = sum(1 for k in kits if k["line"] in c["lines"])
            unit = "series" if c["lines"][0].startswith("defender") else "mẫu"
            img_src = card_image(c["img"]) if (POSTERS / f"{c['img']}.webp").exists() or (ROOT / "img" / f"{c['img']}.webp").exists() else "img/brand.png"
            cards.append(f'''    <a class="card" href="{c["href"]}">
      <div class="art"><img alt="" src="{prefix}{img_src}" loading="lazy"></div>
      <div class="meta">
        <span class="kicker">{html.escape(c["kicker"])}</span>
        <h2>{html.escape(c["title"])}<span aria-hidden="true">→</span></h2>
        <p>{html.escape(c["desc"])}</p>
        <span class="count">{n} {unit}</span>
      </div>
    </a>''')
        brand = f'<div class="brand"><img src="{prefix}img/brand.png" alt="Hibe Hobby"></div>' if page.get("brand") else ""
        body = (common(hub_tpl, page, prefix)
                .replace("__BRAND__", brand)
                .replace("__CARDS__", "\n".join(cards))
                .replace("__REDIRECT__", json.dumps("champion-class/transformers/" if page["path"] == "" else "")))
    else:
        page_kits = [with_prefix(k, prefix) for k in kits if k.get("page", k["line"]) in page["lines"]]
        cfg = dict(page["page"])
        scope = cfg.pop("scope")
        body = (common(checklist_tpl, page, prefix)
                .replace("__SEARCH_HINT__", html.escape(page["hint"]))
                .replace("__SCOPE__", scope)
                .replace("__PAGE__", json.dumps(cfg, ensure_ascii=False))
                .replace("__CATALOG__", json.dumps(page_kits, ensure_ascii=False))
                .replace("__SEED__", json.dumps(seed, ensure_ascii=False))
                .replace("__FIREBASE__", json.dumps(firebase, ensure_ascii=False)))
    out = DIST / page["path"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(HEAD + body + "\n</html>\n", encoding="utf-8")

(DIST / ".nojekyll").write_text("", encoding="utf-8")
size = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
print(f"docs: {len(PAGES)} pages, {len(kits)} kits, {size // 1024} KB")
