import threading


class Consts:
    RUN_WITH_DB = False
    CLEAN_OLD_ORDERS = True
    CLEAN_OLD_BOT_DATA = True

    SIGNIFICANT_CHANGE_FACTOR = 7
    VOLUMES_CAPACITY = 1000
    MEDIAN_GROUPING_INTERVAL = 20
    TOKENS_COUNT_TO_FOLLOW = 300
    MINIMUM_TARGET_VOLUME = 4000
    BOT_WORK_DURATION = 10  # in seconds
    BOT_START_MAX_SECOND = 10
    BOT_WORKING_SECONDS_LIMIT = BOT_START_MAX_SECOND + BOT_WORK_DURATION
    BIG_VOLUME_PERCENT_TO_BE_TRADED = 70
    SMALL_VOLUME_ACCEPTABLE_DURATION = 500

    SHORT_FACTOR = -1
    LONG_FACTOR = 1

    YELLOW = '\33[33m'
    RED = '\33[91m'
    RED_FILL = '\33[101m'
    DARK_RED = '\33[31m'
    DARK_RED_FILL = '\33[41m'
    GREEN = '\033[92m'
    GREEN_FILL = '\033[42m'
    DARK_GREEN = '\33[32m'
    DARK_GREEN_FILL = '\33[42m'
    RESET_COLOR = '\033[0m'
    LONG_COLORS = ('', GREEN, DARK_GREEN, GREEN_FILL, DARK_GREEN_FILL)
    SHORT_COLORS = ('', RED, DARK_RED, RED_FILL, DARK_RED_FILL)

    PRICE = 0
    VOLUME = 1
    TIME = 2

    BAD = 0
    GOOD_1 = 1
    GOOD_2 = 2
    VERY_GOOD = 3
    PERFECT = 4

    USE_MOCK_DATA = False
    MOCK_BIG_VALUE_FIXED = 8000  # in USD
    MOCK_USUAL_VALUE_MIN = 400  # in USD
    MOCK_USUAL_VALUE_MAX = 500  # in USD
    MOCK_BIG_VALUE_MIN = MOCK_USUAL_VALUE_MAX * SIGNIFICANT_CHANGE_FACTOR  # in USD
    MOCK_BIG_VALUE_MAX = MOCK_BIG_VALUE_MIN * 2  # in USD
    MOCK_BOT_WORK_DURATION_MIN = 2  # in milliseconds
    MOCK_BOT_WORK_DURATION_MAX = 6  # in milliseconds
    MOCK_BOT_START_SECOND_MIN = 0
    MOCK_BOT_START_SECOND_MAX = 10

    MOCK_CASE_NEUTRAL = -1
    MOCK_CASE_BAD = 0
    MOCK_CASE_GOOD_1 = 1
    MOCK_CASE_GOOD_2 = 2
    MOCK_CASE_VERY_GOOD = 3
    MOCK_CASE_PERFECT = 4
    MOCK_CASE = MOCK_CASE_GOOD_1

    AGG_TRADES_CALLS_COUNT_PER_MINUTE = 0
    AGG_TRADES_CALLS_COUNT_TOTAL = 0
    lock = threading.Lock()
    symbols = []

    @classmethod
    def increment(cls, symbol):
        with cls.lock:
            # Critical section - only one thread can execute this at a time
            cls.AGG_TRADES_CALLS_COUNT_PER_MINUTE += 1
            cls.AGG_TRADES_CALLS_COUNT_TOTAL += 1
            if symbol not in cls.symbols:
                cls.symbols.append(symbol)

    @classmethod
    def reset(cls):
        with cls.lock:
            # Critical section - only one thread can execute this at a time
            cls.AGG_TRADES_CALLS_COUNT_PER_MINUTE = 0
