from pyspark.sql import DataFrame
from pyspark.sql.functions import avg, col, count, when

from .utils import add_rolling_window_to_stream, with_column_if_ticker
from .windows import (
    LAST_DAY_STREAMING_WINDOW,
    LAST_DAY_WINDOW,
    LAST_HALF_DAY_STREAMING_WINDOW,
    LAST_HALF_DAY_WINDOW,
    LAST_HOUR_STREAMING_WINDOW,
    LAST_HOUR_WINDOW,
)


def calculate_tickers_features_offline(df: DataFrame) -> DataFrame:
    ticker_price = when(col("event") == "ticker", col("price"))
    df = with_column_if_ticker(df, "avg_price_last_hour", avg(ticker_price).over(LAST_HOUR_WINDOW))
    df = with_column_if_ticker(
        df, "avg_price_last_half_day", avg(ticker_price).over(LAST_HALF_DAY_WINDOW)
    )
    df = with_column_if_ticker(df, "avg_price_last_day", avg(ticker_price).over(LAST_DAY_WINDOW))
    return df


def calculate_tickers_features_online(df: DataFrame) -> DataFrame:
    ticker_price = when(col("event") == "ticker", col("price"))
    output = add_rolling_window_to_stream(df, "avg_price_last_15s", avg(ticker_price), "15 seconds")
    output = add_rolling_window_to_stream(
        output, "avg_price_last_30s", avg(ticker_price), "30 seconds"
    )
    output = add_rolling_window_to_stream(
        output, "avg_price_last_60s", avg(ticker_price), "60 seconds"
    )
    return output
