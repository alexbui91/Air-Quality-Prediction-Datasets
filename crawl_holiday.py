"""
craw holiday
"""

# _*_ coding: utf-8 _*_
from bs4 import BeautifulSoup as Soup
import requests
from argparse import ArgumentParser
from datetime import datetime, timedelta
import utils
import numpy as np
import properties as pr


# clear out html and get data
def mine_data(year, html):
    tables = html.find('table', attrs={"class": "zebra fw tb-cl tb-hover"}).find("tbody")
    rows = tables.find_all('tr')
    values = []
    months = np.array(pr.months)
    for r in rows:
        info = r.find_all("td")
        print(info)
        tp = info[-1].get_text()
        name = info[1].get_text()
        if tp != "Season" and tp != "Observance" and "observance" not in tp:
            d = r.find("th").get_text().split(" ")
            m_v = d[0]
            print(d)
            d_v = utils.format10(int(d[1]))
            m = np.where(months == m_v)
            m = utils.format10(m[0][0] + 1)
            date = "%s-%s-%s" % (year, m, d_v)
            values.append(date)
    return values


# craw aqi data from source 
def craw_data(year, country="south-korea"):
    url = "https://www.timeanddate.com/holidays/%s/%s" % (country, year)
    r = requests.get(url)
    html = Soup(r.text, "html5lib")
    return html
    

# write data crawled to file
def write_log(filename, output):
    if output:
        with open(filename, "a") as f:
            f.write(output)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--interval", default=1, type=int)
    parser.add_argument("-s", "--start", default=2018, type=int)
    parser.add_argument("-e", "--end", default=2018, type=int)
    parser.add_argument("-c", "--country", default="south-korea")
    
    args = parser.parse_args()

    filename = "holiday_%s_%s_%s.txt" % (args.country, args.start, args.end)
    end = args.end
    start = args.start
    # output = "timestamp,PM10_VAL,PM2.5_VAL,O3(ppm),NO2(ppm),CO(ppm),SO2(ppm),PM10_AQI,PM2.5_AQI\n"
    output = ""
    length = end - start + 1
    counter = 0
    last_save = 0
    start_point = utils.get_datetime_now()
    while start <= end:
        now = utils.get_datetime_now()
        if (now - start_point).total_seconds() >= args.interval:
            counter += 1
            # try:
            year = start
            html = craw_data(year, args.country)
            data = mine_data(year, html)
            if data:
                output += ",".join(data) + "\n"
            # except Exception as e:
            #     print(e)
            start += 1
            start_point = now   
            utils.update_progress(counter * 1.0 / length)
    write_log(filename, output)