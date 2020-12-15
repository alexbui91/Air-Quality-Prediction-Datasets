# _*_ coding: utf-8 _*_
import requests
from argparse import ArgumentParser
from datetime import datetime, timedelta
import json
import time
import utils
import properties as pr
from crawling_base import Crawling


"""

craw aqicn.org instantly
saving to data/aqicn.csv

"""
class CrawAQICN(Crawling):

    def __init__(self):
        self.filename = "data/aqicn.csv"
        # self.city = ['beijing', 'shenyang']
        self.city = [('1451', 'beijing'), ('1473', 'shenyang')]
    
    def mine_data(self, html):
        # pm2_5
        values = json.loads(html)
        res = 0
        if values:
            res = values["aqiv"]
        return res

    # craw aqi data from source 
    def craw_data(self, code):
        url = "http://feed.aqicn.org/xservices/refresh:%s" % code
        r = requests.get(url)
        return r.text
    
    def craw_data_controller(self, current):
        output = ""
        timestamp = "%s-%s-%s" % (current.year, self.format10(current.month), self.format10(current.day))
        hour = self.format10(current.hour)
        for i, c in self.city:
            text = self.craw_data(i)
            value = self.mine_data(text)
            output += timestamp + " " + hour + (":00,%s,%s" % (c, value)) + "\n"
        return output

    def execute(self, args):
        print("start crawling aqicn")
        save_interval = args.save_interval
        start = utils.get_datetime_now()
        start = start - timedelta(hours=1)
        output = ""
        crawler_range = 3600 * args.interval
        while True:
            now = utils.get_datetime_now()
            if (now - start).total_seconds() > crawler_range:
                output = self.craw_data_controller(now)
                # move pointer for timestep
                self.write_log(output)
                start = start + timedelta(hours=1)
                output = ""


if __name__ == "__main__":
    crawler = CrawAQICN()
    args = crawler.add_argument()
    # crawler.init_env()
    crawler.execute(args)