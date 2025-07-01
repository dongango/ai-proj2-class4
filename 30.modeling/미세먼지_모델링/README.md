 1. 단변량 LSTM 

- input_len=40, output_len=10, 값 예측

- 예측 성능:
PM10 RMSE: 14~19 정도
PM25 RMSE: 7~9 정도

- 모양도 실제값을 잘 따라가는 경향이 있음


2. 다변량 LSTM

- feature_cols:['temperature', 'wind_direction', 'wind_speed', 'precipitation', 'humidity', 'aod_avg']

- target_cols: ['pm10', 'pm25']

- input_len=24, output_len=6

- 예측 성능:
PM10 RMSE: 25~35 정도
PM25 RMSE: 12~17 정도

- 예측 결과 일자임


3. 향후 개선 방향

- 상관 관계 분석을 통해 관련이 높은 변수만 남기기
- scale 조정(정규화)
- 모델 구조 개선: 2층 구조 검토