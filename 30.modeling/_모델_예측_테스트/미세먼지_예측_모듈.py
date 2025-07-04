#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pymysql
import pandas as pd
import numpy as np
import json
import io
import tempfile  
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import timedelta


# In[13]:


# 전역 설정
INPUT_LEN = 365
PREDICT_DAYS = 7

REGIONS = [
    '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구',
    '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구',
    '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
]
POLLUTIONS = ['pm10', 'pm25']


# In[14]:


# DB config 로드
with open('db-config.json', encoding='utf-8') as f:
    DB_CONFIG = json.load(f)

def get_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG.get('port', 3306),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


# In[ ]:


def predict_for_region_pollution(region, pollution):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 모델 로드
            model_name = f"lstm_{pollution}_{region}"
            cursor.execute("""
                SELECT data
                FROM models
                WHERE name = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (model_name,))
            row = cursor.fetchone()
            if row is None:
                print(f"모델 없음: {model_name}")
                return None

            model_binary = row['data']
            with tempfile.NamedTemporaryFile(delete=True, suffix=".h5") as tmp:
                tmp.write(model_binary)
                tmp.flush()
                lstm_model = load_model(tmp.name, compile=False)

            print(f"모델 로드 완료: {model_name}")

            # 어제 기준 최신 365일 데이터 로드
            cursor.execute(f"""
                SELECT datetime, {pollution}
                FROM air_quality
                WHERE region = %s
                  AND datetime < CURDATE()
                ORDER BY datetime DESC
                LIMIT {INPUT_LEN}
            """, (region,))
            rows = cursor.fetchall()
            if len(rows) < INPUT_LEN:
                print(f"데이터 부족: {region} - {pollution}")
                return None

            df = pd.DataFrame(rows).sort_values('datetime')

            # 정규화
            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(df[[pollution]].values)

            # 예측
            input_seq = X_scaled.reshape(1, INPUT_LEN, 1)
            preds = lstm_model.predict(input_seq, verbose=0)  # (1,30)
            preds_inverse = scaler.inverse_transform(preds.reshape(-1, 1))  # (30,1)

            start_date = df['datetime'].iloc[-1] + timedelta(days=1)

            predictions = []
            for i in range(PREDICT_DAYS):
                predictions.append({
                    'datetime': start_date + timedelta(days=i),
                    'region': region,
                    'pollution': pollution,
                    'value': float(preds_inverse[i, 0])
                })

            return predictions

    finally:
        conn.close()


# In[16]:


if __name__ == "__main__":
    results = []

    for region in REGIONS:
        for pollution in POLLUTIONS:
            preds = predict_for_region_pollution(region, pollution)
            if preds is not None:
                results.extend(preds)

    result_df = pd.DataFrame(results)
    print(result_df)

    # 결과 CSV 저장 (선택)
    # result_df.to_csv("air_quality_predictions.csv", index=False)

