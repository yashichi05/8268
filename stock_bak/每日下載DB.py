#執行下載程式
import time
import sqlite3
import requests 
import shutil
import csv
import os
from os import listdir
from os.path import isfile, isdir, join
import sys
import io

conn = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\stock_db.db')
c = conn.cursor()
conn2 = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\TSE.db')
c2 = conn2.cursor()
conn3 = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\taifex.db')
c3 = conn3.cursor()
conn4 = sqlite3.connect(r'C:\Users\Owner\Downloads\stock_analyze\bigdeal.db')
c4 = conn4.cursor()
def dlcsv(csvnm):
    url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date='+ csvnm +'&type=ALLBUT0999'
    req = requests.get(url) 
    with open('C:\\Users\\Owner\\Downloads\\stock_analyze\\價格\\'+str(csvnm)+'.csv', "wb") as code:
        code.write(req.content)
    time.sleep(2)  #休息三秒
    url = 'http://www.twse.com.tw/fund/BFI82U?response=csv&dayDate='+ csvnm +'&weekDate='+ csvnm +'&monthDate='+ csvnm +'&type=day'
    req = requests.get(url) 
    with open('C:\\Users\\Owner\\Downloads\\stock_analyze\\法人\\法人'+str(csvnm)+'.csv', "wb") as code:
        code.write(req.content)
    time.sleep(2)  #休息三秒
    url = 'http://www.twse.com.tw/fund/T86?response=csv&date='+ str(csvnm) +'&selectType=ALLBUT0999'
    req = requests.get(url) 
    with open('C:\\Users\\Owner\\Downloads\\stock_analyze\\個股法人\\'+str(csvnm)+'.csv', "wb") as code:
        code.write(req.content)
    time.sleep(2)  #休息三秒
    
    newtime = time.strftime("%Y/%m/%d",time.strptime(str(csvnm),"%Y%m%d"))
    url = 'http://www.taifex.com.tw/cht/3/dlFutContractsDateDown'
    postdata = {'firstDate':'2001/04/12 00:00','lastDate':newtime +' 00:00','queryStartDate':newtime,'queryEndDate':newtime,'commodityId':''}
    newSession = requests.Session() #新的session
    #post 資料
    #沿用session
    res = newSession.post(url,data = postdata)
    with open("C:\\Users\\Owner\\Downloads\\stock_analyze\\期貨三大法人\\"+ str(csvnm)+".csv", "wb") as code:
            code.write(res.content)

    url = 'http://www.taifex.com.tw/cht/3/dlLargeTraderFutDown'
    postdata = {'queryStartDate': newtime,'queryEndDate': newtime}

    res = newSession.post(url,data = postdata)
    with open("C:\\Users\\Owner\\Downloads\\stock_analyze\\期貨鉅額交易\\"+ str(csvnm)+".csv", "wb") as code:
            code.write(res.content)
        
