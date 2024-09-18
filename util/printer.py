# Define the variables

class Printer:
    symbol = None
    start_price = None
    first_big_volume = None
    big_volume_existence_duration = None  # seconds
    end_price = None
    end_volume = None
    trades_volume = None
    realized_value_percent = None
    first_big_volume_detection_time = None
    last_order_time = None
    first_big_volume_detection_time_millis = None
    last_volume_detection_millis = None
    reason = None
    color = '\033[0m'

    # Define the column widths for each variable (modify as needed)
    widths = {
        'symbol': 15,
        'start_price': 10,
        'first_big_volume': 11,
        'big_volume_existence_duration': 10,
        'end_price': 10,
        'end_volume': 11,
        'trades_volume': 10,
        'realized_value_percent': 10,
        'first_big_volume_detection_time': 23,
        'last_order_time': 23,
        'first_big_volume_detection_time_millis': 8,
        'last_volume_detection_millis': 8,
        'reason': 7
    }

    # Print header
    header = (
        f"{'Symbol'.ljust(widths['symbol'])}"
        f"{'S. Price'.ljust(widths['start_price'])}"
        f"{'Big Volume'.ljust(widths['first_big_volume'])}"
        f"{'Duration'.ljust(widths['big_volume_existence_duration'])}"
        f"{'E. Price'.ljust(widths['end_price'])}"
        f"{'E. Volume'.ljust(widths['end_volume'])}"
        f"{'Tr. Volume'.ljust(widths['trades_volume'])}"
        f"{'(%)'.ljust(widths['realized_value_percent'])}"
        f"{'Start Time'.ljust(widths['first_big_volume_detection_time'])}"
        f"{'St. mls'.ljust(widths['first_big_volume_detection_time_millis'])}"
        f"{'End Time'.ljust(widths['last_order_time'])}"
        f"{'End mls'.ljust(widths['last_volume_detection_millis'])}"
        f"{'Reason'.ljust(widths['reason'])}"
    )

    # Print values

    @classmethod
    def print_row(cls):
        row = (
            f"{cls.symbol.ljust(cls.widths['symbol'])}"
            f"{str(cls.start_price).ljust(cls.widths['start_price'])}"
            f"{str(cls.first_big_volume).ljust(cls.widths['first_big_volume'])}"
            f"{str(cls.big_volume_existence_duration).ljust(cls.widths['big_volume_existence_duration'])}"
            f"{str(cls.end_price).ljust(cls.widths['end_price'])}"
            f"{str(cls.end_volume).ljust(cls.widths['end_volume'])}"
            f"{str(round(cls.trades_volume)).ljust(cls.widths['trades_volume'])}"
            f"{str(cls.realized_value_percent).ljust(cls.widths['realized_value_percent'])}"
            f"{str(cls.first_big_volume_detection_time).ljust(cls.widths['first_big_volume_detection_time'])}"
            f"{str(cls.first_big_volume_detection_time_millis).ljust(cls.widths['first_big_volume_detection_time_millis'])}"
            f"{str(cls.last_order_time).ljust(cls.widths['last_order_time'])}"
            f"{str(cls.last_volume_detection_millis).ljust(cls.widths['last_volume_detection_millis'])}"
            f"{str(cls.reason).ljust(cls.widths['reason'])}"
        )
        text = cls.color + str(row) + '\033[0m' + '\n'
        print(text, end='')

    @classmethod
    def print_header(cls):
        print(cls.header)
        print("-" * sum(cls.widths.values()))  # Separator line
