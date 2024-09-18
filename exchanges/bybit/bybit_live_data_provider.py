import traceback
from datetime import datetime

import requests
from pybit.unified_trading import WebSocket, HTTP

# Define the symbol for which you want to subscribe to the order book
TOKENS_COUNT_TO_FOLLOW = 100
NOT_USEFUL_TOKENS = {'BTCUSDT'}


def handle_orderbook_message(message):
    # Check if the incoming message is an order book update
    # print(message)
    try:
        if 'data' in message:
            t = datetime.fromtimestamp(message['cts'] // 1000)
            ms = str(message['cts'] % 1000)
            print('\33[91m' + message['data']['a'][0][0] + ' '
                  + str(int(float(message['data']['a'][0][0]) * float(message['data']['a'][0][1])))
                  + ' ' + str(t) + ':' + ms
                  + '\033[0m')
            print('\033[92m' + message['data']['b'][0][0] + ' '
                  + str(int(float(message['data']['b'][0][0]) * float(message['data']['b'][0][1])))
                  + ' ' + str(t) + ':' + ms
                  + '\033[0m')
    except Exception:
        print('\33[31m' + str(traceback.format_exc()) + '\033[0m')


def get_all_symbols():
    session = HTTP()
    response = session.get_instruments_info(category="linear")
    if response['retCode'] == 0:
        symbols = [symbol['symbol'] for symbol in response['result']['list']]
        print(len(symbols))
        symbols = set(filter(lambda s: s.endswith('USDT'), symbols))
        print(len(symbols))
        return list(symbols - NOT_USEFUL_TOKENS)
    else:
        print("Failed to fetch symbols:", response['retMsg'])


def open_socket(symbol, message_handler, db_connection=None):
    """

    :param symbol:
    :param message_handler:
    :param db_connection:
    :return:
    """
    # Create an instance of the WebSocket class from pybit
    ws = WebSocket(testnet=False,
                   trace_logging=False,
                   channel_type='linear')

    # Subscribe to the order book channel for the given symbol
    ws.orderbook_stream(
        depth=1,
        symbol=symbol,
        callback=message_handler
    )


def open_all_connections(message_handler, db_connection=None):
    symbols = get_all_symbols()
    print(len(symbols))
    if len(symbols) > TOKENS_COUNT_TO_FOLLOW:
        symbols = symbols[:TOKENS_COUNT_TO_FOLLOW]
    print(*symbols, sep='\n')
    for symbol in symbols:
        open_socket(symbol.lower(), message_handler, db_connection)


def get_bybit_trades(symbol, start_time, end_time, factor, limit=100):
    url = "https://api.bybit.com/v5/market/recent-trade"
    params = {
        'category': 'linear',  # Specify contract type, e.g., 'linear' for USDT perpetual
        'symbol': symbol,  # Specify the symbol, e.g., BTCUSDT
        'limit': limit  # Number of trades to retrieve
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        trades = data['result']['list']
        side = 'Buy' if factor == 1 else 'Sell'
        trades_in_period = list(
            filter(lambda x: start_time <= int(x['time']) <= end_time and x['side'] == side, trades))
        trades_sum = 0
        for trade in trades_in_period:
            trades_sum += float(trade['price']) * int(trade['size'])
        return int(trades_sum)
    else:
        print(f"Error fetching trades: {response.status_code}")
        return None


# while True:
#     sleep(1)