def in_data(date_str):

    true_path = "C:\\Users\\Owner\\Downloads\\stock_analyze\\價格\\"+date_str+".csv"
    with open(true_path, newline='') as csvfile:
        start_load = 0 #初始化值(是否找到證券代號)
        rows = csv.reader(csvfile)
        for i in rows:
            if start_load == 1: 
                stock_code = i[0].replace('"',"").replace("=","") #證券代號檔案名稱
                #新增TABLE
                c.execute('CREATE TABLE IF NOT EXISTS "'+stock_code+'" ( \
                            "date" INTEGER NOT NULL, \
                            "vol" INTEGER, \
                            "num" INTEGER, \
                            "price" INTEGER, \
                            "open" REAL, \
                            "high" REAL, \
                            "low" REAL, \
                            "close" REAL, \
                            "up" TEXT, \
                            "upprice" REAL, \
                            "lastbuy" REAL, \
                            "lastbuyvol" INTEGER, \
                            "lastsell" REAL, \
                            "lastsellvol" INTEGER, \
                            "PE" REAL, \
                            "外陸資買進股數(不含外資自營商)" INTEGER, \
                            "外陸資賣出股數(不含外資自營商)" INTEGER, \
                            "外陸資買賣超股數(不含外資自營商)" INTEGER, \
                            "外資自營商買進股數" INTEGER, \
                            "外資自營商賣出股數" INTEGER, \
                            "外資自營商買賣超股數" INTEGER, \
                            "投信買進股數" INTEGER, \
                            "投信賣出股數" INTEGER, \
                            "投信買賣超股數" INTEGER, \
                            "自營商買賣超股數" INTEGER, \
                            "自營商買進股數(自行買賣)" INTEGER, \
                            "自營商賣出股數(自行買賣)" INTEGER, \
                            "自營商買賣超股數(自行買賣)" INTEGER, \
                            "自營商買進股數(避險)" INTEGER, \
                            "自營商賣出股數(避險)" INTEGER, \
                            "自營商買賣超股數(避險)" INTEGER, \
                            "三大法人買賣超股數" INTEGER, \
                            PRIMARY KEY("date"));')
                #除錯用 INT欄補NULL
                insert14 = i[14].replace(",","").replace("--","NULL")
                insert12 = i[12].replace(",","").replace("--","NULL")
                insert9 = '"'+i[9].replace(",","").replace("--","NULL")+'"'
                if insert14 == "":
                    insert14 = "NULL"
                if insert12 == "":
                    insert12 = "NULL"
                if insert9 == '" "':
                    insert9 = 'NULL'

                c.execute('INSERT OR REPLACE INTO "' + stock_code + '" VALUES('+date_str+',' \
                             +i[2].replace(",","").replace("--","NULL")+',' \
                             +i[3].replace(",","").replace("--","NULL")+',' \
                             +i[4].replace(",","").replace("--","NULL")+',' \
                             +i[5].replace(",","").replace("--","NULL")+',' \
                             +i[6].replace(",","").replace("--","NULL")+',' \
                             +i[7].replace(",","").replace("--","NULL")+',' \
                             +i[8].replace(",","").replace("--","NULL")+',' \
                             +insert9+',' \
                             +i[10].replace(",","").replace("--","NULL")+',' \
                             +i[11].replace(",","").replace("--","NULL")+',' \
                             +insert12+',' \
                             +i[13].replace(",","").replace("--","NULL")+',' \
                             +insert14+',' \
                             +i[15].replace(",","").replace("--","NULL")+',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);')
            try:
                if i[0] == '證券代號': #找到代號，開始新增
                    start_load = 1
            except:
                pass
    conn.commit() #CSV 讀完下指令

def in_data2(date_str):
    col_data = ['外陸資買進股數(不含外資自營商)',
                 '外陸資賣出股數(不含外資自營商)',
                 '外陸資買賣超股數(不含外資自營商)',
                 '外資自營商買進股數',
                 '外資自營商賣出股數',
                 '外資自營商買賣超股數',
                 '投信買進股數',
                 '投信賣出股數',
                 '投信買賣超股數',
                 '自營商買賣超股數',
                 '自營商買進股數(自行買賣)',
                 '自營商賣出股數(自行買賣)',
                 '自營商買賣超股數(自行買賣)',
                 '自營商買進股數(避險)',
                 '自營商賣出股數(避險)',
                 '自營商買賣超股數(避險)',
                 '三大法人買賣超股數']
    true_path = "C:\\Users\\Owner\\Downloads\\stock_analyze\\個股法人\\"+date_str+".csv"
    with open(true_path, newline='') as csvfile:
        start_load = 0 #初始化值(是否找到證券代號)
        rows = csv.reader(csvfile)
        for i in rows:
            if start_load == 1: 
                if i[0] == "說明:": #跳出迴圈
                    break
                stock_code = i[0].replace('"',"").replace("=","") #證券代號檔案名稱
                #新增TABLE
                col_num = 2 #讀取第二攔
                for col_t in col_data:
                    try:
                        c.execute('UPDATE "'+stock_code+'" SET "'+ col_t +'" = '+i[col_num].replace(",","")+' WHERE "date" = '+date_str+';')
                    except:
                        c.execute('UPDATE "'+stock_code+'" SET "'+ col_t +'" = '+'NULL'+' WHERE "date" = '+date_str+';')
                    col_num += 1
            try:
                if i[0] == '證券代號': #找到代號，開始新增
                    start_load = 1
            except:
                pass
    conn.commit() #CSV 讀完下指令
    
