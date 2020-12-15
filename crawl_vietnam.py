import requests
import json
from utils import save_file
import numpy as np
import pandas as pd


base_url = "http://moitruongthudo.vn/public/dailyaqi/%s?site_id=%i"
factors = ["NO2","CO","PM2.5","PM10"]
vietnam_ids = [1,7,8,9,10,11,12,13,14,15,16]


def mining_data(txt):
    content = json.loads(txt)
    times = []
    values = []
    for d in content:
        times.append(d["time"])
        values.append(d["value"])
    return times, values


def get_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    file_path = "data_vietnam/data_%i.csv"
    for idx in vietnam_ids:
        s_data = []
        for f in factors:
            url = base_url % (f, idx)
            data = requests.get(url,headers=headers)
            times, values = mining_data(data.text)
            s_data.append(values)
        s_data.append(times)
        s_data = np.transpose(s_data)
        df = pd.DataFrame(s_data)
        with open(file_path % idx, 'a') as f:
            df.to_csv(f, header=False)


if __name__ == "__main__":
    get_data()