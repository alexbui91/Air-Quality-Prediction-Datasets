# _*_ coding: utf-8 _*_
import subprocess
from lxml import etree
import requests
from argparse import ArgumentParser
import math
import properties as pr

class Crawling(object):
    
    def __init__(self):
        self.filename = ""
        pass

    def mine_data(self, html):
        return ""
    
    def craw_data_controller(self):
        return ""

    def craw_data(self):
        return ""
    
    # format hour, day < 10 to 10 format
    def format10(self, no):
        if no < 10:
            return "0" + str(no)
        else:
            return str(no)
    
    # write data crawled to file
    def write_log(self, output):
        if output:
            with open(self.filename, "a") as f:
                f.write(output)

    def Linear(self, AQIhigh, AQIlow, Conchigh, Conclow, Concentration):
        Conc = float(Concentration)
        a = ((Conc - Conclow) / (Conchigh - Conclow)) * (AQIhigh - AQIlow) + AQIlow
        # linear = round(a)
        return a

    # convert pm10 micro value to aqi value
    def AQIPM10(self, Concentration):
        Conc = float(Concentration)
        c = math.floor(Conc)
        if (c >= 0 and c < 55):
            AQI = self.Linear(50, 0, 54, 0, c)
        elif(c >= 55 and c < 155):
            AQI = self.Linear(100, 51, 154, 55, c)
        elif(c >= 155 and c < 255):
            AQI = self.Linear(150, 101, 254, 155, c)
        elif(c >= 255 and c < 355):
            AQI = self.Linear(200, 151, 354, 255, c)
        elif(c >= 355 and c < 425):
            AQI = self.Linear(300, 201, 424, 355, c)
        elif(c >= 425 and c < 505):
            AQI = self.Linear(400, 301, 504, 425, c)
        elif(c >= 505 and c < 605):
            AQI = self.Linear(500, 401, 604, 505, c)
        else:
            AQI = 0
        return AQI


    # convert pm25 micro value to aqi value
    def AQIPM25(self, Concentration):
        Conc = float(Concentration)
        c = (math.floor(10 * Conc)) / 10
        if (c >= 0 and c < 12.1):
            AQI = self.Linear(50, 0, 12, 0, c)
        elif (c >= 12.1 and c < 35.5):
            AQI = self.Linear(100, 51, 35.4, 12.1, c)
        elif (c >= 35.5 and c < 55.5):
            AQI = self.Linear(150, 101, 55.4, 35.5, c)
        elif (c >= 55.5 and c < 150.5):
            AQI = self.Linear(200, 151, 150.4, 55.5, c)
        elif (c >= 150.5 and c < 250.5):
            AQI = self.Linear(300, 201, 250.4, 150.5, c)
        elif (c >= 250.5 and c < 350.5):
            AQI = self.Linear(400, 301, 350.4, 250.5, c)
        elif (c >= 350.5 and c < 500.5):
            AQI = self.Linear(500, 401, 500.4, 350.5, c)
        else:
            AQI = 0
        return AQI
    

    def aqi_pm25_china(self, c):
        c = (math.floor(10 * c)) / 10
        if (c >= 0.0 and c < 35.1):
            AQI = self.Linear(50.0, 0, 35.0, 0, c)
        elif (c >= 35.1 and c < 75.0):
            AQI = self.Linear(100.0, 51, 75.0, 35.1, c)
        elif (c >= 75.0 and c < 115.0):
            AQI = self.Linear(150, 101, 115.0, 75.1, c)
        elif (c >= 115.0 and c < 150.0):
            AQI = self.Linear(200.0, 151.0, 150.0, 115.1, c)
        elif (c >= 150.0 and c < 250.0):
            AQI = self.Linear(300.0, 201.0, 250.0, 150.1, c)
        elif (c >= 250.0 and c < 500.0):
            AQI = self.Linear(500.0, 301.0, 500.0, 250.1, c)
        else:
            AQI = 0.
        return AQI
    

    def aqi_pm25_china_class(self, c):
        c = (math.floor(10 * c)) / 10
        if (c >= 0.0 and c < 35.1):
            return 0
        elif (c >= 35.1 and c < 75.0):
            return 1
        elif (c >= 75.0 and c < 115.0):
            return 2
        elif (c >= 115.0 and c < 150.0):
            return 3
        elif (c >= 150.0 and c < 250.0):
            return 4
        elif (c >= 250.0):
            return 5
        return 0


    def InvLinear(self, AQIhigh, AQIlow, Conchigh, Conclow, a):
        c=((a-AQIlow)/(AQIhigh-AQIlow))*(Conchigh-Conclow)+Conclow
        return c


    def ConcPM25(self, a):
        if a>=0 and a<=50:
            ConcCalc=self.InvLinear(50,0,12,0,a)
        elif a>50 and a<=100:
            ConcCalc=self.InvLinear(100,51,35.4,12.1,a)
        elif a>100 and a<=150:
            ConcCalc=self.InvLinear(150,101,55.4,35.5,a)
        elif a>150 and a<=200:
            ConcCalc=self.InvLinear(200,151,150.4,55.5,a)
        elif a>200 and a<=300:
            ConcCalc=self.InvLinear(300,201,250.4,150.5,a)
        elif a>300 and a<=400:
            ConcCalc=self.InvLinear(400,301,350.4,250.5,a)
        elif a>400 and a<=500:
            ConcCalc=self.InvLinear(500,401,500.4,350.5,a)
        else:
            ConcCalc=0
        return ConcCalc


    def ConcPM10(self, a):
        if a>=0 and a<=50:
            ConcCalc=self.InvLinear(50,0,54,0,a)
        elif a>50 and a<=100:
            ConcCalc=self.InvLinear(100,51,154,55,a)
        elif a>100 and a<=150:
            ConcCalc=self.InvLinear(150,101,254,155,a)
        elif a>150 and a<=200:
            ConcCalc=self.InvLinear(200,151,354,255,a)
        elif a>200 and a<=300:
            ConcCalc=self.InvLinear(300,201,424,355,a)
        elif a>300 and a<=400:
            ConcCalc=self.InvLinear(400,301,504,425,a)
        elif a>400 and a<=500:
            ConcCalc=self.InvLinear(500,401,604,505,a)
        else:
            ConcCalc = 0.
        return ConcCalc


    def init_env(self):
        subprocess.call("source activate tensorflow")
    
    def add_argument(self):
        parser = ArgumentParser()
        parser.add_argument("-f", "--forward", default=1, type=int, help="continuously collecting flag")
        parser.add_argument("-i", "--interval", default=1, type=int, help="interval time to activate crawling service")
        parser.add_argument("-si", "--save_interval", default=1, type=int, help="interval time to save data")
        # parser.add_argument("-s", "--start", default="2009-03-01 00:00:00", type=str)
        parser.add_argument("-s", "--start", default="2018-10-16 00:00:00", type=str, help="the start crawling point")
        parser.add_argument("-c", "--city", type=str, default="seoul,beijing,shenyang", help="crawl data of a city")
        parser.add_argument("-e", "--end", type=str, help="the end crawling point")
        args = parser.parse_args()
        return args


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-n", "--number", type=float)
    args = parser.parse_args()

    crawling = Crawling()
    print(crawling.ConcPM25(args.number))
