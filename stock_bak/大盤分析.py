#載入
import sqlite3
import pandas as pd
import numpy as np
import datetime
import time
from os import listdir
from os.path import isfile, isdir, join
import os
import talib as tb
import talib.abstract as tbab
import math #判斷nan值用
import csv
import requests
import json
import time
from bs4 import BeautifulSoup
conn = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\TSE.db')
c = conn.cursor()
conn_s = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\stock_db.db')
c_s = conn_s.cursor()
conn_t = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\taifex.db')
c_t = conn_t.cursor()
conn_b = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\bigdeal.db')
c_b = conn_b.cursor()


#篩選function
def fill_nan(df): #填充nan值 大量會無法使用
    col_list = list(df) #欄位名稱
    for col_name in col_list:
        isnull_data = df.isnull()[col_name]
        isnull_index = df[isnull_data].index.tolist() #提取NULL 的Index
        for i in isnull_index:
            while_plus = 1 #同上一筆資料、或上上筆 類推
            while str(df.loc[i][col_name]) == 'nan': #只要是nan 則填如上其數字
                try:
                    df.at[i, col_name] = df.loc[i-while_plus][col_name] #修改df 的值
                except: #第一列沒有填0
                    df.at[i, col_name] = 0
                while_plus = while_plus + 1

    return df
def rsi_back(target_date,input_file): #
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,收盤指數 FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        if len(foundindex):    
            ok_data = fill_nan(data)
            rsi_val = tb.RSI(ok_data['收盤指數'],timeperiod = 5)
            cal_day = 20 #鎖定20天內的資料
            if ok_data['收盤指數'][foundindex[0]] == ok_data['收盤指數'][foundindex[0]+1-cal_day:foundindex[0]+1].max(): #當天創新高
                ans = rsi_val[foundindex[0]] == rsi_val[foundindex[0]+1-cal_day:foundindex[0]+1].max() #RSI 是否也創新高
                if ans == False:
                    got.append({'stock':f,'signal':'賣出訊號'})
                    #pass
            elif ok_data['收盤指數'][foundindex[0]] == ok_data['收盤指數'][foundindex[0]+1-cal_day:foundindex[0]+1].min(): #當天創新高
                ans = rsi_val[foundindex[0]] == rsi_val[foundindex[0]+1-cal_day:foundindex[0]+1].min() #RSI 是否也創新高
                if ans == False:
                    got.append({'stock':f,'signal':'買進訊號'})
    return got

def avgclose(target_date,input_file):#前三天股價漲跌(包括今天-前天)
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,收盤指數 FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        try:
            if len(foundindex):  
                ok_data = fill_nan(data)  
                data1 = ok_data['收盤指數'][foundindex[0]-0]
                data5 = ok_data['收盤指數'][foundindex[0]-4]
                got.append({'stock':f,'grow':data1-data5})
        except:
            pass
    return got

def ma5biger(target_date,input_file): #ma5 在上
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,收盤指數 FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        if len(foundindex):   
            ok_data = fill_nan(data)['收盤指數']
            ma_5 = tb.MA(ok_data,timeperiod = 5)[foundindex[0]]#計算五日MA 並取出當日值
            ma_20 = tb.MA(ok_data,timeperiod = 20)[foundindex[0]] #計算20日MA 並取出當日值
            if ma_5 > ma_20:#如果五日大於20日
                #print(f,ma_5,ma_20)
                got.append({'stock':f,'ma5':'在上'})
        #break
            if ma_5 < ma_20:#如果五日小於20日
                #print(f,ma_5,ma_20)
                got.append({'stock':f,"ma5":'在下'})
    return got

def updown(target_date,input_file): #一個月內是否有震盪
    day = 15#幾天內的資料
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,收盤指數 FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        if len(foundindex):   
            ok_data = fill_nan(data)['收盤指數']
            ma_5 = tb.MA(ok_data,timeperiod = 5)#計算五日MA 
            ma_20 = tb.MA(ok_data,timeperiod = 20) #計算20日MA
            ma_ary = [] #ma5 與20的差
            down = 0
            grow = 0
            for d in  range(0,day): 
                ma_ary.append(ma_5[foundindex[0]-d]-ma_20[foundindex[0]-d])
            for i in ma_ary: #驗證ma5 是否都在ma20 之上
                if i < 0:
                    down = 1
            for i in ma_ary: #驗證ma5 是否都在ma20 之下
                if i > 0:
                    grow = 1
            if down == 1 and grow == 1: #這個月有之下也有之上的代表震盪
                got.append({'stock':f,"ma":'震盪'})
            elif down == 1 and grow == 0: #這個月有之下也有之上的代表震盪
                got.append({'stock':f,"ma":'跌勢'})
            elif down == 0 and grow == 1: #這個月有之下也有之上的代表震盪
                got.append({'stock':f,"ma":'漲勢'})
                


    return got

def ma_buy(target_date,input_file): #非常不准
    got = []
    cc = 0
    for f in input_file:
        
        data = pd.read_sql_query('SELECT date,收盤指數 FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        if len(foundindex):   
            ok_data = fill_nan(data)['收盤指數']
            ma_5 = tb.MA(ok_data,timeperiod = 5)#計算五日MA 
            ma_10 = tb.MA(ok_data,timeperiod = 10) #計算10日MA
            ma_20 = tb.MA(ok_data,timeperiod = 20) #計算20日MA
            close = pd.read_sql_query('SELECT date,收盤指數 FROM "'+ f +'" WHERE date = '+str(target_date)+';', conn).iloc[0,1]
            got.append({'stock':f,"ma":'未分析'})
            if (ma_5[foundindex[0]] - ma_20[foundindex[0]]) >0: #漲勢
                if close <= ma_5[foundindex[0]]:
                    got[cc]["ma"] = 'ma5買進訊號'
                    
                if close <= ma_10[foundindex[0]]:
                    got[cc]["ma"] = 'ma10買進訊號'
                    
                if close <= ma_20[foundindex[0]]:
                    got[cc]["ma"] = 'ma20買進訊號'
                    pass
            elif (ma_5[foundindex[0]] - ma_20[foundindex[0]]) <0: #跌勢
                if close >= ma_5[foundindex[0]]:
                    got[cc]["ma"] = 'ma5賣出訊號'
                if close >= ma_10[foundindex[0]]:
                    got[cc]["ma"] = 'ma10賣出訊號'
                if close >= ma_20[foundindex[0]]:
                    got[cc]["ma"] = 'ma20賣出訊號'
                    pass
            if got[cc]["ma"] == '未分析':
                got[cc]["ma"] = '無買賣訊號'
                    
        cc += 1 #記數加1 判斷用
    return got

def macdbuy(target_date,input_file):
    got = []
    cc = 0
    for f in input_file:
        
        data = pd.read_sql_query('SELECT date,收盤指數 FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        if len(foundindex):   
            ok_data = fill_nan(data)['收盤指數']
            macd_data = tb.MACD(ok_data)
            osc1 = macd_data[2][foundindex[0]]
            osc2 = macd_data[2][foundindex[0]-1]
            osc3 =  macd_data[2][foundindex[0]-2]
            goin = 0
            if osc2>osc3:#上漲反轉
                if osc1 < osc2: 
                    goin = 1
                    got.append({'stock':f,"macd_osc":'賣出訊號'})
            elif osc2<osc3:#下跌反轉
                if osc1 > osc2: 
                    goin = 1
                    got.append({'stock':f,"macd_osc":'買進訊號'})
            
            if goin == 0:
                got.append({'stock':f,"macd_osc":'無買賣訊號'})
    return got


#判斷當天買進訊號
stock_code = "^TWII"
url = "https://tw.stock.yahoo.com/q/q?s="+stock_code
my_headers = {'Cache-Control': 'no-cache','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
gotrq = requests.get(url,headers = my_headers)
soup = BeautifulSoup(gotrq.text, "html.parser") #"html.parser" html解析器 將html 轉為bs4格式操作
target_table = soup.select('table')[2]
data_val = target_table.select('td')[2].text

point = data_val #當天指數

today_str = int(time.strftime("%Y%m%d"))
#today_str = 20190422
c.execute('INSERT OR REPLACE INTO "發行量加權股價指數" VALUES('+ str(today_str) +','+str(point)+',null,null,null,null,null,null,null,null,null);')
#today_str = 20190329
close_date = pd.read_sql_query('SELECT date,收盤指數 FROM "發行量加權股價指數";', conn)["date"]
date_f = [] #交易日ARY
for i in close_date:
    date_f.append(i)
yes_index = date_f.index(today_str)-1
yest_int = date_f[yes_index]
def detect(today_str):
    rsi = rsi_back(today_str,["發行量加權股價指數"])
    avg = avgclose(today_str,["發行量加權股價指數"])
    ma5_ma20 = ma5biger(today_str,["發行量加權股價指數"])
    up_down = updown(today_str,["發行量加權股價指數"])
    ma_signal = ma_buy(today_str,["發行量加權股價指數"])
    macd_signal = macdbuy(today_str,["發行量加權股價指數"])
    got = [today_str]
    if rsi != []: #RSI 有訊號
        got.append('rsi'+rsi[0]['signal'])

    #if avg[0]['grow'] >= 50 or avg[0]['grow']*-1 >= 50: #平盤訊號 (暫時刪除)
    if 1 == 1: #平盤訊號 (暫時刪除)
        if up_down[0]['ma'] != '震盪': #不等於震盪
            if ma_signal[0]['ma'] != "無買賣訊號":
                got.append('均線操作:'+ma_signal[0]['ma'])
        else: #震盪
            if macd_signal[0]['macd_osc'] != "無買賣訊號":
                got.append('MACD操作:'+macd_signal[0]['macd_osc'])
    else:
        pass
    print(got)
    



detect(yest_int)
detect(today_str)
print(point)