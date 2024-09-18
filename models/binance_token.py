from models.order_history import OrderHistory


class BinanceToken:
    tokens = {}

    def __init__(self, symbol, thread_name):
        self.symbol = symbol
        self.is_printed = False
        self.order_history = {
            'SHORT': OrderHistory('SHORT', symbol),
            'LONG': OrderHistory('LONG', symbol)
        }
        self.thread_name = thread_name

    def add_short(self, latest_short, event_time):
        self.order_history['SHORT'].add_order(latest_short, event_time)

    def add_long(self, latest_long, event_time):
        self.order_history['LONG'].add_order(latest_long, event_time)

    @staticmethod
    def get_tokens(thread_name):
        return set(filter(lambda t: t.thread_name == thread_name, BinanceToken.tokens))
