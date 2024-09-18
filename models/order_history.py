import statistics
from collections import deque
from datetime import datetime

from util.constants import Consts as C


class OrderHistory:

    def __init__(self, order_type, symbol):
        self.symbol = symbol
        self.__order_type = order_type
        self.__orders = deque(maxlen=C.VOLUMES_CAPACITY)
        self.__last_index = -1

        self.__first_big_volume = None
        self.__first_big_order_price = None
        self.__first_big_volume_detection_time = None
        self.__is_small_volume_detected = False
        self.__last_order_time = None
        self.__is_data_reset = True

    @property
    def order_type(self):
        return self.__order_type

    @property
    def orders(self):
        return self.__orders

    @property
    def first_big_volume(self):
        return self.__first_big_volume

    @property
    def first_big_order_price(self):
        return self.__first_big_order_price

    @property
    def last_index(self):
        return self.__last_index

    @property
    def first_big_volume_detection_time(self):
        return self.__first_big_volume_detection_time

    @property
    def is_small_volume_detected(self):
        return self.__is_small_volume_detected

    @property
    def last_order_time(self):
        return self.__last_order_time

    @property
    def is_data_reset(self):
        return self.__is_data_reset

    @first_big_volume.setter
    def first_big_volume(self, value):
        self.__first_big_volume = value
        self.__is_data_reset = False

    @first_big_order_price.setter
    def first_big_order_price(self, value):
        self.__first_big_order_price = value
        self.__is_data_reset = False

    @first_big_volume_detection_time.setter
    def first_big_volume_detection_time(self, value):
        self.__first_big_volume_detection_time = value
        self.__is_data_reset = False

    @is_small_volume_detected.setter
    def is_small_volume_detected(self, value):
        self.__is_small_volume_detected = value
        self.__is_data_reset = False

    @last_order_time.setter
    def last_order_time(self, value):
        self.__last_order_time = value
        self.__is_data_reset = False

    def add_order(self, latest_order, event_time):
        converted_order = (float(latest_order[C.PRICE]),
                           int(float(latest_order[C.VOLUME]) * float(latest_order[C.PRICE])),
                           event_time)
        self.orders.append(converted_order)
        target_volume = self.get_target_volume()
        event_second = datetime.fromtimestamp(event_time // 1000).second
        if event_second < C.BOT_START_MAX_SECOND:
            latest_order_volume = self.orders[-1][C.VOLUME]
            if latest_order_volume > target_volume and not self.first_big_volume:
                self.first_big_volume = latest_order_volume
                self.first_big_volume_detection_time = event_time
                self.first_big_order_price = self.orders[-1][C.PRICE]

    @property
    def median_volume(self):
        start_index = len(self.orders) // 2 - len(self.orders) // 10
        end_index = len(self.orders) // 2 + len(self.orders) // 10 + 1

        volumes = [order[C.VOLUME] for order in self.__orders]
        return statistics.mean(sorted(volumes[start_index:end_index]))

    def get_target_volume(self):
        target_volume = self.median_volume * C.SIGNIFICANT_CHANGE_FACTOR

        target_volume = max(C.MINIMUM_TARGET_VOLUME, int(target_volume))
        return target_volume

    def is_big_volume_detected(self):
        return (self.first_big_volume_detection_time is not None
                and self.first_big_volume_detection_time != self.orders[-1][C.TIME])

    def reset_data(self):
        if not self.__is_data_reset:
            self.__first_big_volume_detection_time = None
            self.__first_big_volume = None
            self.__first_big_order_price = None
            self.__is_small_volume_detected = False
            self.__last_order_time = None
            self.__is_data_reset = True
