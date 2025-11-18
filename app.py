import feedparser
from flask import Flask, render_template, request


app = Flask(__name__)

RSS_FEEDS = {
    "IEEE IoT Journal": {
        "url": "https://ieeexplore.ieee.org/rss/TOC84.XML",
        "theme": "IoT",
        "ranking": 5,             # qualité de la source
        "ranking_author": "Valentin"
    },
    "TechCrunch IoT": {
        "url": "https://techcrunch.com/tag/iot/feed/",
        "theme": "IoT",
        "ranking": 4,
        "ranking_author": "Valentin"
    },
    # ...
}

@app.route('/')
def index():
    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    articles = sorted(articles, key=lambda x: x[1].published_parsed, reverse=True)

    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_articles = len(articles)
    start = (page-1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template('index.html', articles=paginated_articles, page=page,
                           total_pages = total_articles // per_page + 1)


@app.route('/search')
def search():
    query = request.args.get('q')

    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    results = [article for article in articles if query.lower() in article[1].title.lower()]

    return render_template('search_results.html', articles=results, query=query)


if __name__ == '__main__':
    app.run(debug=True)