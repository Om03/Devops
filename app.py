from yahoo_fin import stock_info as si
from datetime import date, timedelta
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import datetime
import pandas as pd
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/short' , methods=['POST'])
def short():
    ret_s = pd.DataFrame(columns=["share_n", "timestamp", "notify", "sell"])
    n = 0
    share_list = json.loads(request.data)['stock_list']
    for share_obj in share_list:
        share = share_obj['name']
        delta = share_obj['delta']
        save = share_obj['save']
        tdy = date.today()
        ydy = date.today() - timedelta(days=1)
        sdy = date.today() - timedelta(days=1500)
        dma50 = si.get_data(share, start_date=sdy, end_date=tdy, interval="1d").close.to_frame()
        dma50["ma"] = dma50.close.rolling(window=50).mean()
        dma50 = dma50.tail(1)
        dma50.index = [0]
        ma50 = dma50.at[0, "ma"]
        hist = si.get_data(share, start_date=tdy, interval="1m").close.to_frame()
        hist["timestamp"] = hist.index + timedelta(minutes=330)
        hist["ticker"] = si.get_data(share, start_date=tdy, interval="1m").ticker
        hist = hist.tail(15)
        hist.index = range(0, 15, 1)
        w = False
        x = False
        for i in range(0, 14, 1):
            mini = save - delta
            maxi = save + delta
            cur_price = si.get_live_price(share)
            if cur_price >= maxi:
                w = True
                x = True
                n = int(n)
                ret_s.at[n, "notify"] = w
                ret_s.at[n, "sell"] = x
                ret_s.at[n, "share_n"] = share
                ret_s.at[n, "timestamp"] = hist.at[i, "timestamp"]
                n = n + 1
                break

            elif cur_price <= mini:
                w = True
                x = False
                ret_s.at[n, "notify"] = w
                ret_s.at[n, "sell"] = x
                ret_s.at[n, "share_name"] = share
                ret_s.at[n, "timestamp"] = hist.at[i, "timestamp"]
                n = n + 1
                break
        n = n
    return ret_s.to_json(orient='records')



@app.route('/long', methods=['POST'])
def long():
    ret_l = pd.DataFrame(columns=["share_n","notify", "sell", "rsi"])
    share_list = json.loads(request.data)['stock_list']
    for share_obj in share_list:
    
        share = share_obj['name']
        market = None
        if share[-2:] == "NS":
            market = "^NSEI"
        elif share[-2:] == "BO":
            market = "BSE-500.BO"
        tdy = date.today()
        sdy = tdy - timedelta(days=1851)
        hist = si.get_data(market, start_date=sdy, interval="1d").close.to_frame()
        hist_comp = si.get_data(share, start_date=sdy, interval="1d").close.to_frame()
        hist_comp = hist_comp.tail(20)
        hist_comp.dropna()
        hist_comp = hist_comp.tail(15)
    
        hist_comp ["close"] = hist_comp.close.__round__(3)
        hist.columns = ["close"]
        hist["date"] = hist.index
        hist_comp["inx"] = range(1, hist_comp.size + 1, 1)
        hist_comp = hist_comp.set_index("inx")
        hist["ma200"] = hist.close.ewm(span=200).mean()
        tdyma = hist.tail(1)
        tdy_close = float(hist.iat[-1, 0]).__round__(3)
        dma200 = float(tdyma.ma200).__round__(3)
        change = [0] * 14
        pos = 0
        neg = 0
        for i in range(1, 15, 1):
    
            change[i - 1] = float(hist_comp.close[i + 1] - hist_comp.close[i])
            if (change[i - 1] >= 0):
                pos = pos + change[i - 1]
            else:
                neg = neg + change[i - 1]
        neg = -neg / 14
        pos = pos / 14
        rs = pos / neg
        rsi = (100 - (100 / (1 + rs))).__round__(3)
    
        x = False
        y = False
        if (dma200 < tdy_close):
            if (rsi <= 30):
                x = True
                y = False
                ret_l = ret_l.append({"share_n":share,"notify": x, "sell" : y,"rsi": rsi}, ignore_index=True)
            elif (rsi >= 70):
                x = True
                y = True
                ret_l = ret_l.append({"share_n":share,"notify": x, "sell": y, "rsi": rsi}, ignore_index=True)
            else:
                x = False
                y = False
                ret_l = ret_l.append({"share_n":share,"notify": x, "sell": y, "rsi": rsi}, ignore_index=True)
        elif (dma200 > tdy_close):
            if (rsi >= 70):
                x = True
                y = True
                ret_l = ret_l.append({"share_n":share,"notify": x, "sell": y, "rsi": rsi}, ignore_index=True)
            else:
                x = False
                y = False
                ret_l = ret_l.append({"share_n":share,"notify": x, "sell": y, "rsi": rsi}, ignore_index=True)
        else:
            ret_l = ret_l.append({"share_n":share,"notify": x, "sell": y, "rsi": rsi}, ignore_index=True)
    return ret_l.to_json(orient='records')


@app.route('/news/<string:search>', methods=['GET'])
def webCrawl (search):
    news_df = pd.DataFrame(columns={"Headline", "Date_time", "URL"})
    date = datetime.datetime.now()
    date = date.date() - datetime.timedelta(days=2)
    date = str(date)
    date = date.replace("-", "")
    date = int(date)
    search = search.replace(" ", "%20")
    search = search.replace("Limited", "")
    search = search.replace("ltd", "")
    search = search.replace("INC", "")
    search = search.replace("inc", "")
    search = search.replace("LLC", "")
    newsUrl = "https://news.google.com/rss/?q=" + str(search)
    website = urlopen(newsUrl)
    xml_page = website.read()
    website.close()
    ret_n = pd.DataFrame(columns=[""])
    soup_page = soup(xml_page, "xml")
    news_list = soup_page.findAll("item")
    # Print news title, url and publish date
    for news in news_list:
        day = (news.pubDate.text[5:7])
        wkday = str(news.pubDate.text[0:4])
        pub_time = str(news.pubDate.text[17:25])
        d = {"Jan" : "01", "Feb" : "02", "Mar" : "03", "Apr" : "04", "May" : "05", "Jun" : "06", "Jul" : "07", "Aug" : "08", "Sep" : "09", "Oct" : "10", "Nov" : "11", "Dec" : "12"}
        month = (d.get(news.pubDate.text[8:11]))
        year = (news.pubDate.text[12:16])
        date_t = str(year + "-" + month + "-" + day + " " +pub_time)
        format = "%Y-%m-%d %H:%M:%S"
        date_time = datetime.datetime.strptime(date_t, format) + datetime.timedelta(minutes = 330)
        date_time = wkday + str(date_time)
        date_a = int(str(year + month + day))

        if (date_a >= date):
            headl = news.title.text
            newslink = news.link.text
            news_df = news_df.append({"Headline": headl, "Date_time" : date_time, "URL": newslink}, ignore_index=True)
    return news_df.to_json(orient='records')

if __name__ == "__main__":
    app.run()
