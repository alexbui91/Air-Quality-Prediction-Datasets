"""
craw weather from https://www.worldweatheronline.com/daegu-weather-history/kr.aspx
https://www.worldweatheronline.com/weifang-weather/shandong/cn.aspx
# previous crawling: by default wind speed is mph (beijing, shenyang, seoul 2008-2018)
# now: by default wind speed is km/h (shandong)
"""

# _*_ coding: utf-8 _*_
from bs4 import BeautifulSoup as Soup
import requests
from argparse import ArgumentParser
from datetime import datetime, timedelta
import utils
import properties as pr
from crawling_base import Crawling


class CrawlWeather(Crawling):
    def __init__(self):
        super(CrawlWeather, self).__init__()
        self.filename = "data/weather_forecasts.csv"

    # clear out html and get data
    def mine_data(self, date, html, city=""):
        tables = html.find('div', attrs={"class": "weather_tb tb_years tb_years_8"})
        weathers = tables.find('div', attrs={"class": "tb_row tb_weather"}).find_all("div", attrs={"class": "tb_cont_item"})
        temps = tables.find('div', attrs={"class": "tb_row tb_temp"}).find_all("div", attrs={"class": "tb_cont_item"})
        feels = tables.find('div', attrs={"class": "tb_row tb_feels"}).find_all("div", attrs={"class": "tb_cont_item"})
        winds = tables.find('div', attrs={"class": "tb_row tb_wind"}).find_all("div", attrs={"class": "tb_cont_item"})
        gusts = tables.find_all('div', attrs={"class": "tb_row tb_gust"})
        dirs = None
        if len(gusts) > 1:
            dirs = gusts[0].find_all("div", attrs={"class": "tb_cont_item"})
            gusts = gusts[1].find_all("div", attrs={"class": "tb_cont_item"})
        else:
            gusts = gusts[0].find_all("div", attrs={"class": "tb_cont_item"})
        clouds = tables.find('div', attrs={"class": "tb_row tb_cloud"}).find_all("div", attrs={"class": "tb_cont_item"})
        humids = tables.find('div', attrs={"class": "tb_row tb_humidity"}).find_all("div", attrs={"class": "tb_cont_item"})
        preps = tables.find('div', attrs={"class": "tb_row tb_precip"}).find_all("div", attrs={"class": "tb_cont_item"})
        pressures = tables.find('div', attrs={"class": "tb_row tb_pressure"}).find_all("div", attrs={"class": "tb_cont_item"})
        values = []
        i = 0
        for wt,t,f,w,g,c,h,r,p in zip(weathers,temps,feels,winds,gusts,clouds,humids,preps,pressures):
            if i:
                w_ = wt.find("img")["alt"]
                # t_ = t.get_text().encode("ascii", "ignore").rstrip(" c")
                # f_ = f.get_text().encode("ascii", "ignore").rstrip(" c")
                t_ = t.get_text().rstrip(" c")
                f_ = f.get_text().rstrip(" c")
                # default of wind speed is km/h, convert to m/s
                ws = w.get_text().split(" ")
                ws_ = "%.1f" % (int(ws[0]) * 0.277778)

                if dirs:
                    d_ = dirs[i].get_text()
                else:
                    d_ = ws[-1].lstrip("km/h")
                g_ = g.get_text().rstrip(" km/h")
                g_ = "%.1f" % (int(g_) * 0.277778)
                
                c_ = c.get_text().rstrip("%")
                h_ = h.get_text().rstrip("%")
                r_ = r.get_text().rstrip(" mm")
                p_ = p.get_text().rstrip(" mb")
                row = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (w_,t_,f_,ws_, d_ ,g_,c_,h_,r_,p_)
                if city:
                    row += ",%s" % city
                t1 = (i - 1) * 3
                t2 = t1 + 1
                t3 = t1 + 2
                values.append("%s %s:00:00,%s" % (date, self.format10(t1), row))
                values.append("%s %s:00:00,%s" % (date, self.format10(t2), row))
                values.append("%s %s:00:00,%s" % (date, self.format10(t3), row))
            i += 1
        return values


    # get url correspond to key
    def get_city_url(self, key, past=True):
        if past:
            keys = {
                "beijing": "https://www.worldweatheronline.com/beijing-weather-history/beijing/cn.aspx",
                "seoul": "https://www.worldweatheronline.com/seoul-weather-history/kr.aspx",
                "daegu": "https://www.worldweatheronline.com/daegu-weather-history/kr.aspx",
                "shenyang": "https://www.worldweatheronline.com/shenyang-weather-history/liaoning/cn.aspx",
                "shandong": "https://www.worldweatheronline.com/weifang-weather-history/shandong/cn.aspx"
            }
        else:
            keys = {
                "seoul" : "https://www.worldweatheronline.com/seoul-weather/kr.aspx",
                "daegu": "https://www.worldweatheronline.com/daegu-weather/kr.aspx",
                "beijing": "https://www.worldweatheronline.com/beijing-weather/beijing/cn.aspx",
                "shenyang": "https://www.worldweatheronline.com/shenyang-weather/liaoning/cn.aspx",
                "shandong": "https://www.worldweatheronline.com/weifang-weather/shandong/cn.aspx"
            }
        return keys[key]


    # craw aqi data from source 
    # wind speed is m/s
    def craw_data(self, key, date):
        data = {
            "__VIEWSTATE": "YXoDh/TJkQEYh7RnUh/zqdnaCMy0fpUIghr2DKhphyOZhykF/BbVFsnKnHDPiq6vbRqCKLsKup9GlMi3RxE0qnJvxgkt4UVGsq9xkHyZoT54258n",
            "__VIEWSTATEGENERATOR": "F960AAB1",
            "ctl00$rblTemp": 1,
            "ctl00$rblPrecip": 1,
            "ctl00$rblWindSpeed": 1,
            "ctl00$rblPressure": 1,
            "ctl00$rblVis": 1,
            "ctl00$rblheight": 1,
            "ctl00$hdlat": 37.570,
            "ctl00$hdlon": 127.000,
            "ctl00$MainContentHolder$txtPastDate": date,
            "ctl00$MainContentHolder$butShowPastWeather":"Get Weather"
        }
        url = self.get_city_url(key)
        r = requests.post(url, data)
        html = Soup(r.text, "html5lib")
        return html


    def craw_future(self, key, days=1):
        data = {
            "day": days
        }
        url = self.get_city_url(key, False)
        r = requests.get(url, data)
        html = Soup(r.text, 'html5lib')
        return html

    """
        crawl historical weather data of cities
    """
    def main(self, args):
        #filename = "craw_weather_%s_%s_%s.txt" % (args.city, utils.clear_datetime(args.start), utils.clear_datetime(args.end))
        start = datetime.strptime(args.start, pr.fm)
        if args.end:
            end = datetime.strptime(args.end, pr.fm)
        else:
            end = utils.get_datetime_now()
        start_point = utils.now_milliseconds()
        # output = "timestamp,PM10_VAL,PM2.5_VAL,O3(ppm),NO2(ppm),CO(ppm),SO2(ppm),PM10_AQI,PM2.5_AQI\n"
        output = ""
        length = (end - start).total_seconds() / 86400.0
        save_interval = args.save_interval
        counter = 0
        last_save = 0
        if "," in args.city:
            cities = args.city.split(",")
        else:
            cities = [args.city]
        while start <= end:
            now = utils.now_milliseconds()
            diff = now - start_point
            # print(elapsed_time)
            if diff >= 100:
                # try:
                counter += 1
                date = "%s-%s-%s" % (start.year, self.format10(start.month), self.format10(start.day))
                for c in cities:
                    html = self.craw_data(c, date)
                    data = self.mine_data(date, html, c)
                    if data:
                        output += "\n".join(data) + "\n"
                    if (counter - last_save) == save_interval:
                        last_save = counter
                        self.write_log(output)
                        output = ""
                # except Exception as e:
                #    print(start.strftime(pr.fm), e)
                start = start + timedelta(days=1)
                start_point = now   
                utils.update_progress(counter * 1.0 / length)
        self.write_log(output)

    """
    craw future weather forecast of corresponding city
    """
    def get_future(self, args):
        print("Collecting future forecasting")
        start_point = utils.get_datetime_now()
        start_point = start_point - timedelta(days=1)
        # interval = args.interval * 86400
        cities = []
        if "," in args.city:
            cities = args.city.split(",")
        else:
            cities.append(args.city)
        while True:
            now = utils.get_datetime_now()
            if (now - start_point).total_seconds() >= 0:
                try:
                    # crawl 4 days forward for each city
                    for i in range(4):
                        start_point = start_point + timedelta(days=1)
                        date = "%s-%s-%s" % (start_point.year, self.format10(start_point.month), self.format10(start_point.day))
                        for c in cities:
                            html = self.craw_future(c, i)
                            data = self.mine_data(date, html, c)
                            if data:
                                output = "\n".join(data) + "\n"
                                self.write_log(output)
                except Exception as e:
                    print(e)


if __name__ == "__main__":
    crawler = CrawlWeather()
    args = crawler.add_argument()
    if args.forward:
        crawler.get_future(args)
    else:
        crawler.main(args)

    
        





        
    
