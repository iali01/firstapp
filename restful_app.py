from flask import Flask
import json
from requests.utils import requote_uri
import datetime
# To transform the data to a JSON object
from flask import jsonify
import urllib
import urllib.parse
import urllib.request
#for caching results
import requests_cache
from flask import render_template
from flask import request

#for ip address
import socket

# connecting to cassandra
from cassandra.cluster import Cluster
# 'cassandra' is the name of the cluster, this maybe different in your case
cluster = Cluster(['cassandra'], connect_timeout=30)
session = cluster.connect()

#caching, results are cached in a file called 'api_cache' in the root app directory
#using 'sqlite' which will expire in 36000 secs
requests_cache.install_cache('api_cache', backend='sqlite', expire_after=36000)

app = Flask(__name__, instance_relative_config=True)

# the order matters, the latter will over write anythin prior
app.config.from_object('config')
app.config.from_pyfile('config.py')

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=" + app.config['API_KEY_WEATHER']
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=" + app.config['API_KEY_CURRENCY']

# defaults for pick list on home page
DEFAULTS = {'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'
            }

#This returns a single IP which is the primary (the one with a default route).
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


@app.route("/404/")
def not_found():
    return render_template("404.html"), 404


@app.route("/weather/<city>/<date>", methods=['GET'])
def historic_weather(city="London", date="20060401"):
    weather_data = session.execute("""Select * From weatherhistory.stats where city = '{}' and date = '{}' ALLOW FILTERING""".format(city,date))

    data = []

    for weather_point in weather_data:
        if weather_point['City'].lower() == city.lower() and weather_point['Date'] == date:
            data.append(weather_point)

    if len(data) == 0:
        return jsonify("Resource NOT FOUND!"), 404

    return jsonify(add_links(date=date, data=data, city=city)), 200

#returns the list of results and renders them in the browser as JSON.
def add_links(city, date, data):
    #host = socket.gethostname()
    host = get_ip()

    next_date = datetime.datetime.strptime(date, "%Y%m%d").date() + datetime.timedelta(days=1)
    previous_day = datetime.datetime.strptime(date, "%Y%m%d").date() + datetime.timedelta(days=-1)

    next_date_str = next_date.strftime("%Y%m%d")
    previous_day_str = previous_day.strftime("%Y%m%d")

# replace the hostname port number from application context
    next_link = requote_uri("http://{}:8080/weather/{}/{}".format(host,city, next_date_str))
    previous_link = requote_uri("http://{}:8080/weather/{}/{}".format(host,city, previous_day_str))

    result = {"links": [{"rel": "next_day", "href": next_link}, {"rel": "previous_day", "href": previous_link}],
              "data": data}
    return result


@app.route("/")
def home():
    # get customised weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    # get customised currency based on user input or default
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)
    return render_template("home.html", weather=weather,
                           currency_from=currency_from, currency_to=currency_to, rate=rate,
                           currencies=sorted(currencies))

def get_rate(frm, to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate / frm_rate, parsed.keys()

def get_weather(query):
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name'],
                   'country': parsed['sys']['country']
                   }
    return weather


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080, debug=False)
