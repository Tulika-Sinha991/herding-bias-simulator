# file for data generation and statistics
# create dummy data for the stock market prices for 200 days
import numpy as np
import pandas as pd

# function to calculate true value/actual value of the stock
# prev_p= value of stock at the previous day
# mu= drift of stock market; sigma= volatility of stock market
def cal_t_value(prev_p,mu,sigma):
    z=np.random.normal()
    price=prev_p*(1+mu+(sigma*z))
    return round(price,2)

#function to calculate the herd bubble for market price spike on random day
def herd_bub(prev_p,beta,k,d):
    mkt_p=prev_p*(1+beta*(np.exp(k*d)))
    return round(mkt_p,2)

# main function to create dataframe for storing sock prices/market data
# starting price of stock at start of day 1 set to arbitrary value of 1000/-
# list true_price to store true prices of stock for every day
# list market_price to store market prices of stock for every day
def generate_md():
    days=list()
    true_price=list()
    market_price=list()
    start_p=1000
    for i in range(1,200):
        days.append(i)
        true_p=cal_t_value(start_p,0.001,0.02)
        true_price.append(true_p)

        # herd bubble triggered after a randomly selected day(day 40)
        # market value spikes at bubble
        if(i>40):
            value=herd_bub(true_p,0.05,0.1,i-40)
            market_price.append(value)

        else:
            market_price.append(true_p)

        start_p=true_p

    # creating dataframe to store computed data
    dataframe=pd.DataFrame({"day":days,
                            "true value":true_price,
                            "market value":market_price})
    return dataframe
