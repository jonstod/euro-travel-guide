from flask import Flask, render_template
from countries import countries, euro_countries, subreddit_dict, flags
import requests
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen


# Configuration
app = Flask(__name__)


# Routes
@app.route("/")
def home_page():
    return render_template("index.html", countries=countries)


@app.route("/about")
def about_page():
    return render_template("about.html", countries=countries)


@app.route("/<country>")
def country_page(country):
    # Prevention from using other parameters (other words/phrases with associated Wikipedia pages and subreddits)
    if country not in countries:
        return render_template("error.html", service = "URL parameters. The parameter(s) specified is not recognized as a European country.")

    flag_code = flags[country]

    # Wikipedia scraper microservice implementation
    try:
        if country == "Georgia":
            wiki_link = "Georgia_(country)"
        else:
            wiki_link = country

        wiki_info = get_wiki_info(country, wiki_link)
        currency = get_wiki_currency(wiki_link)
    except:
        return render_template("error.html", service="Wikipedia scraper service")

    # Subreddit scraper microservice implementation
    try: 
        sub = get_subreddit_name(country)
        posts = get_sub_posts(sub)
        titles = posts.keys()
        content = posts.values()
    except:
        return render_template("error.html", service="Subreddit scraper service")

    # Currency converter microservice implementation
    try:
        if country in euro_countries:
            currency = "Euro (€) (EUR)"  # don't show additional currencies (i.e. France)

        conv_rate = get_currency_conv(country)
    except:
        return render_template("error.html", service="currency conversion")

    return render_template("country.html", country=country, wiki=wiki_info, posts=posts, sub=sub, currency=currency, conv_rate = conv_rate, flag = flag_code, countries = countries)
    

def get_wiki_info(country, wiki_link) -> str:
    """
    Returns the top information section of a country's wikipedia page.
    """
    r = requests.get('http://flip3.engr.oregonstate.edu:6231/?article=%s' %wiki_link)
    info_dict = json.loads(r.content)
    wiki_info = info_dict['info']
    wiki_info = wiki_info[wiki_info.find(country):]

    return wiki_info


def get_wiki_currency(wiki_link) -> str:
    """
    Returns the name of a country's national currency as specified by its wikipedia page.
    """
    r2 = requests.get('http://flip3.engr.oregonstate.edu:6231/?article=%s&country_data=y' %wiki_link)
    data_dict = json.loads(r2.content)
    currency = data_dict['currency']

    return currency


def get_subreddit_name(country) -> str:
    """
    Returns the name of a country's subreddit.
    """ 
    if country in subreddit_dict:
        return subreddit_dict.get(country)
    else:
        return country


def get_sub_posts(sub):
    """
    Returns the titles and content links of the top 10 all-time posts in a subreddit.
    """
    posts = {}

    url = 'http://flip3.engr.oregonstate.edu:6069/sub?subreddit=%s' %sub
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    tbody = soup.find('tbody')
    rows = tbody.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        posts[cols[0].text.strip()] = cols[1].text.strip()

    return posts


def get_currency_conv(country) -> str:
    """
    Returns the conversion rate between a country's currency and US Dollars. Specifies if unavaible.
    """
    # Account for differences in microservice conversion - rates are flipped for some countries
    if country in ['Denmark', 'Norway', 'Sweden', 'Switzerland']:
        r4 = requests.get('http://flip3.engr.oregonstate.edu:4241/?%s=1' %country)
        r4 = json.loads(r4.content)
        conv = r4["amount"]
        conv_inverse = round(1.0/float(conv), 2)
        conv_rate = str(conv_inverse) + " US Dollars."
    elif country == 'United Kingdom':
        r4 = requests.get('http://flip3.engr.oregonstate.edu:4241/?%s=1' %country)
        r4 = json.loads(r4.content)
        conv_rate = str(r4["amount"]) + " US Dollars."
    elif country in euro_countries:
        r4 = requests.get('http://flip3.engr.oregonstate.edu:4241/?EMU%20Members=1')
        r4 = json.loads(r4.content)
        conv_rate = str(r4["amount"]) + " US Dollars."
    else:
        conv_rate = "Conversion unavailable"

    return conv_rate


# Listener
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6207, debug=True)