# Air Quality Prediction Datasets
This repository lists up crawled air quality data, meteorological data, and other data, which can be used for air quality prediction or weather forecast problem. If you use our provided codes and data, please cite our publications:

```
@article{bui2018deep,
  title={A deep learning approach for forecasting air pollution in South Korea using LSTM},
  author={Bui, Tien-Cuong and Le, Van-Duc and Cha, Sang-Kyun},
  journal={arXiv preprint arXiv:1804.07891},
  year={2018}
}
```
```
@article{bui2020star,
  title={STAR: Spatio-Temporal Prediction of Air Quality Using A Multimodal Approach},
  author={Bui, Tien-Cuong and Kim, Joonyoung and Kang, Taewoo and Lee, Donghyeon and Choi, Junyoung and Yang, Insoon and Jung, Kyomin and Cha, Sang Kyun},
  journal={arXiv preprint arXiv:2003.02632},
  year={2020}
}
```

```
@inproceedings{le2020spatiotemporal,
  title={Spatiotemporal deep learning model for citywide air pollution interpolation and prediction},
  author={Le, Van-Duc and Bui, Tien-Cuong and Cha, Sang-Kyun},
  booktitle={2020 IEEE International Conference on Big Data and Smart Computing (BigComp)},
  pages={55--62},
  year={2020},
  organization={IEEE}
}
```

Please assure that you install required libraries to execute crawling services

- Install lxml following this [guide](https://lxml.de/installation.html)
- Install BeautifulSoup:
  - `pip install beautifulsoup4`

Purposes of crawling scripts:

- `crawl_holiday.py`: Crawl a list of holidays of South Korea and China (Can be arbitrary to any country with corresponding url from timeanddate.com). You can simply execute `python crawl_holiday.py -s 2018 -e 2020 -c south-korea` meaning crawling a list of holidays in South Korea from 2018 to 2020.
- `crawl_aws.py`: it was used to crawl weather data from stations across Seoul areas. Unfortunately, the public website has been shutdown recently. You can refer to our crawled data [here](https://drive.google.com/file/d/1ugI0ju4K81J2aPcyxP6gmJA_P8LpkJiP/view?usp=sharing). The data were collected from 2008 to 2018 with size about 8GB in text format.
- `crawl_weather.py`: This script can be used to collect weather data both in the past and future from [worldweatheronline.com](worldweatheronline.com). Plz check file `crawling_base.py` for argument descriptions.
- `crawl_seoul_aqi.py`: This script collects AQI data of 25 districts in Seoul with granularity of 1 hour that means one day has 24*25 records. To run the script, please refer to arguments in `crawling_base.py`.
- `crawling_aqicn.py`: This script collects AQI data of cities in China from Berkeley Air. It has the same granularity with Seoul AQI. To run the script, please refer to arguments in `crawling_base.py`.
- `crawl_vietnam.py`: we planned to extend our work to air quality prediction in some cities in Vietnam. However, this work is suspended. 


Note: Some functions were written in python 2.7 and are not guaranteed to work well. However, occurred errors should not be difficult to fix.

All collected data are listed [in our Google drive](https://drive.google.com/drive/folders/1YQ3LltilM3lcTuYNsTlocEyeXV4vVjO5?usp=sharing).