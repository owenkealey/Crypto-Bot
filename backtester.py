from flask import Flask, render_template, redirect, request
from threading import Thread
import matplotlib.pyplot as plt
import requests, json, webbrowser

#define global variables. app = our server, historical_data is for backtesting
app = Flask(__name__)
message = ""
historical_data = []


def start():
    """
    Here we fetch historical data from cryptocompare and record it 
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


def plot_graph(x, y):
    plt.plot(x, y)
    plt.xlabel("Day")
    plt.ylabel("Portfolio Value")
    plt.show()


def get_average(averages_list):
    total = 0 
    for data_set in averages_list:
        total += float(data_set["close"])
    return total/len(averages_list)


def moving_averages():
    """
    If the 3 day average price of ETH is above the 5 day average price, buy. If below, sell.
    """
    global message
    ethereum = 0
    cash = 10000
    x_values = []
    y_values = []
    for place, data_set in enumerate(historical_data[10:-1]):
        three_day_average = get_average([historical_data[place-1], historical_data[place-2], historical_data[place-3]])
        five_day_average = get_average([historical_data[place-1], 
                                       historical_data[place-2],
                                       historical_data[place-3],
                                       historical_data[place-4],
                                       historical_data[place-5]])
        if three_day_average > five_day_average:
            cash_used_to_buy = cash/2
            price = float(data_set["close"])
            number_of_ethereum_we_just_bought = cash_used_to_buy/price
            ethereum += number_of_ethereum_we_just_bought
            cash -= cash_used_to_buy
            print "Just bought: " + str(number_of_ethereum_we_just_bought) + " Ethereum!"
        if ethereum > 1 and three_day_average < five_day_average:
            price = float(data_set["close"])
            number_of_ethereum_being_sold = ethereum/2
            new_cash = number_of_ethereum_being_sold * price
            cash += new_cash
            ethereum -= number_of_ethereum_being_sold
            print "Just sold: " + str(number_of_ethereum_being_sold) + " Ethereum!"
        portfolio_value = cash + (ethereum * float(data_set["close"]))
        x_values.append(place)
        y_values.append(portfolio_value)
    message = "Backtest Complete!"
    print "Final portfolio value:" + str(portfolio_value)
    plot_graph(x_values, y_values)


def backtest_ethereum(strategy):
    if int(strategy) == 1:
        moving_averages()


@app.route("/")
def index():
    """
    When a request is made to the / endpoint of localhost, this function is called, responding
    with our HTML file
    """
    global message
    return render_template("index.html", message=message)


@app.route("/start_backtesting", methods=["POST"])
def start_backtesting():
    """
    When the user submits the form to start backtesting, this function can see what ticker the user chose and start our
    backtesting function in a seperate Thread. It then redirects the user back to the / endpoint where our index function
    handles the user's request from there.
    """
    global message
    data = request.form 
    ticker = str(data["ticker"])
    strategy = str(data["strategy"])
    if ticker == "ETH":
        Thread(target=backtest_ethereum, kwargs={"strategy":strategy}).start()
    message = "Backtesting ETH..."
    return redirect("http://127.0.0.1:5000")


if __name__ == "__main__":
    start()
    app.run()



