import json
import traceback
from datetime import datetime
from threading import Thread

import requests
import websocket


def get_okex_symbols():
    """
    documentation URL: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-instruments
    Public Data / REST API / Get instruments
    :return:
    """
    url = "https://www.okx.com/api/v5/public/instruments"
    params = {'instType': 'SWAP'}  # You can specify other instrument types like FUTURES, SWAP, SPOT, etc.
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        symbols = [(item['instId'], item['ctVal']) for item in data['data']]
        return symbols
    else:
        print(f"Error fetching symbols: {response.status_code}")
        return []


# Define the OKEx WebSocket endpoint for public data
# OKEX_WS_URL = "wss://wspap.okx.com:8443/ws/v5/public"

def handle_orderbook_message(ws, message):
    message_json = json.loads(message)
    try:
        if 'data' in message_json:
            data = message_json['data'][0]
            t = datetime.fromtimestamp(int(data['ts']) // 1000)
            ms = str(int(data['ts']) % 1000)
            print('\33[91m' + data['asks'][0][0] + ' '
                  + str(int(float(data['asks'][0][0]) * float(data['asks'][0][1]) * 0.01))
                  + ' ' + str(t) + ':' + ms
                  + '\033[0m')
            print('\033[92m' + data['bids'][0][0] + ' '
                  + str(int(float(data['bids'][0][0]) * float(data['bids'][0][1]) * 0.01))
                  + ' ' + str(t) + ':' + ms
                  + '\033[0m')
    except Exception:
        print('\33[31m' + str(traceback.format_exc()) + '\033[0m')


def subscribe_to_order_books(symbols):
    ws_url = "wss://ws.okx.com:8443/ws/v5/public"

    def on_open(ws):
        print(f"WebSocket connection opened")

        # Subscribe to the order book channels for all futures symbols
        for symbol in symbols:
            # TODO add 'ctVal' property to ok_ex_order class
            subscribe_message = {
                "op": "subscribe",
                "args": [{
                    "channel": "books5",  # top 5 levels, but we can subscribe to "books" for full depth
                    "instFamily": "SWAP",
                    "instId": symbol['instId']  # Specify futures symbol
                }]
            }
            ws.send(json.dumps(subscribe_message))
            print(symbol)

    def on_message(ws, message):
        handle_orderbook_message(ws, message)

    def on_error(ws, error):
        print(f"WebSocket Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"WebSocket closed: {close_msg}")

    # Start the WebSocket connection
    ws = websocket.WebSocketApp(ws_url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()


def get_trades_volume(symbol, start_time, end_time, factor, limit=100):
    """

    :param symbol:
    :param start_time:
    :param end_time:
    :param factor:
    :param limit:
    :return: volume in UDS for specified side (buy if factor is 1 else sell)
    """
    url = "https://www.okx.com/api/v5/market/trades"
    params = {
        'instId': symbol,  # Specify the symbol, e.g., BTC-USDT
        'limit': limit  # Number of trades to retrieve
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()['data']
        side = 'buy' if factor == 1 else 'sell'
        trades_in_period = list(filter(lambda x: start_time <= int(x['ts']) <= end_time and x['side'] == side, data))
        trades_sum = 0
        for trade in trades_in_period:
            trades_sum += float(trade['px']) * int(trade['sz'])
        return int(trades_sum)
    else:
        print(f"Error fetching trades: {response.status_code}")
        return None


def main():
    futures_symbols = get_okex_symbols()
    print('overall: ' + str(len(futures_symbols)))
    if futures_symbols:
        # Start WebSocket connection and subscribe to all symbols
        ws_thread = Thread(target=subscribe_to_order_books, args=(futures_symbols,))
        ws_thread.start()
    else:
        print("No futures symbols available")


# Run the main function
# if __name__ == "__main__":
#     main()
# get_okex_symbols()
# subscribe_to_order_books(['BTC-USDT-SWAP'])

# Example usage
# symbol = "BTC-USDT"
# okex_trades = get_okex_trades(symbol)
# if okex_trades:
#     print(f"Recent trades for {symbol} on OKEx:", okex_trades)
