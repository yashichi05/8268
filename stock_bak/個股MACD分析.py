import sqlite3
import pandas as pd
import numpy as np
import talib as tb
import requests
import json
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import mpl_finance as mpf
import datetime as datetime
import talib






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
conn = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\stock_db.db')
c = conn.cursor()

conn_b = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\bigdeal.db')
c_b = conn_b.cursor()

table_name = [] #所有股號
for i in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    table_name.append(i[0])


def grow(target_date,target_date2,percent,input_file): #漲跌幅 (今天,昨天,%數,股號陣列)
    got = []
    for f in input_file:

        try:
            data1 = pd.read_sql_query('SELECT date,close FROM "'+ f +'" WHERE date ='+str(target_date)+';', conn)['close'][0]
            data2 = pd.read_sql_query('SELECT date,close FROM "'+ f +'" WHERE date ='+str(target_date2)+';', conn)['close'][0]
            if ((data1/data2-1)*100) > percent and percent > 0:
                got.append(f)
            elif ((data1/data2-1)*100) < percent and percent < 0:
                got.append(f)
        except:
            pass
    return got
def find_vol_bigger(target_date,input_file): #(日期,搜尋股號陣列) 計算今日成交量是否大於昨日兩倍
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,vol FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列形式
        if len(foundindex): #如果有找到目標日期
            try: #如果沒有昨天的資料 會錯誤
                todayvol = data['vol'][foundindex[0]] #當天成交量資料
                yestervol = data['vol'][foundindex[0]-5]+data['vol'][foundindex[0]-4]+data['vol'][foundindex[0]-3]+data['vol'][foundindex[0]-2]+data['vol'][foundindex[0]-1] #5天前平均成交量資料
                if todayvol > yestervol/5*2 and todayvol>1000*1000: #計算今日成交量是否大於昨日兩倍 #成交量大於1000張
                    got.append(f) #是 則加入陣列
            except:
                pass
        #break
    return got

def priceHighest(target_date,input_file): #半月最高價
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index
        if len(foundindex):
            #ok_data = fill_nan(data)['close'] #去掉NAN
            ok_data = data['close']
            if ok_data[foundindex[0]-10:foundindex[0]+1].max() == ok_data[foundindex[0]]:#
                got.append(f)
        #break
    return got

def price(target_date,input_file): #價格小於40
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index
        if len(foundindex):
            #ok_data = fill_nan(data)['close'] #去掉NAN
            ok_data = data['close']
            if ok_data[foundindex[0]]<40:#
                got.append(f)
        #break
    return got


def ma5biger(target_date,input_file): #ma5 在上
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        if len(foundindex):   
            ok_data = fill_nan(data)['close']
            ma_5 = tb.MA(ok_data,timeperiod = 5)[foundindex[0]]#計算五日MA 並取出當日值
            ma_20 = tb.MA(ok_data,timeperiod = 20)[foundindex[0]] #計算20日MA 並取出當日值
            if ma_5 > ma_20:#如果五日大於20日
                #print(f,ma_5,ma_20)
                got.append(f)
        #break
    return got


def rsi_back(target_date,input_file): #
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        if len(foundindex):    
            ok_data = fill_nan(data)
            rsi_val = tb.RSI(ok_data['close'],timeperiod = 5)
            cal_day = 20 #鎖定20天內的資料
            if ok_data['close'][foundindex[0]] == ok_data['close'][foundindex[0]+1-cal_day:foundindex[0]+1].max(): #當天創新高
                ans = rsi_val[foundindex[0]] == rsi_val[foundindex[0]+1-cal_day:foundindex[0]+1].max() #RSI 是否也創新高
                if ans == False:
                    got.append(f)
                    #pass
            elif ok_data['close'][foundindex[0]] == ok_data['close'][foundindex[0]+1-cal_day:foundindex[0]+1].min(): #當天創新高
                ans = rsi_val[foundindex[0]] == rsi_val[foundindex[0]+1-cal_day:foundindex[0]+1].min() #RSI 是否也創新高
                if ans == False:
                    got.append(f)
                

    return got

def volbig(target_date,nu,input_file): #成交量大於
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close FROM "'+ f +'" WHERE date ='+str(target_date)+' AND vol > '+str(nu*1000)+';', conn)
        if len(data)> 0:
            got.append(f)

    return got

def bigboybuy(target_date,input_file):#法人5日買超
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,三大法人買賣超股數 FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        try:
            if len(foundindex):  
                ok_data = fill_nan(data)  
                data1 = ok_data['三大法人買賣超股數'][foundindex[0]-0]
                data2 = ok_data['三大法人買賣超股數'][foundindex[0]-1]
                data3 = ok_data['三大法人買賣超股數'][foundindex[0]-2]
                data4 = ok_data['三大法人買賣超股數'][foundindex[0]-3]
                data5 = ok_data['三大法人買賣超股數'][foundindex[0]-4]
                if (data1 + data2 +data3 +data4 +data5)>0 :
                    got.append(f)
        except:
            pass
    return got

