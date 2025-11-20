def filter_articles(articles, selected_domains=None, selected_themes=None):

    result = articles

    if selected_domains:
        result = [
            a for a in result
            if any(d in a["domains"] for d in selected_domains)
        ]

    if selected_themes:
        result = [
            a for a in result
            if any(t in a["themes"] for t in selected_themes)
        ]

    return result
