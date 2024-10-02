#!/usr/bin/env python
import json
import logging
import random
import traceback
from datetime import datetime
from threading import Thread

from util.printer import Printer
from time import sleep

from binance.lib.utils import config_logging
from playsound import playsound
from websocket import WebSocketConnectionClosedException

from data_management.db_manager import *
from exchanges.binance_ex.binance_live_data_provider import *

config_logging(logging, logging.WARN)
cases_to_check = []

if C.RUN_WITH_DB:
    db_connection = get_db_connection()
    create_bot_detection_data_table(db_connection, C.CLEAN_OLD_BOT_DATA)
else:
    db_connection = None


def lose_socket_connection_handler(ws):
    print(ws.name + ' is closed')


def message_handler(ws, message):
    try:
        data = json.loads(message)
        if 's' not in data:
            print("'s'")
            return
        handle_data(data)
    except WebSocketConnectionClosedException:
        print(C.GREEN + str(traceback.format_exc()) + C.RESET_COLOR)
    except ClientError:
        print('total calls:', C.AGG_TRADES_CALLS_COUNT_TOTAL)
        print(C.GREEN + str(traceback.format_exc()) + C.RESET_COLOR)
    except Exception:
        print('total calls :', C.AGG_TRADES_CALLS_COUNT_TOTAL)
        print(C.GREEN + str(traceback.format_exc()) + C.RESET_COLOR)