def tes(date_str):#大盤資料
    true_path = "C:\\Users\\Owner\\Downloads\\stock_analyze\\價格\\"+date_str+".csv"#完整位置
    with open(true_path, newline='') as csvfile:
        start_load = 0 #初始化值(是否找到證券代號)
        rows = csv.reader(csvfile)
        for i in rows:
            try:
                if i[0] == '發行量加權股價指數' or i[0] == '加權股價指數': #找到代號，開始新增
                    start_load = 1
            except:
                pass
            if start_load == 1: 
                if i[0] != "發行量加權股價指數" and i[0] !=  '加權股價指數': #跳出迴圈
                    break
                #print( date_str +','+ i[1].replace(",","") +',"'+ i[2].replace(",","") +'",'+i[3].replace(",","").replace("--","NULL") + ','+i[4].replace(",","").replace("--","NULL"))
                try:
                    c2.execute('INSERT OR REPLACE INTO "發行量加權股價指數" VALUES('+ date_str +','+ i[1].replace(",","") +',"'+ i[2].replace(",","") +'",'+i[3].replace(",","").replace("--","NULL") + ','+i[4].replace(",","").replace("--","NULL") + ',null,null,null,null,null,null);')
                except:
                    c2.execute('INSERT OR REPLACE INTO "發行量加權股價指數" VALUES('+ date_str +','+ i[1].replace(",","") +',"'+ i[2].replace(",","") +'",'+i[3].replace(",","").replace("--","NULL") + ','+i[4].replace(",","").replace("---","NULL") + ',null,null,null,null,null,null);')

    #大盤法人輸入
    true_path = "C:\\Users\\Owner\\Downloads\\stock_analyze\\法人\\法人"+ date_str+".csv"#完整位置
    with open(true_path, newline='') as csvfile:
        start_load = 0 #初始化值(是否找到證券代號)
        rows = csv.reader(csvfile)
        data_ary = []
        for i in rows:
            if start_load == 1: 
                if i[0] == "說明:": #跳出迴圈
                    break
                data_ary.append(i[3].replace(",",""))

            try:
                if i[0] == '單位名稱': #找到代號，開始新增
                    start_load = 1
            except:
                pass
        c2.execute('UPDATE "發行量加權股價指數" SET "自營商(自行買賣)" = '+ data_ary[0] +' WHERE "date" = '+date_str +';')
        c2.execute('UPDATE "發行量加權股價指數" SET "自營商(避險)" = '+ data_ary[1] +' WHERE "date" = '+date_str +';')
        c2.execute('UPDATE "發行量加權股價指數" SET "投信" = '+ data_ary[2] +' WHERE "date" = '+date_str +';')
        c2.execute('UPDATE "發行量加權股價指數" SET "外資及陸資(不含外資自營商)" = '+ data_ary[3] +' WHERE "date" = '+date_str +';')
        c2.execute('UPDATE "發行量加權股價指數" SET "外資自營商" = '+ data_ary[4] +' WHERE "date" = '+date_str +';')
        c2.execute('UPDATE "發行量加權股價指數" SET "合計" = '+ data_ary[5] +' WHERE "date" = '+date_str +';')
    conn2.commit() #CSV 讀完下指令
def change(text_ary):
    a= []
    for i in text_ary:
        i = i.replace("-","")
        if i == "":
            i = "NULL"
        a.append(i)
    return a
    
