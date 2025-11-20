import csv
import datetime
import requests
import feedparser
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime

from modules.feeds import load_feeds
from modules.images import extract_image


# ---------------------------------------------------------
# DATE FORMAT (FR)
# ---------------------------------------------------------
def format_french_date(date_str: str) -> str:
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%d %B %Y – %H:%M")
    except:
        return date_str


# ---------------------------------------------------------
# CLEAN HTML
# ---------------------------------------------------------
def clean_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "table", "img"]):
        tag.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


# ---------------------------------------------------------
# FULL TEXT EXTRACTION
# ---------------------------------------------------------
def extract_full_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = soup.find_all("p")

        full_text = " ".join(
            p.get_text(" ", strip=True) for p in paragraphs
        )
        return clean_html(full_text)

    except:
        return ""


# ---------------------------------------------------------
# LOAD ALL ARTICLES FROM RSS (USED BY /refresh)
# ---------------------------------------------------------
def load_all_articles() -> list:
    """Fetch all articles from RSS feeds."""
    feeds = load_feeds()
    articles = []

    for feed in feeds:
        parsed = feedparser.parse(feed["url"])

        for entry in parsed.entries:
            title = getattr(entry, "title", "Sans titre")
            link = getattr(entry, "link", "")

            # SUMMARY
            summary_raw = getattr(entry, "summary", "")
            if hasattr(entry, "content"):
                alt = entry.content[0].get("value", "")
                summary_raw = alt or summary_raw

            summary = clean_html(summary_raw)
            full_text = extract_full_text(link)
            image_url = extract_image(entry)

            article = {
                "source": feed["name"],
                "domains": feed["domains"],
                "themes": feed["themes"],

                "title": title,
                "link": link,
                "published": format_french_date(getattr(entry, "published", "")),

                "summary": summary,
                "full_text": full_text,
                "image_url": image_url,

                "source_ranking": feed["source_ranking"],
                "article_ranking": feed["source_ranking"],
                "ranking_author": feed["ranking_author"],

                "feasibility_score": 0,
                "feasibility_author": "",

                "fetched_at": datetime.datetime.utcnow().strftime("%d %B %Y – %H:%M"),
            }

            articles.append(article)

    return articles


# ---------------------------------------------------------
# SAVE ARTICLES (CSV)
# ---------------------------------------------------------
def save_articles_to_csv(path, articles):
    fieldnames = [
        "id", "source", "domains", "themes",
        "title", "link", "published",
        "summary", "full_text", "image_url",
        "source_ranking", "article_ranking",
        "ranking_author", "feasibility_score",
        "feasibility_author", "fetched_at",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, article in enumerate(articles):
            row = article.copy()
            row["id"] = i
            row["domains"] = ",".join(row["domains"])
            row["themes"] = ",".join(row["themes"])
            writer.writerow(row)


# ---------------------------------------------------------
# LOAD ARTICLES (FROM CSV CACHE)
# ---------------------------------------------------------
def load_articles_from_csv(path):
    articles = []
    errors = []

    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            required = {
                "source", "domains", "themes", "title", "summary",
                "full_text", "source_ranking", "article_ranking", "feasibility_score"
            }

            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                return [], ["CSV incomplet ou obsolète."]

            for row in reader:
                row["domains"] = [d.strip() for d in row["domains"].split(",")]
                row["themes"] = [t.strip() for t in row["themes"].split(",")]

                row["source_ranking"] = int(row["source_ranking"])
                row["article_ranking"] = int(row["article_ranking"])
                row["feasibility_score"] = int(row["feasibility_score"])

                articles.append(row)

            return articles, []

    except FileNotFoundError:
        return [], ["Fichier articles.csv introuvable."]
