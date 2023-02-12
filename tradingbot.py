import asyncio, requests, json, time
import hmac, hashlib
from binance import AsyncClient, BinanceSocketManager
from prometheus_client import start_http_server, Counter, Summary, Gauge, Histogram


kline_counter = Counter("KLINE", "Number of times the data has been received so far")
LTMA_counter = Gauge("LTMA", "amount of calculated LTMA")
STMA_counter = Gauge("STMA", "amount of calculated STMA")
buy_counter = Counter("BUY", "Number of times for buying")
sell_counter = Counter("SELL", "Number of times for selling")

async def main():

    client = await AsyncClient.create(testnet='wss://testnet.binance.vision/')
    bm = BinanceSocketManager(client)

    # chose to use kline_socket method to get data
    symbol = 'BTCUSDT'
    ts = bm.kline_socket(symbol)

    async with ts as tscm:
        kline_count = 0

        # calculate simple moving average so far
        def calculate_moving_average(window, sum_of_so_far):
            sma = sum_of_so_far / window
            return sma
        
        def place_order(symbol, side, quantity, price):
            # Define the endpoint URL
            url = "https://testnet.binance.vision/api/v3/order"

            # Define the API key and secret
            api_key = "Xb8usz6gjCRsSpNtdJqjq6xLBpEs5TxJXKDdoCWWVnGVQRVfwHRUQe97n5fHiGzc"
            secret_key = "3yfTfXZnUW7RggAGfAEr5ZXYGb0YSMngXmHAuJD8T17JzwAfWJ9yn3P85IjeTR7j"

            # Define the request payload
            payload = {
                "symbol": symbol, #"BTCUSDT",
                "side": side, #"BUY",
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": quantity, #"0.5",
                "price": price, #"1000",
                "recvWindow": 5000,
                "timestamp": int(time.time() * 1000)
            }

            # Create the signature for the request
            query_string = '&'.join([f'{key}={value}' for key, value in payload.items()])
            signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
            query_string = query_string + '&signature=' + signature

            # Send a POST request to the endpoint with the query string
            headers = {
                "X-MBX-APIKEY": api_key
            }
            response = requests.post(url, headers=headers, data=query_string)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = json.loads(response.text)
                # print(data)
                if data['side'] == "SELL":
                    sell_counter.inc()
                elif data['side'] == "BUY":
                    buy_counter.inc()
            
            else:
                # If the request was not successful, print the error message
                raise ValueError("Failed to place order: " + response.text)
                # print("Request failed with status code:", response.status_code, response.text)

        close_price_list = []   #Latest LTMA and STMA are included

        while True: #kline_count < 9: # the number determines the many MA you want to set up
            res = await tscm.recv()
            close_price = float(res['k']['c'])
            kline_count += 1
            print("====================================")
            print(f"current kline count num is {kline_count}")
            kline_counter.inc()
            close_price_list.append(close_price)        # 최신 close price를 리스트에 가장 뒤에 추가
            # print(f"current list is {close_price_list}") # 데이터 로깅을 위한 프린팅 

            short_term_window = 10   # stma 기준값 
            long_term_window = 20   # ltma 기준값

            if kline_count >= long_term_window:
                sum_for_lt = sum(close_price_list)
                ltma = calculate_moving_average(long_term_window, sum_for_lt)
                print(f"LTMA is {ltma}")
                LTMA_counter.set(ltma)

                sum_for_st = sum(close_price_list[short_term_window:]) # sum for STMA
                stma = calculate_moving_average(short_term_window, sum_for_st)
                print(f"STMA is {stma}")
                STMA_counter.set(stma)
                
                del close_price_list[0] # 키포인트: 맨앞 인덱스 벨류 제거, 다음 받아올 kline으로 새로운 list를 만들기 위함

                buying_amount = 0.001   # amount depends on your own risk tolerance
                selling_amount = 0.001  

                # 매수&매도 판단 로직:
                if stma > ltma:
                    print(f"STMA is greater than LTMA, BUY signal!")
                    place_order(symbol, 'BUY', buying_amount, close_price)
                elif stma < ltma:
                    print(f"STMA is less than LTMA, SELL signal!")
                    place_order(symbol, 'SELL', selling_amount, close_price)
                else: # Just in case if stma = ltma (almost impossible)
                    pass

    # await client.close_connection()

if __name__ == "__main__":
    start_http_server(8000)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


# =========== Kline Streams DataSet =============
# {
#   "e": "kline",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "k": {
#     "t": 123400000, // Kline start time
#     "T": 123460000, // Kline close time
#     "s": "BNBBTC",  // Symbol
#     "i": "1m",      // Interval
#     "f": 100,       // First trade ID
#     "L": 200,       // Last trade ID
#     "o": "0.0010",  // Open price
#     "c": "0.0020",  // Close price
#     "h": "0.0025",  // High price
#     "l": "0.0015",  // Low price
#     "v": "1000",    // Base asset volume
#     "n": 100,       // Number of trades
#     "x": false,     // Is this kline closed?
#     "q": "1.0000",  // Quote asset volume
#     "V": "500",     // Taker buy base asset volume
#     "Q": "0.500",   // Taker buy quote asset volume
#     "B": "123456"   // Ignore
#   }
# }