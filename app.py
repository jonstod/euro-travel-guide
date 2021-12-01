from flask import Flask, render_template
from countries import countries, flags
import requests
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen

# Configuration
app = Flask(__name__)

# Routes
@app.route("/")
def home():
    return render_template("index.html", countries=countries)

@app.route("/<country>")
def country(country):
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
        r1 = requests.get('http://flip3.engr.oregonstate.edu:6231/?article=%s' %wiki_link)
        info_dict = json.loads(r1.content)
        wiki_info = info_dict['info']

        r2 = requests.get('http://flip3.engr.oregonstate.edu:6231/?article=%s&country_data=y' %wiki_link)
        data_dict = json.loads(r2.content)
        currency = data_dict['currency']
    except:
        return render_template("error.html", service="Wikipedia scraper service")

    # Subreddit scraper microservice implementation
    try: 
        if country == "Bosnia and Herzegovina":
            sub = "bih"
        elif country == "Czech Republic":
            sub = "czech"
        elif country == "Estonia":
            sub = "Eesti"
        elif country == "Georgia":
            sub = "Sakartvelo"
        elif country == "North Macedonia":
            sub = "mkd"
        elif country == "San Marino":
            sub = "San_Marino"
        elif country == "United Kingdom":
            sub = "unitedkingdom"
        elif country == "Vatican City":
            sub = "vatican"
        else:
            sub = country

        posts = {}

        url = 'http://flip3.engr.oregonstate.edu:6069/sub?subreddit=%s' %sub
        html = urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        tbody = soup.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            posts[cols[0].text.strip()] = cols[1].text.strip()

        titles = posts.keys()
        content = posts.values()
    except:
        return render_template("error.html", service="Subreddit scraper service")

    # Currency converter microservice implementation
    try:
        euro_countries = ['Austria', 'Belgium', 'Cyprus', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 
        'Malta', 'Netherlands', 'Portugal', 'Slovakia', 'Slovenia', 'Spain']

        if country in ['Denmark', 'Norway', 'Sweden', 'Switzerland', 'United Kingdom']:
            r4 = requests.get('http://flip3.engr.oregonstate.edu:4241/?%s=1' %country)
            r4 = json.loads(r4.content)
            conv_rate = str(r4["amount"]) + " US Dollars."
        elif country in euro_countries:
            r4 = requests.get('http://flip3.engr.oregonstate.edu:4241/?EMU%20Members=1')
            r4 = json.loads(r4.content)
            conv_rate = str(r4["amount"]) + " US Dollars."
            currency = "Euro (€) (EUR)"
        else:
            conv_rate = "Conversion unavailable"
    except:
        return render_template("error.html", service="currency conversion")

    return render_template("country.html", country=country, wiki=wiki_info, posts=posts, sub=sub, currency=currency, conv_rate = conv_rate, flag = flag_code)
    

# Listener
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6207, debug=True)