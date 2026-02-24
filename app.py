from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def analyze_page(url, keyword):
    result = {
        "title": "",
        "meta": "",
        "word_count": 0,
        "keyword_count": 0,
        "seo_score": 0,
        "page_type": "Homepage"
    }

    keyword = keyword.lower()
    score = 0

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if response.status_code != 200:
            return result

        score += 10  # Page reachable

        soup = BeautifulSoup(response.text, "html.parser")

        # Detect page type
        if url.count("/") > 3:
            result["page_type"] = "Article Page"

        # Title
        title = soup.title.string.strip() if soup.title else ""
        result["title"] = title
        if title:
            score += 15
        if keyword in title.lower():
            score += 20

        # Meta description
        meta = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta["content"].strip() if meta else ""
        result["meta"] = meta_desc
        if meta_desc:
            score += 15

        # Content + keyword
        text = soup.get_text(separator=" ").lower()
        words = re.findall(r'\w+', text)
        result["word_count"] = len(words)

        keyword_count = words.count(keyword)
        result["keyword_count"] = keyword_count
        if keyword_count > 0:
            score += 20

        if len(words) > 300:
            score += 20

        result["seo_score"] = score

    except:
        pass

    return result


@app.route("/", methods=["GET", "POST"])
def index():
    seo = None
    if request.method == "POST":
        url = request.form["url"].strip()
        keyword = request.form["keyword"].strip()
        seo = analyze_page(url, keyword)

    return render_template("index.html", seo=seo)


if __name__ == "__main__":
    app.run(debug=True)