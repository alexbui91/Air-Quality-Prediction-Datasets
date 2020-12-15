# _*_ coding: utf-8 _*_
from bs4 import BeautifulSoup as Soup
import requests
from argparse import ArgumentParser
from datetime import datetime, timedelta
import utils
import properties as pr
from crawling_base import Crawling

#https://young-0.com/airquality/charts.php?years=1&months=0&city=4&month=4&year=2018&dir=1&threshold=500&action=Export+CSV
"""
Craw air quality information for cleanair.seoul.or.kr
Data are organized as seconds intervally records that consist of 
"""

class CrawSeoulAQI(Crawling):
        
    def __init__(self, **kwargs):
        super(CrawSeoulAQI, self).__init__(**kwargs)
        self.filename = "data/seoul_aqi.csv"
    
    def mine_data(self, html):
        tables = html.find('table', attrs={"class": "tbl1"})
        body = tables.find('tbody')
        all_values = []
        if body:
            all_tr = body.find_all("tr")
            if all_tr:
                for ku, r in enumerate(all_tr):
                    td = r.find_all('td')
                    values = []
                    for i, v in enumerate(td):
                        txt = v.get_text()
                        txt = "".join(txt.replace("\n", "").split(" "))
                        if i > 0 and i < 7 and "-" not in txt:
                            txt = txt.encode('ascii', 'ignore').replace("\t", "").replace(" ", "")
                            if txt:
                                values.append(float(txt))
                            else:
                                values.append(all_values[0][i])
                        elif i == 0:        
                            txt = txt.rstrip("\n").replace("\t", "").replace(" ", "") 
                            if txt in pr.districts:
                                index = pr.districts.index(txt)
                                values.append(index)
                            txt = txt.rstrip("\n")   
                            index = pr.districts.index(txt)
                            values.append(index)
                    values.append(self.AQIPM10(values[1]))
                    values.append(self.AQIPM25(values[2]))
                    all_values.append(values)
        return all_values

    # craw aqi data from source 
    def craw_data(self, year, month, date, hour):
        data = {
            "bodyCommonMethod": "measure",
            "bodyCommonHtml": "air_city.htm",
            "msrntwCode": "A",
            "grp1": "pm25",
            "pNum": "1",
            "scrollTopVal": "713.6363525390625",
            "lGroup": "1",
            "mGroup":"",
            "sGroup": "TIME",
            "cal2": "%s" % year,
            "cal2Month": "%s" % month,
            "cal2Day": "%s" % date,
            "time": "%s" % hour,
            "x": "21",
            "y": "32"
        }
        r = requests.post("http://cleanair.seoul.go.kr/air_city.htm?method=measure&citySection=CITY", data)
        html = Soup(r.text, "html5lib")
        return html


    # perform craw in loop or by files
    def craw_data_controller(self, output, counter, last_save, save_interval, tmp, hour, timestamp):
        year = tmp.year
        month = self.format10(tmp.month)
        date = self.format10(tmp.day)
        counter += 1
        #try:
        html = self.craw_data(year, month, date, hour)
        data = self.mine_data(html)
        for x in data:
            output += timestamp + "," + utils.array_to_str(x, ",") + "\n"
            if (counter - last_save) == save_interval:
                last_save = counter
                self.write_log(output)
                output = ""
        #except Exception as e:
        #    print(e)
        return output, counter, last_save

    def execute(self, args):
        print("start crawling aqi seoul")
        save_interval = args.save_interval
        start = datetime.strptime(args.start, pr.fm)
        # start_point = utils.get_datetime_now()
        output = ""
        counter = 0
        last_save = 0
        # crawler_range = 3600
        if not args.forward:
            if args.end:
                end = datetime.strptime(args.end, pr.fm)
            else:
                end = utils.get_datetime_now()
            length = (end - start).total_seconds() / 86400
        else:
            end = datetime.strptime("2050-12-31 00:00:00", pr.fm)
        while start <= end:
            now = utils.get_datetime_now()
            # if (now - start_point).total_seconds() >= args.interval:
            #     start_point = now
            if (now - start).total_seconds() > 3600:
                hour = start.hour
                tmp = start
                if tmp.hour == 0:
                    tmp = tmp - timedelta(hours=1)
                    hour = "24"
                else:
                    hour = self.format10(tmp.hour)
                st_ = start.strftime(pr.fm)
                output, counter, last_save = self.craw_data_controller(output, counter, last_save, save_interval, tmp, hour, st_)
                # move pointer for timestep
                start = start + timedelta(hours=1)
                if not args.forward:
                    utils.update_progress(counter * 1.0 / length)
                else:
                    self.write_log(output)
                    output = ""
        self.write_log(output)      


if __name__ == "__main__":
    crawler = CrawSeoulAQI()
    args = crawler.add_argument()
    # crawler.init_env()
    crawler.execute(args)