def in_data3(date_str):
    #寫入DB 三大法人
    target_path = "C:\\Users\\Owner\\Downloads\\stock_analyze\\期貨三大法人\\"+ date_str+".csv"

    with open(target_path, newline='') as csvfile:
        rows = csv.reader(csvfile)
        start = 0
        for i in rows:
            if start >= 1:
                date = i[0]
                t_name = i[1]+"_"+i[2]
                data = [i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13],i[14]]
                c3.execute('CREATE TABLE IF NOT EXISTS "'+ t_name +'" ( \
                                        "date" INTEGER NOT NULL \
                                        ,"多方交易口數" INTEGER \
                                        ,"多方交易契約金額(百萬元)" INTEGER \
                                        ,"空方交易口數" INTEGER \
                                        ,"空方交易契約金額(百萬元)" INTEGER \
                                        ,"多空交易口數淨額" INTEGER \
                                        ,"多空交易契約金額淨額(百萬元)" INTEGER \
                                        ,"多方未平倉口數" INTEGER \
                                        ,"多方未平倉契約金額(百萬元)" INTEGER \
                                        ,"空方未平倉口數" INTEGER \
                                        ,"空方未平倉契約金額(百萬元)" INTEGER \
                                        ,"多空未平倉口數淨額" INTEGER \
                                        ,"多空未平倉契約金額淨額(百萬元)" INTEGER, \
                                        PRIMARY KEY("date"));')
                c3.execute('INSERT OR REPLACE INTO "'+ t_name +'" VALUES('+ date.replace("/","") +","+data[0]+","+data[1]+","+data[2]+","+data[3]+","+data[4]+","+data[5]+","+data[6]+","+data[7]+","+data[8]+","+data[9]+","+data[10]+","+data[11]+');')

            start += 1

    conn3.commit() #CSV 讀完下指令
        #break

        #鉅額


    #寫入DB
    target_path = "C:\\Users\\Owner\\Downloads\\stock_analyze\\期貨鉅額交易\\"+ date_str+".csv"

    with open(target_path, newline='') as csvfile:
        rows = csv.reader(csvfile)
        start = 0
        for i in rows:
            if start >= 1 and len(i) == 10  and i[4] == "0":
                date = i[0]
                t_name = i[1].replace(" ","")+"_"+i[2].replace(" ","")+"_"+"近月"
                if i[3].replace(" ","") == "999999":
                    t_name = i[1].replace(" ","")+"_"+i[2].replace(" ","")+"_"+"所有"
                data = [i[3],i[4],i[5],i[6],i[7],i[8],i[9]]
                data = change(data)
                c4.execute('CREATE TABLE IF NOT EXISTS "'+ t_name +'" ( \
                                        "date" INTEGER NOT NULL \
                                        ,"到期月份(週別)" TEXT \
                                        ,"交易人類別" INTEGER \
                                        ,"前五大交易人買方" INTEGER \
                                        ,"前五大交易人賣方" INTEGER \
                                        ,"前十大交易人買方" INTEGER \
                                        ,"前十大交易人賣方" INTEGER \
                                        ,"全市場未沖銷部位數" INTEGER , \
                                        PRIMARY KEY("date"));')
                text = 'INSERT OR REPLACE INTO "'+ t_name +'" VALUES('+ date.replace('/','') +',"'+data[0].replace('  ','')+'",'+data[1]+','+data[2]+','+data[3]+','+data[4]+','+data[5]+','+data[6]+');'
                c4.execute(text)
            start += 1

        conn4.commit() #CSV 讀完下指令
            #break

    
    
today_str = time.strftime("%Y%m%d")
today_str = input("Date("+today_str+"): ")
dlcsv(today_str)
print('寫入資料')
in_data(today_str)

in_data2(today_str)
#in_data3(today_str)

tes(today_str)

c.close()
conn.close()
c2.close()
conn2.close()
c3.close()
conn3.close()
c4.close()
conn4.close()
print('完成')