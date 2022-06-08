import sqlite3
from matplotlib import use
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

def five_line(data):   
    timetrend = list(range(1, data.shape[0]+1))
    data['timetrend'] = timetrend
    data = data[['timetrend','Close']]
    data = data.dropna()
    reg = LinearRegression()
    x = data['timetrend'].to_frame()
    y = data['Close'].to_frame()
    reg.fit(x,y)
    
    a = reg.intercept_ #截距
    beta = reg.coef_ #斜率
    longtrend = a + beta*x
    res = np.array(list(data['Close'])) - np.array(list(longtrend['timetrend']))
    std = np.std(res,ddof=1)
    fiveline = pd.DataFrame()
    fiveline['+2SD'] = longtrend['timetrend'] + (2*std)
    fiveline['+1SD'] = longtrend['timetrend'] + (1*std)
    fiveline['TL'] = longtrend['timetrend']
    fiveline['-1SD'] = longtrend['timetrend'] - (1*std)
    fiveline['-2SD'] = longtrend['timetrend'] - (2*std) 
    use_fiveline = pd.merge(data, fiveline[['+2SD','+1SD','TL','-1SD','-2SD']], left_index=True, right_index=True, how='left')
    pick_fiveline = use_fiveline[['Close','+2SD','+1SD','TL','-1SD','-2SD']]
    return pick_fiveline

def BBands(data): #布林通道，非樂活通道
    data_bb = data.copy()
    indicator_bb = ta.volatility.BollingerBands(close = data_bb['Close'], window = 20, window_dev = 2)
    data_bb['bbh'] = indicator_bb.bollinger_hband()
    data_bb['bbm'] = indicator_bb.bollinger_mavg()
    data_bb['bbl'] = indicator_bb.bollinger_lband()
    data_bb = data_bb.dropna()
    use_BBands = pd.merge(data, data_bb[['bbh','bbm','bbl']], left_index=True, right_index=True, how='left')
    pick_BBands = use_BBands[['bbh','bbm','bbl']]
    return pick_BBands

def KD(data):
    data_KD = data.copy()
    data_KD['min'] = data_KD['Low'].rolling(9).min()
    data_KD['max'] = data_KD['High'].rolling(9).max()
    data_KD['RSV'] = 100*(data_KD['Close'] - data_KD['min'])/(data_KD['max'] - data_KD['min'])
    data_KD = data_KD.dropna()

    K_list = [50]
    for num,rsv in enumerate(list(data_KD['RSV'])):
        K_yestarday = K_list[num]
        K_today = 2/3 * K_yestarday + 1/3 * rsv
        K_list.append(K_today)
    data_KD['K'] = K_list[1:]

    D_list = [50]
    for num,K in enumerate(list(data_KD['K'])):
        D_yestarday = D_list[num]
        D_today = 2/3 * D_yestarday + 1/3 * K
        D_list.append(D_today)
    data_KD['D'] = D_list[1:]
    use_KD = pd.merge(data, data_KD[['K','D']], left_index=True, right_index=True, how='left')
    pick_KD = use_KD[['K','D']]
    return pick_KD



ETF_list = ['0050','0051','0052']
for i in ETF_list:
    df = yf.download(f"{i}.TW", start = str(start), end = str(end))
    f = five_line(df)
    b = BBands(df)
    k = KD(df)
    merge_df = pd.merge(b,k, left_index=True, right_index=True, how='left')
    merge2_df = pd.merge(f, merge_df, left_index=True, right_index=True, how='left')
    merge2_df = merge2_df.dropna()
    merge2_df['Number'] = f'{i}'
    merge2_df['Date'] = merge2_df.index
    pick_df = merge2_df[['Date','Number','Close','+2SD','+1SD','TL','-1SD','-2SD','bbh','bbm','bbl','K','D']]
    #print(pick_df)
#'''
    conn = sqlite3.connect('ETF_list.db')  #建立資料庫
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE 'Strategy_data_{i}'(Date, Number, Close, '+2SD', '+1SD', TL, '-1SD', '-2SD', bbh, bbm, bbl, K, D)")  #建立資料表
    conn.commit()

    #如果資料表存在，就寫入資料，否則建立資料表
    pick_df.to_sql(f'Strategy_data_{i}', conn, if_exists='append', index=False) 
#'''
    