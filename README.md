# python을 활용한 binanace testnet과 socket 통신하는 trading bot

## INTERVAL 1M을 기준으로 STMA 와 LTMA 값을 계산하여, 매수매도를 판단하는 로직입니다.

## Prometheus를 활용하여 모니터링을 적용하였습니다.
1. kline_count = socket 통신으로 인한 데이터를 받아오는 단위를 뜻합니다.
2. LTMA_amount = Latest 장기MA 값
3. STMA_amount = Latest 단기MA 값
4. buy_counter = 매수 횟수
5. sell_counter = 매도 횟수

## Terraform을 이용한 배포
 - EC2 instance .tf 파일을 이용하여 생성
## github action을 이용한 CI /CD
 - push와 같은 동작으로 repository에 수정사항이 반영될때, ec2 접근 및 deploy
