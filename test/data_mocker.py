import random
from datetime import datetime

from util.constants import Consts as C


class DataMocker:

    def __init__(self):
        # self.__is_data_reset = True
        self.current_price = 0.020001
        self.big_volume_time = None
        self.big_volume_price = None
        self.bot_work_duration = None
        self.bot_start_second = None
        self.is_done = False

    def mock_data(self, data):
        event_time = data['E']
        event_second = datetime.fromtimestamp(event_time // 1000).second
        if event_second <= C.BOT_WORKING_SECONDS_LIMIT + 1:
            if C.MOCK_CASE is C.MOCK_CASE_BAD:
                self.mock_case_bad(data, 'b')
            elif C.MOCK_CASE is C.MOCK_CASE_GOOD_1:
                self.mock_case_good_1(data, 'b')
            elif C.MOCK_CASE is C.MOCK_CASE_GOOD_2:
                self.mock_case_good_2(data, 'b')
            elif C.MOCK_CASE is C.MOCK_CASE_VERY_GOOD:
                self.mock_case_very_good(data, 'b')
            elif C.MOCK_CASE is C.MOCK_CASE_PERFECT:
                self.mock_case_perfect(data, 'b')
        else:
            self.reset_data()
            self.mock_neutral_volume(data, 'a')
            self.mock_neutral_price(data, 'a')
            self.mock_neutral_volume(data, 'b')
            self.mock_neutral_price(data, 'b')

    def mock_neutral_volume(self, data, order_type):
        """
        mocks the data in a way that no big values appear
        :return:
        """
        orders = data[order_type]
        # converts USDs to token quantity
        volume = random.randint(C.MOCK_USUAL_VALUE_MIN, C.MOCK_USUAL_VALUE_MAX) / float(orders[0][C.PRICE])
        orders[0][C.VOLUME] = volume

    def mock_neutral_price(self, data, order_type):
        """
        mocks the data in a way that no big values appear
        :return:
        """
        orders = data[order_type]
        price = float(self.current_price)
        self.current_price = random.choice([self.get_step_up_price(price), self.get_step_down_price(price), price])
        orders[0][C.PRICE] = self.current_price

    def mock_case_bad(self, data, order_type):
        """
        mocks the data in a way that during the period when bot supposed to work
        at first mocks a big volume and then
        changes the price in opposite way to make the price change negative related to the first big value appearing
        :return:
        """
        # TODO consider to take into account points below:
        # 1. big volume changes
        # 2. big volume realization
        # 3. price direction before negative change
        event_time = data['E']
        orders = data[order_type]
        self.mock_neutral_volume(data, 'a' if order_type == 'b' else 'b')
        self.mock_neutral_price(data, 'a' if order_type == 'b' else 'b')
        if self.is_data_reset():
            # self.bot_start_second = random.randint(C.MOCK_BOT_START_SECOND_MIN, C.MOCK_BOT_START_SECOND_MAX)
            # self.bot_work_duration = random.randint(C.MOCK_BOT_WORK_DURATION_MIN, C.MOCK_BOT_WORK_DURATION_MIN)
            self.bot_start_second = 1
            self.bot_work_duration = C.BOT_WORK_DURATION
        else:
            event_second = datetime.fromtimestamp(event_time // 1000).second
            if self.bot_start_second < event_second < self.bot_start_second + self.bot_work_duration and not self.is_done:
                if not self.is_big_volume_data_set():
                    self.big_volume_time = event_time
                    print('big volume time set to: ' + str(self.big_volume_time))
                    self.big_volume_price = self.current_price
                    print('big volume price set to: ' + str(self.big_volume_price))
                # big_volume = random.randint(C.MOCK_BIG_VALUE_MIN, C.MOCK_BIG_VALUE_MAX)
                big_volume = C.MOCK_BIG_VALUE_FIXED
                orders[0][C.VOLUME] = big_volume / float(orders[0][C.PRICE])
                print('volume set to: ' + str(big_volume))
                orders[0][C.PRICE] = self.current_price
                print('price set to: ' + str(orders[0][C.PRICE]))
                if event_second > self.bot_start_second + C.BOT_WORK_DURATION - 2:
                    self.current_price = self.get_step_down_price(self.big_volume_price)
                    orders[0][C.PRICE] = self.current_price
                    print('price set to: ' + str(orders[0][C.PRICE]))
                    self.is_done = True
            else:
                self.mock_neutral_volume(data, order_type)
                # print('small volume set to: ' + str(int(orders[0][C.VOLUME] * self.current_price)))
                orders[0][C.PRICE] = self.current_price
                # print('price set to: ' + str(orders[0][C.PRICE]))

    def mock_case_good_1(self, data, order_type):
        """
        mocks the data in a way that during the period when bot supposed to work
        at first mocks a big volume
        after that changes price in a positive direction and then
        changes the price in opposite way to make the price change negative related to the previous order
        but not less than the price of the first big value appeared
        :param order_type:
        :param data:
        :return:
        """
        event_time = data['E']
        orders = data[order_type]
        self.mock_neutral_volume(data, 'a' if order_type == 'b' else 'b')
        if self.is_data_reset():
            # self.bot_start_second = random.randint(C.MOCK_BOT_START_SECOND_MIN, C.MOCK_BOT_START_SECOND_MAX)
            # self.bot_work_duration = random.randint(C.MOCK_BOT_WORK_DURATION_MIN, C.MOCK_BOT_WORK_DURATION_MIN)
            self.bot_start_second = 1
            self.bot_work_duration = C.BOT_WORK_DURATION
        else:
            event_second = datetime.fromtimestamp(event_time // 1000).second
            if self.bot_start_second < event_second < self.bot_start_second + self.bot_work_duration:
                if not self.is_big_volume_data_set():
                    self.big_volume_time = event_time
                    print('big volume time set to: ' + str(self.big_volume_time))
                    self.big_volume_price = float(orders[0][C.PRICE])
                    print('big volume price set to: ' + str(self.big_volume_price))
                if self.is_done:
                    self.mock_neutral_volume(data, order_type)
                    print('small volume set to: ' + str(int(orders[0][C.VOLUME] * float(orders[0][C.PRICE]))))
                    orders[0][C.PRICE] = self.big_volume_price
                    print('price set to: ' + str(orders[0][C.PRICE]))
                else:
                    # big_volume = random.randint(C.MOCK_BIG_VALUE_MIN, C.MOCK_BIG_VALUE_MAX)
                    big_volume = C.MOCK_BIG_VALUE_FIXED
                    orders[0][C.VOLUME] = big_volume / float(orders[0][C.PRICE])
                    print('volume set to: ' + str(big_volume))
                    self.big_volume_price = self.get_step_up_price(float(self.big_volume_price))
                    orders[0][C.PRICE] = self.big_volume_price
                    print('price set to: ' + str(orders[0][C.PRICE]))
                if event_second > self.bot_start_second + C.BOT_WORK_DURATION - 2 and not self.is_done:
                    self.big_volume_price = self.get_step_down_price(self.big_volume_price)
                    orders[0][C.PRICE] = self.big_volume_price
                    print('price set to: ' + str(orders[0][C.PRICE]))
                    self.is_done = True

    def mock_case_good_2(self, data, order_type='b'):
        """
        mocks the data in a way that during the period when bot supposed to work
        at first mocks a big volume
        after that changes price in a positive direction
        (realized value need to be less than C.BIG_VOLUME_PERCENT_TO_BE_TRADED(%) percent of detected big volume)
        :param order_type:
        :param data:
        :return:
        """
        event_time = data['E']
        orders = data[order_type]
        self.mock_neutral_volume(data, 'a' if order_type == 'b' else 'b')
        if self.is_data_reset():
            # self.bot_start_second = random.randint(C.MOCK_BOT_START_SECOND_MIN, C.MOCK_BOT_START_SECOND_MAX)
            # self.bot_work_duration = random.randint(C.MOCK_BOT_WORK_DURATION_MIN, C.MOCK_BOT_WORK_DURATION_MIN)
            self.bot_start_second = 1
            self.bot_work_duration = C.BOT_WORK_DURATION
        else:
            event_second = datetime.fromtimestamp(event_time // 1000).second
            if self.bot_start_second <= event_second < self.bot_start_second + self.bot_work_duration:
                if not self.is_big_volume_data_set():
                    self.big_volume_time = event_time
                    print('big volume time set to: ' + str(self.big_volume_time))
                    self.big_volume_price = float(orders[0][C.PRICE])
                    print('big volume price set to: ' + str(self.big_volume_price))
                if self.is_done:
                    self.mock_neutral_volume(data, order_type)
                else:
                    # big_volume = random.randint(C.MOCK_BIG_VALUE_MIN, C.MOCK_BIG_VALUE_MAX)
                    big_volume = C.MOCK_BIG_VALUE_FIXED
                    orders[0][C.VOLUME] = big_volume / float(orders[0][C.PRICE])
                    print('volume set to: ' + str(big_volume))
                # orders[0][C.PRICE] = random.choice([orders[0][C.PRICE], self.get_step_up_price(orders[0][C.PRICE])])
                orders[0][C.PRICE] = self.get_step_up_price(orders[0][C.PRICE])
                print('price set to: ' + str(orders[0][C.PRICE]))
                if not self.is_done and event_second > self.bot_start_second + self.bot_work_duration - 1:
                    self.is_done = True

    def mock_case_very_good(self, data, order_type):
        """
        mocks the data in a way that during the period when bot supposed to work
        at first mocks a big volume
        after that changes price in a positive direction and then
        changes the price in opposite way to make the price change negative related to the previous order
        but not less than the price of the first big value appeared
        (realized value need to be more than C.BIG_VOLUME_PERCENT_TO_BE_TRADED(%) percent of detected big volume)
        :param order_type:
        :param data:
        :return:
        """
        self.mock_case_good_1(data, order_type)

    def mock_case_perfect(self, data, order_type):
        """
        mocks the data in a way that during the period when bot supposed to work
        at first mocks a big volume
        after that changes price in a positive direction
        (realized value need to be more than C.BIG_VOLUME_PERCENT_TO_BE_TRADED(%) percent of detected big volume)
        :param order_type:
        :param data:
        :return:
        """
        self.mock_case_good_2(data, order_type)

    def get_step_down_price(self, price):
        # price_str = str(price)
        # decimal_digits_count = len(price_str[price_str.index('.') + 1:])
        # return round(price - 1 / (pow(10, decimal_digits_count)), ndigits=decimal_digits_count)
        return round(price - 0.000001, 6)

    def get_step_up_price(self, price):
        # price_str = str(price)
        # decimal_digits_count = len(price_str[price_str.index('.') + 1:])
        # return round(price + 1 / (pow(10, decimal_digits_count)), ndigits=decimal_digits_count)
        return round(price + 0.000001, 6)

    def is_big_volume_data_set(self):
        return (self.big_volume_time is not None and
                self.big_volume_price is not None)

    def is_data_reset(self):
        return (self.big_volume_time is None and
                self.big_volume_price is None and
                self.bot_work_duration is None and
                self.bot_start_second is None)

    def reset_data(self):
        self.big_volume_time = None
        self.big_volume_price = None
        self.bot_work_duration = None
        self.bot_start_second = None
        self.is_done = False
