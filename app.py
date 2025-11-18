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

    articles = sorted(articles, key=lambda x: x[1].published_gitparsed, reverse=True)
