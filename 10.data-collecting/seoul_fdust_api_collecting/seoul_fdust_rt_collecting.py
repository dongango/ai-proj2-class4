#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
from sqlalchemy import create_engine, text
import json

# 접속 정보 로딩 (옵션: db-config.json 파일이 있을 경우)
with open('db-config.json') as f:
    config = json.load(f)

user = config['user']
password = config['password']
host = config['host']
port = config['port']
database = config['database']

# SQLAlchemy 엔진 생성
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")



# In[ ]:


# 마지막 데이타 수집일을 가져옴..

def get_latest_datetime():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(datetime) FROM air_quality"))
        row = result.fetchone()
        return row[0] if row and row[0] else datetime.datetime(2024, 1, 1)


# In[16]:


# 날짜 기준 미세먼지, 오염데이타 수집.
from xml.etree import ElementTree as ET
import requests

def fetch_air_data(ymd):
    url = f"http://openapi.seoul.go.kr:8088/735461674c646f6e393879456f456f/xml/TimeAverageAirQuality/1/700/{ymd}"
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: {response.status_code}")
        return None


# In[68]:


## 수집한 XML 데이타를 시간별 미세면지, 오염물질 데이타를 가져온다.
## NULL 값 대비 함수
def parse_float(value, default=0.0):
    try:
        return float(value) if value and value.strip().lower() != 'null' else default
    except:
        return default

## NULL 값을 대비하는 함수
def parse_int(value, default=0):
    try:
        return int(float(value)) if value and value.strip().lower() != 'null' else default
    except:
        return default
        
def parse_air_data(xml):
    quality_list = []
    pollution_list = []

    root = ET.fromstring(xml)
    rows = root.findall(".//row")
    for row in rows:
        try:
            dt_str = row.findtext("MSRDT")
            dt = datetime.datetime.strptime(dt_str, "%Y%m%d%H%M")
            region = row.findtext("MSRSTE_NM")
            pm10 = parse_int(row.findtext("PM10"))
            pm25 = parse_int(row.findtext("PM25"))

            no2 = parse_float(row.findtext("NO2"))
            co = parse_float(row.findtext("CO"))
            so2 = parse_float(row.findtext("SO2"))
            o3 = parse_float(row.findtext("O3"))

            quality_list.append({'datetime': dt, 'region': region, 'pm10': pm10, 'pm25': pm25})
            # print(dt, " qu : ", pm10)
            pollution_list.append({'datetime': dt, 'region': region, 'no2': no2, 'co': co, 'so2': so2, 'o3': o3})
            # print(dt, " po : ", o3)
        except Exception as e:
            print(dt, " ", region, " ", pm10, " ", pm25, " ", no2, " ", co, " ", so2, " ", o3)
            print(f"Parsing error: {e}")
            continue

    quality_list.sort(key=lambda x: x['datetime'])
    pollution_list.sort(key=lambda x: x['datetime'])

    return quality_list, pollution_list


# In[61]:


def save_to_db(quality_list, pollution_list):
    with engine.begin() as conn:
        for item in quality_list:
            conn.execute(text("""
                INSERT INTO air_quality (datetime, region, pm10, pm25)
                VALUES (:datetime, :region, :pm10, :pm25)
                ON DUPLICATE KEY UPDATE
                    pm10 = VALUES(pm10),
                    pm25 = VALUES(pm25)
            """), item)

        for item in pollution_list:
            conn.execute(text("""
                INSERT INTO air_pollution (datetime, region, no2, co, so2, o3)
                VALUES (:datetime, :region, :no2, :co, :so2, :o3)
                ON DUPLICATE KEY UPDATE
                    no2 = VALUES(no2),
                    co  = VALUES(co),
                    so2 = VALUES(so2),
                    o3  = VALUES(o3)
            """), item)


# In[ ]:


import datetime

last_dt = get_latest_datetime()
today = datetime.datetime.now().date()
current_date = last_dt.date()
current_date += datetime.timedelta(days=1)

print("start date : ", current_date)

while current_date <= today:
    ymd = current_date.strftime("%Y%m%d")
    print(f"Fetching data for {ymd}...")
    xml = fetch_air_data(ymd)
    if xml:
        quality, pollution = parse_air_data(xml)
        save_to_db(quality, pollution)
        print(f"{ymd}: {len(quality)} records inserted/updated.")
    time.sleep(1)
    current_date += datetime.timedelta(days=1)


