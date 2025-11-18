import csv
import datetime
import feedparser
from flask import Flask, render_template, request

app = Flask(__name__)

# -----------------------------
# 1) FEEDS avec thème + ranking
# -----------------------------
RSS_FEEDS = {
    "IEEE IoT Journal": {
        "url": "https://ieeexplore.ieee.org/rss/TOC84.XML",
        "theme": "IoT",
        "ranking": 5,
        "ranking_author": "Valentin"
    },
    "TechCrunch IoT": {
        "url": "https://techcrunch.com/tag/iot/feed/",
        "theme": "IoT",
        "ranking": 4,
        "ranking_author": "Valentin"
    },
    "5G Americas": {
        "url": "https://www.5gamericas.org/feed/",
        "theme": "5G",
        "ranking": 4,
        "ranking_author": "Valentin"
    },
    "Architecture 2030 – Climate Action": {
        "url": "https://architecture2030.org/feed/",
        "theme": "Carbone",
        "ranking": 5,
        "ranking_author": "Valentin"
    }
}

# -----------------------------
# 2) Extraction image RSS
# -----------------------------
def extract_image(entry):
    media = getattr(entry, "media_content", None)
    if media and len(media) > 0 and "url" in media[0]:
        return media[0]["url"]

    thumb = getattr(entry, "media_thumbnail", None)
    if thumb and len(thumb) > 0 and "url" in thumb[0]:
        return thumb[0]["url"]

    enclosures = getattr(entry, "enclosures", None)
    if enclosures and len(enclosures) > 0 and "href" in enclosures[0]:
        return enclosures[0]["href"]

    return None


# -----------------------------
# 3) Sauvegarde CSV
# -----------------------------
def save_articles_to_csv(path, articles):
    fieldnames = [
        "id", "source", "theme", "title", "link", "published",
        "summary", "image_url", "source_ranking", "article_ranking",
        "ranking_author", "fetched_at"
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, art in enumerate(articles, start=1):
            row = art.copy()
            row["id"] = i
            row["fetched_at"] = datetime.datetime.utcnow().isoformat()
            writer.writerow(row)


# -----------------------------
# 4) ROUTE PRINCIPALE "/"
# -----------------------------
@app.route('/')
def index():
    articles = []

    # Parse de toutes les sources
    for source, meta in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(meta["url"])

        for entry in parsed_feed.entries:
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            image_url = extract_image(entry)

            article = {
                "source": source,
                "theme": meta["theme"],
                "title": getattr(entry, "title", "Sans titre"),
                "link": getattr(entry, "link", "#"),
                "published": getattr(entry, "published", ""),
                "summary": summary,
                "image_url": image_url,
                "source_ranking": meta["ranking"],
                "article_ranking": meta["ranking"],
                "ranking_author": meta["ranking_author"]
            }

            articles.append(article)

    # Tri : ranking puis date
    articles = sorted(
        articles,
        key=lambda x: (x["article_ranking"], x["published"]),
        reverse=True
    )

    # Sauvegarde CSV
    save_articles_to_csv("data/articles.csv", articles)

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 10
    total_articles = len(articles)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    total_pages = total_articles // per_page + (1 if total_articles % per_page != 0 else 0)

    return render_template(
        "index.html",
        articles=paginated_articles,
        page=page,
        total_pages=total_pages
    )


# -----------------------------
# 5) ROUTE SEARCH "/search"
# -----------------------------
@app.route('/search')
def search():
    query = request.args.get("q", "")

    # Recharger les articles (sans repasser par le CSV)
    articles = []
    for source, meta in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(meta["url"])
        for entry in parsed_feed.entries:
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            image_url = extract_image(entry)

            article = {
                "source": source,
                "theme": meta["theme"],
                "title": getattr(entry, "title", "Sans titre"),
                "link": getattr(entry, "link", "#"),
                "published": getattr(entry, "published", ""),
                "summary": summary,
                "image_url": image_url,
                "source_ranking": meta["ranking"],
                "article_ranking": meta["ranking"],
                "ranking_author": meta["ranking_author"]
            }

            articles.append(article)

    if not query:
        results = []
    else:
        results = [
            a for a in articles
            if query.lower() in a["title"].lower()
        ]

    return render_template("search_results.html", articles=results, query=query)


# -----------------------------
# 6) RUN
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
