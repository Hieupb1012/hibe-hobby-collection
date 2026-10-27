import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PAGES = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cache" / "pages"
SKIP = {("champion-class", "transformers"), ("defender", "transformers"), ("defender", "batman"), ("defender", "astral-rally")}
RARE_WORDS = ("special", "secret", "chase", "radiant", "hidden", "rare")
RARE_ODDS = {"1/144", "1/72", "1/36", "3/144", "2/144"}


def parse_cards(page):
    items = []
    for m in re.finditer(r'detail-dufault-item-title">([^<]+)</h3>', page):
        imgs = list(re.finditer(r'detail-dufault-item-img" src="([^"]+)"', page[:m.start()]))
        odds = re.search(r'Probability \(Math\.\)</p>\s*<p[^>]*>([^<]+)</p>', page[m.end():m.end() + 1500], re.S)
        items.append({"title": m.group(1).strip(), "img": "https:" + imgs[-1].group(1) if imgs else None,
                      "odds": odds.group(1).strip() if odds else ""})
    return items


def parse_columns(page):
    pattern = (r'<img src="(//blokees\.com/cdn/shop/files/[^"]+?)(?:&width=\d+)?" loading="lazy">\s*</picture>\s*</div>\s*'
               r'<div class="columns-context"[^>]*>\s*<div class="title">\s*([^<]+?)\s*</div>.*?'
               r'Probability \(Math\.\)</div>\s*<div[^>]*>\s*([^<]+?)\s*</div>')
    return [{"title": m.group(2), "img": "https:" + m.group(1).replace("&amp;", "&"), "odds": m.group(3)}
            for m in re.finditer(pattern, page, re.S)]


def clean(name):
    name = re.sub(r"\s*-\s*", "-", name.strip())
    return name.replace("Glittering-", "Glittering ").replace("Brilliant-", "Brilliant ")


def to_figures(rows):
    seen = set()
    out = []
    for row in rows:
        if not row["img"]:
            continue
        name = clean(row["title"])
        rare = name in seen or name.lower().startswith(RARE_WORDS) or row["odds"].replace(" ", "") in RARE_ODDS
        label = f"Chase {name}" if name in seen and not name.lower().startswith(RARE_WORDS) else name
        seen.add(name)
        out.append({"name": label, "odds": row["odds"], "img": row["img"], "line": "chase" if rare else "regular"})
    return out


def find_poster(page):
    for m in re.finditer(r'//blokees\.com/cdn/shop/files/([^"\'?\s)]+\.(?:webp|png|jpe?g))', page):
        name = m.group(1)
        if re.search(r"(^|[^a-z])kv([^a-z]|$)", name, re.I):
            return "https://blokees.com/cdn/shop/files/" + name
    return None


def main():
    lines = json.loads((ROOT / "data" / "lines.json").read_text(encoding="utf-8"))["lines"]
    figures_file = ROOT / "data" / "figures.json"
    figures = json.loads(figures_file.read_text(encoding="utf-8"))
    posters_file = ROOT / "data" / "posters.json"
    posters = json.loads(posters_file.read_text(encoding="utf-8")) if posters_file.exists() else {}
    found = missing = 0
    for line in lines:
        for fr in line["franchises"]:
            if (line["slug"], fr["slug"]) in SKIP:
                continue
            for item in fr["items"]:
                page_file = PAGES / f"{item['handle']}.html"
                if not page_file.exists():
                    missing += 1
                    continue
                page = page_file.read_text(encoding="utf-8", errors="ignore")
                rows = parse_cards(page) or parse_columns(page)
                figs = to_figures(rows)
                if len(figs) >= 3:
                    figures[item["key"]] = figs
                    found += 1
                poster = find_poster(page)
                if poster and item["key"] not in posters:
                    posters[item["key"]] = poster
    figures_file.write_text(json.dumps(figures, ensure_ascii=False, indent=1), encoding="utf-8")
    posters_file.write_text(json.dumps(posters, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"series with figures: {found}, pages missing: {missing}, posters: {len(posters)}")


if __name__ == "__main__":
    main()
