import feedparser
from flask import Flask, render_template, request

app = Flask(__name__)

RSS_FEEDS = {
    'BuildingSmart OpenBIM': 'https://www.buildingsmart.org/feed/',
    'IEA – Smart Buildings & Energy': 'https://www.iea.org/rss/news',
    'Smart Buildings Magazine': 'https://smartbuildingsmagazine.com/feed',
    'IEEE IoT Journal': 'https://ieeexplore.ieee.org/rss/TOC84.XML',
    '5G Americas': 'https://www.5gamericas.org/feed/',
    'Ericsson 5G Insights': 'https://www.ericsson.com/api/rss/section/media',
    'GreenTechMedia': 'https://www.greentechmedia.com/rss',
    'Architecture 2030 – Climate Action': 'https://architecture2030.org/feed/',
    'ArchDaily – Smart & Sustainable': 'https://www.archdaily.com/rss',
    'TechCrunch IoT': 'https://techcrunch.com/tag/iot/feed/',
}

@app.route('/')
def index():
    articles = []
    for source, feed in RSS_FEEDS.itmes():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]

    articles = sorted(articles, key=lambda x: x[1].published_parsed, reverse=True)

    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_articles = len(articles)
    start = (page-1) * per_page
    end = start + page
    paginated_articles = articles[start:end]

    return render_template('index.html', articles=paginated_articles, page=page, total_page = total_articles // per_page + 1)

@app.route('/search')
def search():
    query = request.args.get('q')

    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    results = [articles for article in articles if query.lower() in article[1].title.lower()]

    return render_template('search_results.html', articles=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)