"""Aggiorna le news ENEA in contenuti.json (eseguito da GitHub Actions)."""
import json, re, urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin
from datetime import date

BASE = "https://italiainclassea.enea.it/"
SKIP = re.compile(r"/(news|eventi|podcast|training-day|elearning)/?$")

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.href = None; self.buf = []; self.out = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href"); self.buf = []
    def handle_data(self, data):
        if self.href is not None: self.buf.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.out.append((self.href, " ".join("".join(self.buf).split()))); self.href = None

def fetch_news():
    req = urllib.request.Request(BASE + "news/", headers={"User-Agent": "Mozilla/5.0 (compatible; greengov-crossword-news)"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    p = Links(); p.feed(html)
    seen, items = set(), []
    for href, text in p.out:
        url = urljoin(BASE, href or "")
        if len(text) < 25 or not url.startswith(BASE) or url.endswith("/") or SKIP.search(url) or url in seen: continue
        seen.add(url); items.append({"t": text, "u": url, "s": "ENEA", "d": "dal sito"})
    return items[:12]

if __name__ == "__main__":
    data = json.load(open("contenuti.json", encoding="utf-8"))
    new = fetch_news()
    if len(new) < 3:
        raise SystemExit("Poche news trovate: contenuti.json non modificato")
    manual = [n for n in data.get("news", []) if n.get("d") != "dal sito" and n["u"] not in {x["u"] for x in new}]
    data["news"] = new + manual
    data["aggiornato"] = date.today().isoformat()
    json.dump(data, open("contenuti.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(new), "news ENEA aggiornate")
