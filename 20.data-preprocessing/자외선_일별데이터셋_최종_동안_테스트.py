#!/usr/bin/env python
# coding: utf-8

# In[12]:


import pandas as pd
from sqlalchemy import create_engine
import json

# DB 접속 정보 로드
with open('db-config.json') as f:
    config = json.load(f)

user = config['user']
password = config['password']
host = config['host']
port = config['port']
database = config['database']

# SQLAlchemy 엔진 생성
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4")



# In[13]:


uv_dataset = pd.read_sql("SELECT * FROM uv_dataset", con=engine)


# In[4]:


# 날짜만 추출해 그룹화 기준으로 사용
uv_dataset['date'] = pd.to_datetime(uv_dataset['datetime']).dt.date

# 하루 기준으로 최대값만 사용 (수치형 변수 기준)
daily = uv_dataset.groupby('date').max().reset_index()

# datetime 컬럼 재구성 (00:00:00으로 고정)
daily['datetime'] = pd.to_datetime(daily['date'].astype(str))  # → '2025-06-27 00:00:00'

# region 통일 ('서울시'로)
daily['region'] = '서울시'

# 불필요한 date 컬럼 제거
daily = daily.drop(columns=['date'])

# 정렬
daily = daily.sort_values(by='datetime').reset_index(drop=True)

# 확인
print(daily.head())


# In[5]:


print(daily['datetime'].dtype)
print(daily['datetime'].head())


# In[6]:


print(daily['datetime'].dt.time.unique())


# In[7]:


daily['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S')).head()


# In[8]:


daily


# In[9]:


print("최종 병합 데이터 크기:", daily.shape)


# In[10]:


# 테이블 덮어쓰기 저장 (기존 uv_dataset 삭제 후 재생성됨)
daily.to_sql(
    name='uv_dataset',    # 같은 테이블에 덮어쓰기
    con=engine,
    if_exists='replace',  # 삭제 후 생성
    index=False
)

print("일별 최고치 기준으로 재구성 완료 & DB 저장")


# In[11]:


daily.to_csv('자외선_일별최고치_데이터셋.csv', index=False, date_format='%Y-%m-%d %H:%M:%S')


# In[ ]:




