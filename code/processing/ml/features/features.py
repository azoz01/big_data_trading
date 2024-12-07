from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from ...constants import FEATURE_LIST, TECHNICAL_COLUMNS
from .news import (
    add_news_features_offline,
    add_news_features_online,
    calculate_news_sentiments_history,
)
from .tickers import (
    calculate_tickers_features_offline,
    calculate_tickers_features_online,
)
from .transactions import (
    calculate_transactions_features_offline,
    calculate_transactions_features_online,
)


def calculate_features_stream(
    tickers_stream: DataFrame, transactions_stream: DataFrame, news_sentiments_df: DataFrame
) -> DataFrame:
    merged_streams = tickers_stream.unionByName(transactions_stream, allowMissingColumns=True)
    features = calculate_transactions_features_online(merged_streams)
    features = features.filter(col("event") == "ticker")
    features = add_news_features_online(features, news_sentiments_df)
    features = calculate_tickers_features_online(features)
    features = features.select(FEATURE_LIST + TECHNICAL_COLUMNS)
    return features


def calculate_features_df(
    tickers_df: DataFrame, transactions_df: DataFrame, news_history_df: DataFrame
) -> DataFrame:
    merged_streams = tickers_df.unionByName(transactions_df, allowMissingColumns=True)
    features = calculate_transactions_features_offline(merged_streams)
    features = features.filter(col("event") == "ticker")

    news_sentiments_history_df = calculate_news_sentiments_history(news_history_df)
    features = add_news_features_offline(features, news_sentiments_history_df)
    features = features.filter(col("event") == "ticker")

    features = calculate_tickers_features_offline(features)
    features = features.select(FEATURE_LIST + TECHNICAL_COLUMNS)
    return features
