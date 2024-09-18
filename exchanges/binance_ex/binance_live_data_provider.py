import random
import aiohttp
import asyncio
from binance.error import ClientError
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from data_management.db_manager import create_orders_table
from models.binance_token import BinanceToken
from test.symbols_provider import get_all_symbols_cache
from util.constants import Consts as C

api_key = 'your_api_key_here'
api_secret = 'your_api_secret_here'
NOT_USEFUL_TOKENS = {"1000SHIBUSDT", "ALICEUSDT", "ATOMUSDT", "BCHUSDT", "BNBUSDT",
                     "BTCUSDT", "DOGEUSDT", "DOTUSDT", "ETHUSDT", "ETCUSDT",
                     "ETHFIUSDT", "FLOWUQST", "GALAUSDT", "XLMUSDT", "XEMUSDT",
                     "XRPUSDT", "TRXUSDT", "1000PEPEUSDT", "1000FLOKIUSDT", "NEIROETHUSDT"}

um_futures_client = UMFutures()


def get_all_symbols():
    try:
        exchange_inf = um_futures_client.exchange_info()
        symbols = [symbol_info['symbol'] for symbol_info in exchange_inf['symbols']]
        symbols = set(filter(lambda s: s.endswith('USDT'), symbols))
        return list(symbols - NOT_USEFUL_TOKENS)
    except ClientError as e:
        print(f"Error occurred: {e.error_message}")
        return None


def get_socket_client(on_message, on_error):
    return UMFuturesWebsocketClient(on_message=on_message, on_error=on_error)


def open_socket(symbol, um_socket_client, db_connection=None):
    """
    # USD-M Futures / Websocket Market Streams / Partial Book Depth Streams
    response example:
    {
        "e": "depthUpdate", // Event type
        "E": 1571889248277, // Event time
        "T": 1571889248276, // Transaction time
        "s": "BTCUSDT",
        "U": 390497796,
        "u": 390497878,
        "pu": 390497794,
        //     | Price  | Quantity
        "b": [["7403.89", "0.002"], ...],
        "a": [["7405.96", "3.340"], ...]
    }
    :param on_close:
    :param um_socket_client:
    :param symbol:
    :param on_message:
    :param db_connection:
    :return:
    """
    if db_connection:
        create_orders_table(db_connection, symbol, C.CLEAN_OLD_ORDERS)
    BinanceToken.tokens[symbol] = BinanceToken(symbol, um_socket_client.socket_manager.name)
    um_socket_client.partial_book_depth(
        symbol=symbol
    )


def open_all_connections(on_message, on_close, db_connection=None):
    symbols = get_all_symbols_cache()
    # symbols = get_all_symbols()
    print(len(symbols))
    if len(symbols) > C.TOKENS_COUNT_TO_FOLLOW:
        symbols = symbols[:C.TOKENS_COUNT_TO_FOLLOW]
    print(*symbols, sep='\n')
    counter = 0
    socket_client = UMFuturesWebsocketClient(on_message=on_message, on_close=on_close)
    for symbol in symbols:
        if counter >= 3:
            socket_client = UMFuturesWebsocketClient(on_message=on_message, on_close=on_close)
            counter = 0
        open_socket(symbol.lower(), socket_client, db_connection)
        counter += 1


trade_volumes = [23, 456, 312, 34, 4554, 23, 434, 45, 768, 312, 56765, 34, 234, 45, 565, 676, 434, 876, 1200, 2400, 100]


def get_trades_volume_mock(symbol, start_time, end_time, factor):
    C.increment(symbol)
    if C.AGG_TRADES_CALLS_COUNT_PER_MINUTE > 50:
        print('\33[43m================= TOO MUCH CALLS =================\033[0m')
    return random.choice(trade_volumes)


def get_trades_volume(symbol, start_time, end_time, factor):
    """
    USD-M Futures / Market Data Endpoints / Compressed/Aggregate Trades List
    path: GET /fapi/v1/aggTrades
    response example:
    [
        {
            "a": 26129,         // Aggregate tradeId
            "p": "0.01633102",  // Price
            "q": "4.70443515",  // Quantity
            "f": 27781,         // First tradeId
            "l": 27781,         // Last tradeId
            "T": 1498793709153, // Timestamp
            "m": true,          // Was the buyer the maker?
        }
    ]
    :param symbol:
    :param start_time:
    :param end_time:
    :param factor: should be passed 1 if position is long, otherwise any other number(e.g. -1)
    :return: the sum of the values where the maker is buyer or seller depending on factor param
    """
    if symbol and start_time and end_time and factor:
        trades = um_futures_client.agg_trades(symbol=symbol, startTime=start_time, endTime=end_time)
        is_count_market_buyers = factor == 1
        total_value = 0.0
        for trade in trades:
            if is_count_market_buyers:
                if trade['m']:
                    total_value += float(trade['q']) * float(trade['p'])
            else:
                if not trade['m']:
                    total_value += float(trade['q']) * float(trade['p'])
        return total_value
    else:
        print('some parameters are falsy', symbol, start_time, end_time, factor)
        return None


async def fetch_agg_trades_volume(symbol, start_time, end_time, factor):
    url = "https://fapi.binance.com/fapi/v1/aggTrades"
    params = {
        'symbol': symbol,
        'startTime': start_time,
        'endTime': end_time
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                trades = await response.json()
                is_count_market_buyers = factor == 1
                total_value = 0.0
                for trade in trades:
                    if is_count_market_buyers:
                        if trade['m']:
                            total_value += float(trade['q']) * float(trade['p'])
                    else:
                        if not trade['m']:
                            total_value += float(trade['q']) * float(trade['p'])
                return total_value
            else:
                print(f"Error fetching open interest: {response.status}")
                return None