def handle_data(data):
    symbol = data['s']
    transaction_time = data['T']
    token = BinanceToken.tokens[symbol.lower()]

    add_order_data(token, data, transaction_time)
    event_second = datetime.fromtimestamp(transaction_time // 1000).second

    if event_second < C.BOT_WORKING_SECONDS_LIMIT:
        handle_latest_order_value_change(token, 'SHORT', transaction_time)
        handle_latest_order_value_change(token, 'LONG', transaction_time)
    else:
        token.order_history['SHORT'].reset_data()
        token.order_history['LONG'].reset_data()


def add_order_data(token, data, event_time):
    shorts = data['a']
    longs = data['b']
    token.add_short(shorts[0], event_time)
    token.add_long(longs[0], event_time)
    handle_db_part(token, shorts, longs, event_time)


def handle_db_part(token, shorts, longs, event_time):
    if C.RUN_WITH_DB:
        symbol = token.symbol
        ask_price = shorts[0][C.PRICE]
        ask_volume = int(float(shorts[0][C.VOLUME]) * float(ask_price))
        bid_price = longs[0][C.PRICE]
        bid_volume = int(float(longs[0][C.VOLUME]) * float(bid_price))
        order_time = datetime.fromtimestamp(event_time // 1000)
        order_time_millis = event_time
        insert_order_data(db_connection,
                          symbol,
                          ask_price,
                          ask_volume,
                          bid_price,
                          bid_volume,
                          order_time,
                          order_time_millis)


def handle_latest_order_value_change(token, order_type, event_time):
    order_history = token.order_history[order_type]
    if order_history.is_big_volume_detected():
        factor = C.SHORT_FACTOR if order_type == 'SHORT' else C.LONG_FACTOR
        # TODO change to True/False
        res = is_time_to_check_results(order_history, event_time, factor)
        if res in ['Time', 'Price', 'Volume']:
            cases_to_check.append({'symbol': token.symbol,
                                   'order_type': order_type,
                                   'reason': res,
                                   'start_price': order_history.first_big_order_price,
                                   'start_time': order_history.first_big_volume_detection_time,
                                   'start_volume': order_history.first_big_volume,
                                   'end_price': order_history.orders[-1][C.PRICE],
                                   'end_time': order_history.last_order_time,
                                   'end_volume': order_history.orders[-1][C.VOLUME]})
            # check_for_significant_results(token.symbol, order_history, order_type, factor, res)
            order_history.reset_data()


def is_time_to_check_results(order_history, event_time, factor):
    event_second = datetime.fromtimestamp(event_time // 1000).second
    first_big_volume_detection_second = datetime.fromtimestamp(
        order_history.first_big_volume_detection_time // 1000).second
    seconds_after_first_big_volume_detected = event_second - first_big_volume_detection_second
    current_price = order_history.orders[-1][C.PRICE]
    previous_price = order_history.orders[-2][C.PRICE]
    latest_order_volume = order_history.orders[-1][C.VOLUME]
    # TODO consider to remove time constraint
    if seconds_after_first_big_volume_detected > C.BOT_WORK_DURATION:
        order_history.last_order_time = event_time
        return 'Time'  # True
    # Checks if price changed negative
    if (current_price - previous_price) * factor < 0:
        order_history.last_order_time = event_time
        return 'Price'  # True
    # Checks if price changed positive
    elif (current_price - previous_price) * factor > 0:
        # order_history.price_change_time = event_time
        return False
    else:
        is_small_volume = is_volume_small(order_history, latest_order_volume)
        if is_small_volume:
            order_history.last_order_time = event_time
            return 'Volume'  # Delete this row
        return is_small_volume


def is_volume_small(order_history, latest_volume):
    # TODO consider other options for small volume size
    # checks if after finding the first big volume found small volume
    return latest_volume < order_history.median_volume * 2


def check_for_significant_results(data):
    symbol = data['symbol']
    start_time = data['start_time']
    end_time = data['end_time']
    factor = 1 if data['order_type'] == 'LONG' else -1
    async with get_trades_volume(symbol, start_time, end_time, factor) as trades_volume:
        trades_volume = get_trades_volume_mock(symbol, data['start_time'], data['end_time'], factor)
        one_percent = data['start_volume'] / 100
        realized_value_percent = round(trades_volume / one_percent)
        big_vol_detect_datetime = datetime.fromtimestamp(data['start_time'] // 1000)
        is_enough_volume_realized = realized_value_percent >= C.BIG_VOLUME_PERCENT_TO_BE_TRADED
        big_volume_existence_duration = data['end_time'] - data['start_time']
        #  init print data ------------------------START------------------------
        Printer.symbol = symbol
        Printer.start_price = data['start_price']
        Printer.first_big_volume = data['start_volume']
        Printer.big_volume_existence_duration = big_volume_existence_duration
        Printer.end_price = data['end_price']
        Printer.end_volume = data['end_volume']
        Printer.trades_volume = trades_volume
        Printer.realized_value_percent = realized_value_percent
        Printer.first_big_volume_detection_time = big_vol_detect_datetime
        Printer.last_order_time = datetime.fromtimestamp(data['end_time'] // 1000)
        Printer.first_big_volume_detection_time_millis = data['start_time'] % 1000
        Printer.last_volume_detection_millis = data['end_time'] % 1000
        Printer.reason = data['reason']
        Printer.color = C.DARK_RED if data['order_type'] == 'SHORT' else C.DARK_GREEN
        #  init print data -------------------------END-------------------------
        if is_enough_volume_realized:
            if C.RUN_WITH_DB:
                insert_bot_data(db_connection=db_connection,
                                symbol=symbol,
                                order_type=data['order_type'],
                                first_big_volume=data['start_volume'],
                                first_big_volume_detection_time_millis=data['start_time'],
                                first_big_volume_detection_time=big_vol_detect_datetime,
                                data_record_time=datetime.now(),
                                big_volume_existence_duration=big_volume_existence_duration,
                                trades_volume=trades_volume,
                                realized_value_percent=realized_value_percent)

            Printer.color = C.DARK_RED_FILL if data['order_type'] == 'SHORT' else C.DARK_GREEN_FILL
        # playsound("D:/srap/Python Projects/Trading/minutely_volume_detector/media/sound_beep-07a.wav")
        Printer.print_row()


def handle_price_change(orders_since_first_big, factor):
    first_big_volume_price = orders_since_first_big[0][C.PRICE]
    previous_price = first_big_volume_price
    is_price_changed_opposite = False
    opposite_price_change_time = None
    for i in range(1, len(orders_since_first_big)):
        # if True it means that the big volume order either canceled or realized at current time
        if is_price_lower_than_previous_price(previous_price, orders_since_first_big, i, factor):
            if not is_price_changed_opposite:
                opposite_price_change_time = orders_since_first_big[i - 1][C.TIME]
                is_price_changed_opposite = True
                break
        previous_price = orders_since_first_big[i][C.PRICE]
    return (is_price_changed_opposite,
            opposite_price_change_time)


def is_price_lower_than_previous_price(previous_price, orders_since_first_big, index, factor):
    return (previous_price - orders_since_first_big[index][C.PRICE]) * factor > 0


def main():
    open_socket('sunusdt', get_socket_client(message_handler, lose_socket_connection_handler))
    # open_all_connections(message_handler, lose_socket_connection_handler)


try:
    thread = Thread(target=main)
    thread.start()
    while True:
        now = datetime.now()

        print('------------------------ ' + str(now) + ' ------------------------', C.AGG_TRADES_CALLS_COUNT_PER_MINUTE,
              C.AGG_TRADES_CALLS_COUNT_TOTAL)
        C.reset()
        Printer.print_header()

        sleep(20)
        counter = 0
        limit = 4
        for data in cases_to_check:
            asyncio.run(check_for_significant_results(data))
            if counter >= limit:
                counter = 0
                sleep(1)
        now = datetime.now()
        sleep(60 - now.second)
except WebSocketConnectionClosedException:
    print(C.YELLOW + str(traceback.format_exc()) + C.RESET_COLOR)
