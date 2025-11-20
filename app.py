from flask import Flask, render_template, request, redirect

from modules.articles import (
    load_articles_from_csv,
    load_all_articles,
    save_articles_to_csv,
)

from modules.feeds import (
    get_available_domains,
    get_available_themes,
)

from modules.filtering import filter_articles

ARTICLES_CSV_PATH = "data/articles.csv"

app = Flask(__name__)

# ---------------------------------------------------------
# HOME (chargement rapide → articles.csv)
# ---------------------------------------------------------
@app.route("/")
def index():
    articles, errors = load_articles_from_csv(ARTICLES_CSV_PATH)

    if errors:
        return render_template(
            "index.html",
            articles=[],
            page=1,
            total_pages=1,
            errors=errors,
            domains=get_available_domains(),
            themes=get_available_themes(),
        )

    page = request.args.get("page", 1, type=int)
    per_page = 10

    start = (page - 1) * per_page
    end = start + per_page
    paginated = articles[start:end]

    total_pages = (len(articles) // per_page) + 1

    return render_template(
        "index.html",
        articles=paginated,
        page=page,
        total_pages=total_pages,
        errors=[],
        domains=get_available_domains(),
        themes=get_available_themes(),
    )


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------
@app.route("/search")
def search():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return redirect("/")

    articles, errors = load_articles_from_csv(ARTICLES_CSV_PATH)

    if errors:
        return render_template(
            "index.html",
            articles=[],
            page=1,
            total_pages=1,
            errors=errors,
            domains=get_available_domains(),
            themes=get_available_themes(),
        )

    results = [
        a for a in articles
        if query in a["title"].lower()
        or query in a["summary"].lower()
        or query in a["full_text"].lower()
    ]

    return render_template(
        "index.html",
        articles=results,
        page=1,
        total_pages=1,
        search_query=query,
        errors=[],
        domains=get_available_domains(),
        themes=get_available_themes(),
    )


# ---------------------------------------------------------
# FILTER : domaine(s) + thèmes
# ---------------------------------------------------------
@app.route("/filter")
def filter_route():
    selected_domains = request.args.getlist("domains")
    selected_themes = request.args.getlist("themes")

    articles, errors = load_articles_from_csv(ARTICLES_CSV_PATH)

    if errors:
        return render_template(
            "index.html",
            articles=[],
            page=1,
            total_pages=1,
            errors=errors,
            domains=get_available_domains(),
            themes=get_available_themes(),
        )

    filtered = filter_articles(
        articles,
        selected_domains or None,
        selected_themes or None,
    )

    return render_template(
        "index.html",
        articles=filtered,
        page=1,
        total_pages=1,
        selected_domains=selected_domains,
        selected_themes=selected_themes,
        errors=[],
        domains=get_available_domains(),
        themes=get_available_themes(),
    )


# ---------------------------------------------------------
# REFRESH — recharge les RSS et régénère articles.csv
# ---------------------------------------------------------
@app.route("/refresh")
def refresh():
    articles = load_all_articles()
    save_articles_to_csv(ARTICLES_CSV_PATH, articles)
    return redirect("/")


# ---------------------------------------------------------
# SOURCE MANAGEMENT (ADD / EDIT / DELETE)
# ---------------------------------------------------------
from modules.feeds_editor import load_sources, add_source, update_source, delete_source

@app.route("/sources")
def manage_sources():
    sources = load_sources()
    return render_template(
        "manage_sources.html",
        sources=sources,
        domains=get_available_domains(),
        themes=get_available_themes(),
    )


@app.route("/sources/new", methods=["GET", "POST"])
def new_source():
    if request.method == "POST":
        name = request.form["name"]
        url = request.form["url"]

        available_domains = get_available_domains()

        # Domaine automatique s'il n'y en a qu'un
        if len(available_domains) == 1:
            domains = available_domains[0]
        else:
            domains = ",".join(request.form.getlist("domains"))

        themes = ",".join(request.form.getlist("themes"))
        ranking = request.form["ranking"]
        author = "Valentin"

        add_source({
            "name": name,
            "url": url,
            "domains": domains,
            "themes": themes,
            "source_ranking": ranking,
            "ranking_author": author,
        })

        return redirect("/sources")

    return render_template(
        "edit_source.html",
        mode="new",
        source=None,
        domains=get_available_domains(),
        themes=get_available_themes(),
    )


@app.route("/sources/edit/<int:index>", methods=["GET", "POST"])
def edit_source(index):
    sources = load_sources()
    source = sources[index]

    if request.method == "POST":
        name = request.form["name"]
        url = request.form["url"]

        available_domains = get_available_domains()

        if len(available_domains) == 1:
            domains = available_domains[0]
        else:
            domains = ",".join(request.form.getlist("domains"))

        themes = ",".join(request.form.getlist("themes"))
        ranking = request.form["ranking"]

        update_source(index, {
            "name": name,
            "url": url,
            "domains": domains,
            "themes": themes,
            "source_ranking": ranking,
            "ranking_author": "Valentin",
        })

        return redirect("/sources")

    return render_template(
        "edit_source.html",
        mode="edit",
        index=index,
        source=source,
        domains=get_available_domains(),
        themes=get_available_themes(),
    )


@app.route("/sources/delete/<int:index>")
def remove_source(index):
    delete_source(index)
    return redirect("/sources")


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
