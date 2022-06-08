import pandas as pd
import sqlite3

df = pd.read_excel("ETF_list.xlsx")
conn = sqlite3.connect('ETF_list.db')  #建立資料庫
cursor = conn.cursor()
cursor.execute('''CREATE TABLE ETF_list(Type TEXT, Number TEXT PRIMARY KEY, Name TEXT);''')
#cursor.execute('CREATE TABLE ETF_list1(Type, Number, Name);')  #建立資料表
conn.commit()
#conn.close()

#如果資料表存在，就寫入資料，否則建立資料表
df.to_sql('ETF_list', conn, if_exists='append', index=False)