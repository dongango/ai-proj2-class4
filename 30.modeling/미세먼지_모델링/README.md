 1. 단변량 LSTM 

- input_len=40, output_len=10, 값 예측

- 예측 성능:
PM10 RMSE: 14~19 정도, PM25 RMSE: 7~9 정도

- 모양도 실제값을 잘 따라가는 경향이 있음


2. 다변량 LSTM

- feature_cols:['temperature', 'wind_direction', 'wind_speed', 'precipitation', 'humidity', 'aod_avg']

- target_cols: ['pm10', 'pm25']

- input_len=24, output_len=6

- 예측 성능:
PM10 RMSE: 25~35 정도, PM25 RMSE: 12~17 정도

- 예측 결과 일자임


3. 향후 개선 방향

- 상관 관계 분석을 통해 관련이 높은 변수만 남기기
- scale 조정(정규화)
- 모델 구조 개선: 2층 구조 검토


## 2차 모델

1. 다변량 LSTM

- feature_cols = ['aod_avg', 'wind_speed', 'precipitation', 'temperature', 'electric']
- 피처 수를 줄임
- target_cols = ['pm10', 'pm25']

- 일 평균 집계 후 MinMaxScaler로 정규화

- 지역별로 학습 및 예측 진행
- input 14일, output 7일 예측

- 대부분 지역에서 미세먼지 추세를 잘 따라감
- 일부 지역은 RSME가 다소 큼

| 지역  | PM10 RMSE | PM2.5 RMSE |
| --- | --------- | ---------- |
| 강남구 | 21.59     | 10.75      |
| 강동구 | 26.58     | 12.43      |
| 광진구 | 38.97     | 19.16      |
| 금천구 | 20.36     | 11.67      |
| 송파구 | 40.32     | 12.92      |
| 성동구 | 21.13     | 9.85       |
| 용산구 | 26.74     | 10.48      |
| 평균  | 약 27.5±6  | 약 12.8±3   |

2. 향후 방향

- 피처수를 연관도가 큰 걸로 더 줄여보기
- feature_cols = ['aod_avg', 'wind_speed', 'precipitation']

- RMSE 외에 MAE, MAPE, R² 등도 고려해보기
