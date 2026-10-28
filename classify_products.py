import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent

LINES = [
    ("champion-class", "Champion Class", "Model kit lắp ráp"),
    ("defender", "Defender", "Hộp mù theo series"),
    ("galaxy-version", "Galaxy Version", "Hộp mù mini"),
    ("shining-version", "Shining Version", "Hộp mù mini bản đặc biệt"),
    ("action-edition", "Action Edition", "Model kit cao cấp"),
    ("legend-edition", "Legend Edition", "Model kit cỡ lớn"),
    ("special-edition", "Phiên bản đặc biệt", "Yearly, Unicron và các bản giới hạn"),
    ("wheels", "Blokees Wheels", "Xe lắp ráp"),
    ("warrior-version", "Warrior Version", "Hộp mù Herospire"),
    ("armor-version", "Armor Version", "Model kit Herospire"),
    ("terraventure", "Terraventure", "Jurassic World"),
    ("daalamode", "DaaLaMode", "Búp bê và trang phục"),
    ("fantastics", "Fantastics", "Figure nhân vật"),
    ("daavibe", "DaaVibe", "Figure cảnh sinh hoạt"),
    ("precool", "preCOOL", "Hộp mù mini"),
    ("mokoo", "Mokoo", "Hộp mù"),
    ("daadoos", "daadoos", "Đồ sưu tầm"),
]

FRANCHISES = [
    (r"transformers|unicron", "transformers", "Transformers"),
    (r"ultraman", "ultraman", "Ultraman"),
    (r"saint seiya", "saint-seiya", "Saint Seiya"),
    (r"naruto|boruto", "naruto", "Naruto"),
    (r"astral rally", "astral-rally", "Astral Rally"),
    (r"\bdc\b|batman", "batman", "Batman"),
    (r"marvel", "marvel", "Marvel"),
    (r"star wars", "star-wars", "Star Wars"),
    (r"mega man", "mega-man", "Mega Man"),
    (r"herospire", "herospire", "Herospire"),
    (r"jurassic", "jurassic-world", "Jurassic World"),
    (r"evangelion", "evangelion", "Evangelion"),
    (r"miku|mojipod", "hatsune-miku", "Hatsune Miku"),
    (r"minion", "minions", "Minions"),
    (r"sesame", "sesame-street", "Sesame Street"),
    (r"powerpuff", "powerpuff-girls", "The Powerpuff Girls"),
    (r"zootopia", "zootopia", "Zootopia"),
    (r"doll clothes", "doll-clothes", "Trang phục búp bê"),
]

LINE_RULES = [
    (r"defender version", "defender"),
    (r"champion class|classic class", "champion-class"),
    (r"galaxy version|naruto shippuden gv\d", "galaxy-version"),
    (r"shining version", "shining-version"),
    (r"action edition", "action-edition"),
    (r"legend edition", "legend-edition"),
    (r"yearly version|unicron", "special-edition"),
    (r"\bwheels\b", "wheels"),
    (r"warrior version", "warrior-version"),
    (r"armor version", "armor-version"),
    (r"terraventure", "terraventure"),
    (r"daalamode", "daalamode"),
    (r"fantastics", "fantastics"),
    (r"daavibe", "daavibe"),
    (r"precool", "precool"),
    (r"mokoo", "mokoo"),
    (r"daadoos", "daadoos"),
]

PREFIX = {"champion-class": "CC", "defender": "DV", "galaxy-version": "GV", "shining-version": "SV", "action-edition": "AE",
          "legend-edition": "LE", "special-edition": "SP", "wheels": "WH", "warrior-version": "WV", "armor-version": "AV",
          "terraventure": "TS", "daalamode": "DL", "fantastics": "FS", "daavibe": "DB", "precool": "PC", "mokoo": "MK", "daadoos": "DD"}


def clean_title(title):
    t = html.unescape(re.sub(r"<[^>]+>", "", title))
    t = re.sub(r"[™®]", "", t)
    t = re.sub(r"\s*\|\s*Blokees\s*$", "", t, flags=re.I)
    t = re.sub(r"^Blokees\s*\|?\s*", "", t, flags=re.I)
    t = re.sub(r"\s+MODEL KITS?$", "", t, flags=re.I)
    t = re.sub(r"\s+Model Kits?$", "", t)
    return re.sub(r"\s+", " ", t).strip()


