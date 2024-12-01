from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when

from .utils import add_rolling_window_to_stream, with_column_if_ticker
from .windows import LAST_DAY_WINDOW, LAST_HALF_DAY_WINDOW, LAST_HOUR_WINDOW


def calculate_transactions_features_offline(df: DataFrame) -> DataFrame:
    transaction_count_source_col = when(col("event") == "transaction", 1)
    df = with_column_if_ticker(
        df,
        "transaction_count_last_hour",
        count(transaction_count_source_col).over(LAST_HOUR_WINDOW),
    )
    df = with_column_if_ticker(
        df,
        "transaction_count_last_half_day",
        count(transaction_count_source_col).over(LAST_HALF_DAY_WINDOW),
    )
    df = with_column_if_ticker(
        df,
        "transaction_count_last_day",
        count(transaction_count_source_col).over(LAST_DAY_WINDOW),
    )
    return df


def calculate_transactions_features_online(df: DataFrame) -> DataFrame:
    transaction_count_source_col = when(col("event") == "transaction", 1)
    output = add_rolling_window_to_stream(
        df, "transaction_count_last_15s", count(transaction_count_source_col), "15 seconds"
    )
    output = add_rolling_window_to_stream(
        output, "transaction_count_last_30s", count(transaction_count_source_col), "30 seconds"
    )
    output = add_rolling_window_to_stream(
        output, "transaction_count_last_60s", count(transaction_count_source_col), "60 seconds"
    )
    return output
