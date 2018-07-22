from flask import Flask, render_template, redirect, request
from threading import Thread
import matplotlib.pyplot as plt
import requests, json, webbrowser

#define global variables. app = our server, historical_data is for backtesting
app = Flask(__name__)
message = ""
historical_data = []
x_values = []
y_values = []


def start():
    """
    Here we fetch historical data fromo cryptocompare and record it 
    in our global variable 'historical_data' for use by our backtester
    Then, we open up our browser to localhost:5000 where our server should
    respond with the HTML GUI
    """
    global historical_data
    print "Starting Crypto Bot V1" 
    data_url = 'https://min-api.cryptocompare.com/data/histominute' +\
          '?fsym=ETH' +\
          '&tsym=USD' +\
          '&limit=2000' +\
          '&aggregate=1'
    response = requests.get(data_url)
    data = response.json()['Data']
    historical_data = data
    print "Fetched historical data for ticker ETH. Opening GUI."
    webbrowser.open("http://127.0.0.1:5000")


@app.route("/")
def index():
    """
    When a request is made to the / endpoint of localhost, this function is called, responding
    with our HTML file
    """
    global message
    return render_template("index.html", message=message)


@app.route("/start_backtesting")
def start_backtesting():
    """
    When the user submits the form to start backtesting, this function can see what ticker the user chose and start our
    backtesting function in a seperate Thread. It then redirects the user back to the / endpoint where our index function
    handles the user's request from there.
    """
    global message
    data = request.form 
    ticker = str(data["ticker"])
    if ticker == "ETH":
        Thread(target=backtest_ethereum).start()
    message = "Backtesting ETH..."
    return redirect("localhost:5000")


if __name__ == "__main__":
    start()
    app.run()