def classify(title):
    low = title.lower()
    line = next((l for pat, l in LINE_RULES if re.search(pat, low)), None)
    franchise = next(((slug, label) for pat, slug, label in FRANCHISES if re.search(pat, low)), None)
    return line, franchise


def number(title):
    m = re.search(r"(?:version|class|edition|series|gv|ts|aspect|0)\s*[-:]?\s*(?:s\s*)?(\d{1,2})\b", title, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(?:C|CT)(\d{2})\b", title)
    return int(m.group(1)) if m else 0


def short_name(title, line):
    t = title
    t = re.sub(r"^(Transformers|Ultraman|Saint Seiya|NARUTO SHIPPUDEN|NARUTO|Mega Man|Herospire|Astral Rally|DC|Marvel[^|]*?|Jurassic World|Evangelion)\s+", "", t, flags=re.I) if line not in ("daalamode", "fantastics", "daavibe", "precool", "mokoo", "daadoos") else t
    t = re.sub(r"^(Galaxy Version|Shining Version|Champion Class|Classic Class|Defender Version|Action Edition|Legend Edition|Warrior Version|Armor Version|Terraventure TS|GV)\s*(S\s+)?\d{0,2}\s*[-:|]?\s*", "", t, flags=re.I)
    t = re.sub(r"^\|\s*", "", t)
    t = re.sub(r"^Wheels \| Transformers (CT|C)\d{2}\s*", "", t)
    return t.strip(" -|:") or title


def main():
    products = json.loads((ROOT / "data" / "blokees-store-products.json").read_text(encoding="utf-8"))["products"]
    lines = {slug: {"slug": slug, "label": label, "kicker": kicker, "franchises": {}} for slug, label, kicker in LINES}
    unknown = []
    for p in products:
        title = clean_title(p["title"])
        line, franchise = classify(title)
        if not line or not franchise:
            unknown.append(title)
            continue
        fslug, flabel = franchise
        fr = lines[line]["franchises"].setdefault(fslug, {"slug": fslug, "label": flabel, "items": []})
        sku = p["variants"][0]["sku"].split("-")[0]
        n = number(title)
        fr["items"].append({
            "key": f"p{sku}", "sku": sku, "n": n, "title": title, "name": short_name(title, line),
            "date": p["published_at"][:7], "handle": p["handle"],
        })
    for m in json.loads((ROOT / "data" / "manual.json").read_text(encoding="utf-8")):
        fr = lines[m["line"]]["franchises"].setdefault(m["franchise"], {"slug": m["franchise"], "label": m["franchise_label"], "items": []})
        fr["items"].append({k: m[k] for k in ("key", "sku", "n", "title", "name", "date", "url", "code")} | {"manual": True, "handle": None})
    for line in lines.values():
        for fr in line["franchises"].values():
            fr["items"].sort(key=lambda i: (i["n"] == 0, bool(re.search(r"version s\s+\d", i["title"], re.I)), i["n"], i["date"], i["title"]))
            prefix = PREFIX[line["slug"]]
            for i, item in enumerate(fr["items"], 1):
                if item.get("manual"):
                    continue
                wheel = re.search(r"\b(CT|C)(\d{2})\b", item["title"]) if line["slug"] == "wheels" else None
                if wheel:
                    item["code"] = wheel.group(1) + wheel.group(2)
                    continue
                sub = "S" if re.search(r"version s\s+\d", item["title"], re.I) else ""
                item["code"] = f"{prefix}{sub}{item['n']:02d}" if item["n"] else f"{prefix}-{i:02d}"
            seen = {}
            for item in fr["items"]:
                seen[item["code"]] = seen.get(item["code"], 0) + 1
                if seen[item["code"]] > 1:
                    item["code"] += "ABCDEFGH"[seen[item["code"]] - 1]
    out = {"lines": [{**l, "franchises": list(l["franchises"].values())} for l in lines.values() if l["franchises"]], "unknown": unknown}
    (ROOT / "data" / "lines.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for l in out["lines"]:
        print(l["label"], {f["label"]: len(f["items"]) for f in l["franchises"]})
    print("unknown:", unknown)


if __name__ == "__main__":
    main()
