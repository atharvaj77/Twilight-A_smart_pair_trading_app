import streamlit as st
from streamlit_login_auth_ui.widgets import __login__
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from math import floor
from termcolor import colored as cl
import pandas_datareader as data
import pandas as pd
import streamlit as st
from datetime import date
import streamlit as st
from streamlit_login_auth_ui.widgets import __login__

__login__obj = __login__(auth_token = "courier_auth_token", 
                    company_name = "Shims",
                    width = 200, height = 250, 
                    logout_button_name = 'Logout', hide_menu_bool = False, 
                    hide_footer_bool = False, 
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()


if LOGGED_IN == True:

     # Stack Rank
    st.subheader("Stack Rank Of 50 Stocks")
    df = pd.read_excel("stackranks.xlsx")
    st.write(df)

    # Taking Input
    st.title("Pair Trading Strategy")
    st.subheader("Enter the start date")
    start = st.date_input("", date(2013, 1, 1))
    end = date.today()

    stock1 = st.text_input("Enter the stock ticker", "SBIN.NS", key="1")
    stock2 = st.text_input("Enter the stock ticker", "SBIN.NS", key="2")
    stock = '^NSEI'
    nifty = data.DataReader(stock, 'yahoo', start, end)
    s1 = data.DataReader(stock1, 'yahoo', start, end)
    s2 = data.DataReader(stock2, 'yahoo', start, end)

    st.subheader(
        f"closing price vs time chart MAX for {stock1}, {stock2}")
    fig = plt.figure(figsize=(12, 6))
    plt.plot(s1.Close, color='orange', linewidth=2, label=stock1)
    plt.plot(s2.Close, color='blue', linewidth=2, label=stock2)
    plt.legend(loc='upper left')
    st.pyplot(fig)

    # --------------------------------------------------------------------------------------
    # Printing Ratio & Supertrend

    def get_supertrend(high, low, close, lookback, multiplier):

        # ATR

        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
        atr = tr.ewm(lookback).mean()

        # H/L AVG AND BASIC UPPER & LOWER BAND

        hl_avg = (high + low) / 2
        upper_band = (hl_avg + multiplier * atr).dropna()
        lower_band = (hl_avg - multiplier * atr).dropna()

        # FINAL UPPER BAND
        final_bands = pd.DataFrame(columns=['upper', 'lower'])
        final_bands.iloc[:, 0] = [x for x in upper_band - upper_band]
        final_bands.iloc[:, 1] = final_bands.iloc[:, 0]
        for i in range(len(final_bands)):
            if i == 0:
                final_bands.iloc[i, 0] = 0
            else:
                if (upper_band[i] < final_bands.iloc[i-1, 0]) | (close[i-1] > final_bands.iloc[i-1, 0]):
                    final_bands.iloc[i, 0] = upper_band[i]
                else:
                    final_bands.iloc[i, 0] = final_bands.iloc[i-1, 0]

        # FINAL LOWER BAND

        for i in range(len(final_bands)):
            if i == 0:
                final_bands.iloc[i, 1] = 0
            else:
                if (lower_band[i] > final_bands.iloc[i-1, 1]) | (close[i-1] < final_bands.iloc[i-1, 1]):
                    final_bands.iloc[i, 1] = lower_band[i]
                else:
                    final_bands.iloc[i, 1] = final_bands.iloc[i-1, 1]

        # SUPERTREND

        supertrend = pd.DataFrame(columns=[f'supertrend_{lookback}'])
        supertrend.iloc[:, 0] = [
            x for x in final_bands['upper'] - final_bands['upper']]

        for i in range(len(supertrend)):
            if i == 0:
                supertrend.iloc[i, 0] = 0
            elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 0] and close[i] < final_bands.iloc[i, 0]:
                supertrend.iloc[i, 0] = final_bands.iloc[i, 0]
            elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 0] and close[i] > final_bands.iloc[i, 0]:
                supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
            elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 1] and close[i] > final_bands.iloc[i, 1]:
                supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
            elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 1] and close[i] < final_bands.iloc[i, 1]:
                supertrend.iloc[i, 0] = final_bands.iloc[i, 0]

        supertrend = supertrend.set_index(upper_band.index)
        supertrend = supertrend.dropna()[1:]

        # ST UPTREND/DOWNTREND

        upt = []
        dt = []
        close = close.iloc[len(close) - len(supertrend):]

        for i in range(len(supertrend)):
            if close[i] > supertrend.iloc[i, 0]:
                upt.append(supertrend.iloc[i, 0])
                dt.append(np.nan)
            elif close[i] < supertrend.iloc[i, 0]:
                upt.append(np.nan)
                dt.append(supertrend.iloc[i, 0])
            else:
                upt.append(np.nan)
                dt.append(np.nan)

        st, upt, dt = pd.Series(
            supertrend.iloc[:, 0]), pd.Series(upt), pd.Series(dt)
        upt.index, dt.index = supertrend.index, supertrend.index

        return st, upt, dt

    ratio = pd.DataFrame()
    ratio['st'], ratio['s_upt'], ratio['st_dt'] = get_supertrend(
        s1['High']/s2['High'], s1['Low']/s2['Low'], s1['Close']/s2['Close'], 10, 3)
    ratio = ratio[1:]
    st.subheader(f"Supertrend of ratio of {stock1} and {stock2}")
    st.write(ratio)

    fig = plt.figure(figsize=(12, 6))
    plt.plot(ratio['s_upt'], color='green',
             linewidth=2, label='ST UPTREND 10,3')
    plt.plot(ratio['st_dt'], color='r', linewidth=2, label='ST DOWNTREND 10,3')
    plt.legend(loc='upper left')
    plt.show()
    st.pyplot(fig)

    # ----------------------------------------------------------------------------------------
    # Printing Relative Strength

    def get_rsi(series, period):
        delta = series.diff().dropna()
        u = delta * 0
        d = u.copy()
        u[delta > 0] = delta[delta > 0]
        d[delta < 0] = -delta[delta < 0]
        u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
        u = u.drop(u.index[:(period-1)])
        d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
        d = d.drop(d.index[:(period-1)])
        rs = pd.DataFrame.ewm(u, com=period-1, adjust=False).mean() / \
            pd.DataFrame.ewm(d, com=period-1, adjust=False).mean()
        return 100-100/(1+rs)

   
    s1['rsi'] = get_rsi(s1['Close'], 14)
    s2['rsi'] = get_rsi(s2['Close'], 14)
    ratio['rsi']=get_rsi(s1['Close']/s2['Close'], 14)
    fig = plt.figure(figsize=(12, 6))
    plt.plot(s1['rsi'], color='green', linewidth=2,
             label=f'Relative Strength of {stock1}')
    plt.plot(s2['rsi'], color='r', linewidth=2,
             label=f'Relative Strength of {stock2}')

    plt.legend(loc='upper left')
    plt.show()
    st.pyplot(fig)
    # -------------------------------------------------------------------------------------
    # Printing Profit

    def entry(long, short, count, i):
        long_entry = long['Close'][i]
        short_entry = short['Close'][i]
        stop_loss1 = -0.05*long_entry
        stop_loss2 = -0.05*short_entry
        max_profit1 = 0.05*long_entry
        max_profit2 = 0.05*short_entry
        counter = 0
        profit1 = long['Close'][i+1]-long_entry
        profit2 = short_entry-short['Close'][i+1]
        while counter < 5 and profit1 <= stop_loss1 and profit2 <= stop_loss2 and profit1 <= max_profit1 and profit2 <= max_profit2:
            counter += 1
            profit1 = long['Close'][i+counter+1]-long_entry
            profit2 = short['Close'][i+1+counter]-short_entry
        count = counter

    #     print(i)
    #     print('----------------------------------------------------------------')
    #     print(long['Close'][i+counter+1])
    #     print('----------------------------------------------------------------')

        return (500000/(long_entry))*profit1+profit2*(500000/(short['Close'][i+1+counter])), counter

    # Backtesting

    def entry(long,short,count,i):
    
        long_entry=long['Close'][i]
        short_entry=short['Close'][i]
    #     print(f"Long entry {long_entry}")
    #     print(f"Short entry {short_entry}")
        stop_loss1=-0.05*long_entry
        stop_loss2=-0.05*short_entry
        max_profit1=0.05*long_entry
        max_profit2=0.05*short_entry
        temp_i=i
        counter=0
        profit1=long['Close'][i+1]-long_entry
        profit2=short_entry-short['Close'][i+1]
        while counter<5 and profit1>=stop_loss1 and profit2>=stop_loss2 and profit1<=max_profit1 and profit2<=max_profit2:
            
            profit1=long['Close'][i+counter+1]-long_entry
            profit2=short_entry-short['Close'][i+1+counter]
            # print(profit1)
            # print(profit2)
            counter+=1
        count=counter
        endate=str(long.index[temp_i])[:10]
        exdate=str(long.index[i+count+1])[:10]
        
        l=[endate,exdate]

        proft=(100000/(long_entry))*profit1+profit2*(100000/(short['Close'][i+1+counter]))
        return proft,count,l

    def backtesting(ratio,s1,s2):
        l=[]
        profit=0
        i=0
        while i<len(s1)-6:
            if ratio['st_dt'][i]>0 and ratio['rsi'][i]>=50:
                pf,count,li=entry(s1,s2,0,i)
                i+=count
                profit+=pf
                l.append(li)
                
            elif ratio['s_upt'][i]>0 and ratio['rsi'][i]<=50:
                pf,count,li=entry(s2,s1,0,i)
                profit+=pf
                i+=count
                l.append(li)
            i+=1
        
        
        return profit,l
    profit,l=backtesting(ratio,s1,s2)
    st.subheader(
        f"The Profit Generated By This pair is:{profit} ")
    st.subheader(
        f"Following are the entry and exit dates:")
    for i in range(len(l)):
        # original_title1 = '<p style="font-family:Courier; color:White; font-size: 12px;">Entry Date is:</p>'
        # original_title2= '<p style="font-family:Courier; color:Blue; font-size: 12px;"> {l[i][0]} </p>'
        # original_title3 = '<p style="font-family:Courier; color:White; font-size: 12px;"> and Exit Date is: </p>'
        # original_title4 = '<p style="font-family:Courier; color:Blue; font-size: 12px;"> {l[i][1]}</p>'
        
        # st.markdown(original_title1, unsafe_allow_html=True)
        # st.markdown(original_title1, unsafe_allow_html=True)
        # st.markdown(original_title1, unsafe_allow_html=True)
        # st.markdown(original_title1, unsafe_allow_html=True)
        st.write(f'Entry Date is: {l[i][0]} and Exit Date is: {l[i][1]}')

    # st.write(l)
    # ----------------------------------------------------------------------------
   