def avgclose(target_date,input_file):#前三天股價漲跌(包括今天-前天)
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        try:
            if len(foundindex):  
                ok_data = fill_nan(data)  
                data1 = ok_data['close'][foundindex[0]-0]
                data5 = ok_data['close'][foundindex[0]-6]
                got.append({'stock':f,'grow':(data1/data5-1)*100})
        except:
            pass
    return got

def downbutbuy(target_date,input_file): #法人賣超 但是 股價上漲
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close,三大法人買賣超股數 FROM "'+ f +'" where date = '+str(target_date)+' and upprice > 0 and "三大法人買賣超股數" < 0;', conn)

        try:
            if len(data):  
                got.append(f)
        except:
            pass
    return got

def pricedownma5(target_date,input_file): #價格ma5之下
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        if len(foundindex):   
            ok_data = fill_nan(data)['close']
            ma_5 = tb.MA(ok_data,timeperiod = 5)[foundindex[0]]#計算五日MA 並取出當日值
            if ma_5 > ok_data[foundindex[0]]:
                #print(f,ma_5,ma_20)
                got.append(f)
        #break
    return got

def macddouble(target_date,input_file): #macd 兩次在上 已回漲
    got = []
    day_cal = 20 #計算時間
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close,low FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        target_date_index = foundindex[0]
        if len(foundindex):   
            ok_data = fill_nan(data)['low']
            macd_data = tb.MACD(ok_data,fastperiod=12, slowperiod=26, signalperiod=9)[2]#計算MACD OSC
            for i in range(0,20):
                try:
                    torf = True #是否符合 OSC 皆為正 初始直
            #        for i in range(0,day_cal): #是否為正
            #            if macd_data[target_date_index-i] < -0.1:
            #                torf = False
            #                break#不是則跳出
                except:
                    torf = False

            if torf: #如果皆為正
                double_state = 0 #峰型幾次初始直
                for i in range(0,day_cal): #峰型 及 目前下降
                     if macd_data[target_date_index-1] < macd_data[target_date_index-2] and macd_data[target_date_index] > macd_data[target_date_index-1] and macd_data[target_date_index-i] < macd_data[target_date_index-i-1] and macd_data[target_date_index-i-1]> macd_data[target_date_index-i-2]:
                        double_state += 1
                if double_state >= 1: #雙峰 返回符合條件資料
                    got.append(f)
        #break
    return got

def macddouble_not(target_date,input_file): #macd 兩次在上 未回漲
    got = []
    day_cal = 20 #計算時間
    for f in input_file:
        data = pd.read_sql_query('SELECT date,close FROM "'+ f +'";', conn)
        found = data['date'] == target_date #搜尋第0欄，目標日期資料    
        foundindex = data[found].index.tolist() #data 顯示找到的結果 所在的index 陣列
        target_date_index = foundindex[0]
        if len(foundindex):   
            ok_data = fill_nan(data)['close']
            macd_data = tb.MACD(ok_data,fastperiod=12, slowperiod=26, signalperiod=9)[2]#計算MACD OSC
            for i in range(0,20):
                try:
                    torf = True #是否符合 OSC 皆為正 初始直
            #        for i in range(0,day_cal): #是否為正
            #            if macd_data[target_date_index-i] < -0.1:
            #                torf = False
            #                break#不是則跳出
                except:
                    torf = False

            if torf: #如果皆為正
                double_state = 0 #峰型幾次初始直
                for i in range(0,day_cal): #峰型 及 目前下降
                     if macd_data[target_date_index] < macd_data[target_date_index-1] and macd_data[target_date_index-i] < macd_data[target_date_index-i-1] and macd_data[target_date_index-i-1]> macd_data[target_date_index-i-2]:
                        double_state += 1
                if double_state >= 1: #雙峰 返回符合條件資料
                    got.append(f)
        #break
    return got
def bigbuy(target_date,input_file): #法人買超
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT * FROM "'+ f +'" where date = '+str(target_date)+';', conn)

        try:
            if len(data):  
                if data['外陸資買賣超股數(不含外資自營商)'][0]>0 or data['投信買賣超股數'][0]>0:
                    got.append(f)
        except:
            pass
    return got
