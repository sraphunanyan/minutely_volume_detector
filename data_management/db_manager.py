import mysql.connector

db_config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'binance_data'
}


def create_orders_table(db_connection, symbol, drop=True):
    cursor = db_connection.cursor()
    drop_table_query = f"DROP TABLE {symbol + '_orders'}"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {symbol + '_orders'} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50),
        ask_price FLOAT,
        ask_volume INT,
        bid_price FLOAT,
        bid_volume INT,
        order_time TIMESTAMP,
        order_time_millis BIGINT
    );
    """
    if drop:
        cursor.execute(drop_table_query)
    cursor.execute(create_table_query)
    db_connection.commit()
    cursor.close()


def insert_order_data(db_connection,
                      symbol,
                      ask_price,
                      ask_volume,
                      bid_price,
                      bid_volume,
                      order_time,
                      order_time_millis):
    cursor = db_connection.cursor()
    insert_query = f"""
    INSERT INTO {symbol + '_orders'} (
        symbol,
        ask_price,
        ask_volume,
        bid_price,
        bid_volume,
        order_time,
        order_time_millis
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (symbol, ask_price, ask_volume, bid_price, bid_volume, order_time, order_time_millis))
    db_connection.commit()
    cursor.close()


def create_bot_detection_data_table(db_connection, drop=False):
    cursor = db_connection.cursor()
    drop_table_query = f"DROP TABLE bot_detection_data"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS bot_detection_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50),
        order_type VARCHAR(50),
        first_big_volume INT,
        first_big_volume_detection_time DATETIME,
        first_big_volume_detection_time_millis BIGINT,
        data_record_time DATETIME,
        big_volume_existence_duration INT,
        trades_volume INT,
        realized_value_percent INT
    );
    """
    if drop:
        cursor.execute(drop_table_query)
    cursor.execute(create_table_query)
    db_connection.commit()
    cursor.close()


def insert_bot_data(db_connection,
                    symbol,
                    order_type,
                    first_big_volume,
                    first_big_volume_detection_time,
                    first_big_volume_detection_time_millis,
                    data_record_time,
                    big_volume_existence_duration,
                    trades_volume,
                    realized_value_percent):
    cursor = db_connection.cursor()
    insert_query = f"""
    INSERT INTO bot_detection_data (symbol,
                                    order_type,
                                    first_big_volume,
                                    first_big_volume_detection_time,
                                    first_big_volume_detection_time_millis,
                                    data_record_time,
                                    big_volume_existence_duration,
                                    trades_volume,
                                    realized_value_percent) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (symbol,
                                  order_type,
                                  first_big_volume,
                                  first_big_volume_detection_time,
                                  first_big_volume_detection_time_millis,
                                  data_record_time,
                                  big_volume_existence_duration,
                                  trades_volume,
                                  realized_value_percent))
    db_connection.commit()
    cursor.close()


def fetch_and_print_data(db_connection, table_name: str):
    cursor = db_connection.cursor()
    select_query = f"SELECT * FROM {table_name}"
    cursor.execute(select_query)

    for row in cursor.fetchall():
        print(row)

    cursor.close()


def get_db_connection():
    return mysql.connector.connect(**db_config)
