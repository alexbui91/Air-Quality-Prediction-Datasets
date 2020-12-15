# _*_ coding: utf-8 _*_
import subprocess
from lxml import etree
import requests
from argparse import ArgumentParser
from datetime import datetime, timedelta
import time
import utils
import properties as pr
from crawling_base import Crawling


class CrawlAWS(Crawling):

    def __init__(self):
        super().__init__()
        self.filename = "data/seoul_aws.csv"
    
    def mine_data(self, html):
        all_values = []
        doc = etree.HTML(html)
        # records
        path1 = doc.xpath("//table[@id='TRptList']/tbody/tr")
        # time
        path2 = doc.xpath("//table[@id='TRptFixed']/tbody/tr")
        
        for r, t in zip(path1, path2):
            record = []
            t_td = t.xpath("./td/text()")
            if  t_td: 
                record.append(t_td[0].encode('ascii', 'ignore'))
                for td in r.xpath("./td/text()"):
                    record.append(td.encode('ascii', 'ignore'))
            all_values.append(record)
        # agg = html.find("div", attrs={"id", "RptFooter"}).find("tr").find_all("td")
        # agg_record = []
        # print(all_values)
        return all_values

    # craw aqi data from source 
    def craw_data(self, timestamp, area, st="00", ed="24"):
        data = {
            "EXCEL": "SCREEN",
            "MODE": "SEARCH",
            "SDATAKEY":" ",
            "VIEW_MIN":" ",
            "VIEW_MAX":" ",
            "VIEW_SITE":" ",
            "VIEW_WIND":" ",
            "AWS_ID": area,
            "RptSDATE": timestamp,
            "RptSH": "00",
            "RptSM": st,
            "RptEH": ed,
            "RptEM": "00"
        }
        r = requests.post("http://aws.seoul.go.kr/Report/RptWeatherMinute.asp", data)
        # html = Soup(r.text, "html5lib")
        return r.text


    # perform craw in loop or by files
    def craw_data_controller(self, output, counter, last_save, save_interval, tmp, st, ed):
        year = tmp.year
        month = self.format10(tmp.month)
        date = self.format10(tmp.day)
        timestamp = "%s-%s-%s" % (year, month, date)
        counter += 1
        try:        
            for dis in pr.district_codes:
                html = self.craw_data(timestamp, dis, st, ed)
                values = self.mine_data(html)
                for x in values:
                    output += timestamp + " " + x[0] + ":00," + str(dis) + "," + utils.array_to_str(x[1:], ",") + "\n"
                    if (counter - last_save) == save_interval:
                        last_save = counter
                        self.write_log(output)
                        output = ""
        except Exception as e:
            print(e)
        return output, counter, last_save

    def execute(self, args):
        print("start crawling aws")
        save_interval = args.save_interval
        start = datetime.strptime(args.start, pr.fm)
        # output = "timestamp,PM10_VAL,PM2.5_VAL,O3(ppm),NO2(ppm),CO(ppm),SO2(ppm),PM10_AQI,PM2.5_AQI\n"
        output = ""
        counter = 0
        last_save = 0
        crawler_range = 86400
        if not args.forward:
            if args.end:
                end = datetime.strptime(args.end, pr.fm)
            else:
                end = utils.get_datetime_now() 
            length = (end - start).total_seconds() / crawler_range
        else:
            end = datetime.strptime("2050-12-31 00:00:00", pr.fm)
        while start <= end:
            now = utils.get_datetime_now()
            # at first, crawling by daily
            # if up to the moment, crawling by hourly
            # how long from last crawled date to now?
            if (now - start).total_seconds() > crawler_range:
                tmp = start
                st = "00"
                ed = "24"
                if crawler_range != 86400:
                    st = self.format10(tmp.hour)
                    ed = self.format10(tmp.hour + 1)
                output, counter, last_save = self.craw_data_controller(output, counter, last_save, save_interval, tmp, st, ed)
                # move pointer for timestep
                if not args.forward:
                    utils.update_progress(counter * 1.0 / length)
                else:
                    self.write_log(output)
                    output = ""
                if crawler_range == 86400:
                    start = start + timedelta(days=1)
                else:
                    start = start + timedelta(hours=1)
                print("AWS done")
            else:
                # Approach boundary (reach end) then reduce range to hourly crawling
                crawler_range = 3600
        self.write_log(output)


if __name__ == "__main__":
    crawler = CrawAWS()
    args = crawler.add_argument()
    # crawler.init_env()
    crawler.execute(args)