#取得及時股價 並加入暫時加入資料庫
def simulation(target_date,input_file):
    for stock_code in input_file:
        try:
            url = "https://tw.stock.yahoo.com/q/q?s="+stock_code
            my_headers = {'Cache-Control': 'no-cache','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            gotrq = requests.get(url,headers = my_headers)
            soup = BeautifulSoup(gotrq.text, "html.parser") #"html.parser" html解析器 將html 轉為bs4格式操作
            target_table = soup.select('table')[2]
            data_val1 = target_table.select('td')[2].text#最新價
            data_val2 = target_table.select('td')[8].text#開
            data_val3 = target_table.select('td')[9].text#高
            data_val4 = target_table.select('td')[10].text#低
            c.execute('INSERT OR REPLACE INTO "'+ stock_code +'" ("date","close","open","high","low") VALUES ('+ str(target_date) +','+ str(data_val1) +','+ str(data_val2)+','+ str(data_val3)+','+ str(data_val4)+');')
        except:
            print(stock_code)
            c.execute('INSERT OR REPLACE INTO "'+ stock_code +'" ("date","close") VALUES ('+ str(target_date) +','+ str(0) +');')

def bigboybuy_oneday(target_date,input_file):#法人單日買超
    got = []
    for f in input_file:
        data = pd.read_sql_query('SELECT date,三大法人買賣超股數 FROM "'+ f +'" where date = '+ str(target_date) +';', conn)
        try:
            if data["三大法人買賣超股數"][0]>0:
                got.append(f)
        except:
            pass
    return got
def draw(target_date,stock):
    date_ary = pd.read_sql_query('SELECT date FROM "0050";', conn)["date"].tolist()
    target_index = date_ary.index(target_date)-60
    data_t =  pd.read_sql_query('SELECT * FROM "'+ stock+'" WHERE date >='+ str(date_ary[target_index]) +' and date <='+str(target_date)+';', conn)
    data_t.index = data_t['date']
    plt.rc('font',family='DFKai-SB')


    sma_5 = tb.SMA(np.array(data_t['close']), 5)
    sma_20 = tb.SMA(np.array(data_t['close']), 20)
    data_t_macd = talib.MACD(data_t['close'])
    data_t_rsi = talib.RSI(data_t['close'])
    
    fig = plt.figure(figsize=(24, 18))
    fig.suptitle(stock, fontsize=48)
    ax = fig.add_axes([0,0.6,1,0.4])
    ax3 = fig.add_axes([0,0.5,1,0.1])
    ax4 = fig.add_axes([0,0.25,1,0.25])
    ax2 = fig.add_axes([0,0,1,0.25])

    ax.set_xticks(range(0, len(data_t.index), 3))
    ax.set_xticklabels(data_t.index[::3])
    mpf.candlestick2_ochl(ax, data_t['open'], data_t['close'], data_t['high'],
                          data_t['low'], width=0.6, colorup='r', colordown='gray', alpha=0.75); 
    #plt.rcParams['font.sans-serif']=['Microsoft JhengHei'] 
    ax.plot(sma_5, label='5日均線')
    ax.plot(sma_20, label='20日均線')

    ax2.plot(np.array(data_t_macd[0]), label='0值')
    ax2.plot(np.array(data_t_macd[1]), label='1值')
    mpf.volume_overlay(ax2, np.array(data_t_macd[1]),np.array(data_t_macd[0]), np.array(data_t_macd[2]), colorup='r', colordown='gray', width=0.5, alpha=0.8)

    ax2.set_xticks(range(0, len(data_t.index), 3))
    ax2.set_xticklabels(data_t.index[::3])
    
    ax4.plot(np.array(data_t_rsi), label='rsi')
    datazero = data_t['open']-data_t['open']
    mpf.volume_overlay(ax3,datazero , data_t['三大法人買賣超股數'], data_t['三大法人買賣超股數'], colorup='r', colordown='blue', width=0.5, alpha=0.75)
    ax3.set_xticks(range(0, len(data_t.index), 3))
    ax3.set_xticklabels(data_t.index[::3])

    ax.legend()
    ax2.legend()
    plt.savefig('C:\\Users\\Owner\\Downloads\\stock_analyze\\'+stock +'.png',format='png')

today_str = int(time.strftime("%Y%m%d"))
c.execute('INSERT OR REPLACE INTO "0050" ("date") VALUES ('+ str(today_str) +');')
close_date = pd.read_sql_query('SELECT date FROM "0050";', conn)["date"]
date_f = [] #交易日ARY
for i in close_date:
    date_f.append(i)
yes_index = date_f.index(today_str)-1
yest_int = date_f[yes_index]
#開始篩選
bb = bigboybuy_oneday(yest_int,table_name) #法人分析隔天買超
volb = volbig(yest_int,5000,bb)
m1 = macddouble_not(yest_int,volb) #先篩昨天 避免跑今天股價太慢
simulation(today_str,m1) #模擬當天
mm = macddouble(today_str,m1) #當天雙峰回漲
print(mm)
for s in mm:
    draw(today_str,s)