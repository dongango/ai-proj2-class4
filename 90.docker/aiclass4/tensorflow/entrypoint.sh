#!/bin/bash
# entrypoint.sh

# bashrc 적용
source /root/.bashrc

# conda 환경 실행 및 전달된 명령 실행
conda run --no-capture-output -n py311 "$@"
