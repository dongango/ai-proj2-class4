### 아래와 같은 형식으로 호출 운영

#### Tempate
docker run -it \\ \
  -v "$(pwd)/(수행할 파이선 코드.py):/app/(수행할 파이선 코드.py)" \\ \
  -v "$(pwd)/(추가할 파일):/app/(추가할 파일)" \\ \
  --name create_uv_day_dateset harbor.dongango.com/aiclass4/tensorflow-2.12:0.1 \\ \
  python (수행할 파이선 코드.py)

#### 예제
docker run -it \\ \
  -v "$(pwd)/create_uv_day_dateset.py:/app/create_uv_day_dateset.py" \\ \
  -v "$(pwd)/db-config.json:/app/db-config.json" \\ \
  --name create_uv_day_dateset harbor.dongango.com/aiclass4/tensorflow-2.12:0.1 \\ \
  python create_uv_day_dateset.py

  
