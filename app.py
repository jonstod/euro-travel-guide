from flask import Flask, render_template
from flask_cors import CORS
from countries import countries
import requests
import json
from bs4 import BeautifulSoup

# Configuration

app = Flask(__name__)
CORS(app)

# Routes
@app.route("/")
def home():
    return render_template("index.html", countries=countries)

@app.route("/<country>")
def country(country):
    # Wikipedia scraper microservice implementation
    r1 = requests.get('http://flip3.engr.oregonstate.edu:6231/?article=%s' %country)
    info_dict = json.loads(r1.content)
    wiki_info = info_dict['info']

    r2 = requests.get('http://flip3.engr.oregonstate.edu:6231/?article=%s&country_data=y' %country)
    data_dict = json.loads(r2.content)
    currency = data_dict['currency']

    # Subreddit scraper microservice implementation
    r3 = requests.get('http://flip3.engr.oregonstate.edu:6069/sub?subreddit=%s' %country)
    soup = BeautifulSoup(r3.text, 'html.parser')
    
    reddit_table = soup.find('table', class_ = 'dataframe')
    posts = {}
    
    for post in reddit_table.find_all('tbody'):
        rows = post.find_all('tr')
        for row in rows:
            posts[row.find('td').text.strip()] = row.find_all('td')[1].text.strip()

    titles = posts.keys()
    content = posts.values()

    # Currency converter microservice implementation


    return render_template("country.html", country=country, wiki=wiki_info, posts=posts, currency=currency)

# Listener
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6207, debug=True)