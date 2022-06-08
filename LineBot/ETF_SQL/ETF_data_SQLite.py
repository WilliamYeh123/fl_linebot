import sqlite3, time
from pandas.io import sql
import yfinance as yf
import ta
import requests
import pandas as pd
import numpy as np
import datetime,time,re
import mplfinance as mpf
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression

dict_from_ETF_list = pd.read_excel("ETF_list.xlsx")
ETF_list = dict_from_ETF_list['Number']

today = datetime.date.today()
end = today - datetime.timedelta(days=1)
start = end - datetime.timedelta(days=365*3.5)

#"""
conn = sqlite3.connect('ETF_list.db')
cursor = conn.cursor()


conn.execute('''CREATE TABLE if not exists ETF_data
       (Date date ,
       Number TEXT ,
       Open FLOAT,
       High FLOAT,
       Low FLOAT,
       Close FLOAT,
       Volume TEXT,
       primary key (Date, Number));''')
conn.commit()
#"""

ETF_list = ['0050']
for i in ETF_list:
    df = yf.download(f"{i}.TW", start = str(start), end = str(end))
    df['Number'] = f'{i}'
    df['Date'] = df.index.strftime("%Y-%m-%d")
    pick_df = df[['Date', 'Number','Open', 'High', 'Low', 'Close', 'Volume']]

    #print(pick_df.index)
    #print(pick_df)
    #print('股票：',i, pick_df)
    
    pick_df['Volume'] = pick_df['Volume'].map('{}'.format)

    #print(tuple(pick_df.iloc[0]))
    #print(len(pick_df))

    for i in range(len(pick_df)):
        #pick_df[i][6] = pick_df[i][6].astype(str)
        print(type(pick_df.iloc[i][6]))
        cursor.execute('insert into ETF_data(Date, Number, Open, High, Low, Close, Volume) VALUES (?, ?, ?, ?, ?, ?, ?)', tuple(pick_df.iloc[i]))
        conn.commit()
        #(pick_df[0][0], pick_df[0][1], ,,,)

"""
    conn = sqlite3.connect('ETF_list.db')  #建立資料庫
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE 'ETF_data_{i}'(Date, Number, Open, High, Low, Close, Volume)")  #建立資料表
    conn.commit()

    #如果資料表存在，就寫入資料，否則建立資料表
    pick_df.to_sql(f'ETF_data_{i}', conn, if_exists='append', index=False) 
"""

sql = "select * from ETF_data where Date = ? and Number = ?"
cursor.execute(sql, ('2018-12-03', '0050'))
rows = cursor.fetchall()
