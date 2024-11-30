from pyspark.sql import Column, DataFrame, GroupedData, Window
from pyspark.sql.functions import (
    avg,
    coalesce,
    col,
    count,
    first,
    last,
    lit,
    lower,
    regexp_replace,
    unix_timestamp,
    when,
)

from ..constants import CRYPTO_NEWS_SOURCES, FEATURE_LIST, NEWS_COLUMNS
from ..ml.sentiment import calculate_sentiment_aggregates, sentiment_udf
from .windows import LAST_DAY_WINDOW, LAST_HALF_DAY_WINDOW, LAST_HOUR_WINDOW


def calculate_features_stream(
    tickers_stream: DataFrame, transactions_stream: DataFrame, news_sentiments_df: DataFrame
) -> DataFrame:
    merged_streams = tickers_stream.unionByName(transactions_stream, allowMissingColumns=True)
    features = calculate_transactions_features(merged_streams)
    features = features.filter(col("event") == "ticker")
    features = add_news_features_online(features, news_sentiments_df)
    features = features.select(FEATURE_LIST)
    return features


def calculate_features_df(
    tickers_df: DataFrame, transactions_df: DataFrame, news_history_df: DataFrame
) -> DataFrame:
    merged_streams = tickers_df.unionByName(transactions_df, allowMissingColumns=True)
    features = calculate_transactions_features(merged_streams)
    features = features.filter(col("event") == "ticker")

    news_sentiments_history_df = calculate_news_sentiments_history(news_history_df)
    features = add_news_features_offline(features, news_sentiments_history_df)
    features = features.filter(col("event") == "ticker")

    features = calculate_tickers_features(features)
    features = features.select(FEATURE_LIST + ["timestamp", "event"])
    return features


def calculate_tickers_features(df: DataFrame) -> DataFrame:
    ticker_price = when(col("event") == "ticker", col("price"))
    df = withColumnIfTicker(df, "avg_price_last_hour", avg(ticker_price).over(LAST_HOUR_WINDOW))
    df = withColumnIfTicker(
        df, "avg_price_last_half_day", avg(ticker_price).over(LAST_HALF_DAY_WINDOW)
    )
    df = withColumnIfTicker(df, "avg_price_last_day", avg(ticker_price).over(LAST_DAY_WINDOW))
    return df


def calculate_transactions_features(df: DataFrame) -> DataFrame:
    transaction_count_source_col = when(col("event") == "transaction", 1)
    df = withColumnIfTicker(
        df,
        "transaction_count_last_hour",
        count(transaction_count_source_col).over(LAST_HOUR_WINDOW),
    )
    df = withColumnIfTicker(
        df,
        "transaction_count_last_half_day",
        count(transaction_count_source_col).over(LAST_HALF_DAY_WINDOW),
    )
    df = withColumnIfTicker(
        df,
        "transaction_count_last_day",
        count(transaction_count_source_col).over(LAST_DAY_WINDOW),
    )
    return df


def withColumnIfTicker(df: DataFrame, name, c: Column) -> DataFrame:
    return df.withColumn(name, when(col("event") == "ticker", c))


def calculate_news_sentiments_history(news_history_df: DataFrame) -> DataFrame:
    news = news_history_df.select(
        col("timestamp"),
        col("source"),
        col("headline"),
        sentiment_udf(col("headline")).alias("sentiment"),
    )
    return calculate_sentiment_aggregates(news.groupBy("timestamp", "source"))


def add_news_features_offline(merged_events: DataFrame, news_sentiments: DataFrame) -> DataFrame:
    news_sentiments = news_sentiments.withColumn(
        "source_standardized", lower(regexp_replace(col("source"), r"\s+", "_"))
    )
    news_features = calculate_news_features(news_sentiments.groupBy("timestamp")).withColumn(
        "event", lit("news_sentiment")
    )
    return merged_events.unionByName(news_features, allowMissingColumns=True).select(
        list(map(col, merged_events.columns))
        + [
            when(
                col("event") == "ticker",
                last(col(colname), ignorenulls=True).over(
                    Window.orderBy(unix_timestamp(col("timestamp"))).rangeBetween(
                        Window.unboundedPreceding, -1
                    )
                ),
            ).alias(colname)
            for colname in set(news_features.columns).difference(merged_events.columns)
        ]
    )


def add_news_features_online(events_stream: DataFrame, news_sentiments: DataFrame) -> DataFrame:
    news_sentiments = news_sentiments.withColumn(
        "source_standardized", lower(regexp_replace(col("source"), r"\s+", "_"))
    )
    news_features = calculate_news_features(news_sentiments.groupBy())
    return events_stream.join(news_features, lit(True))


def calculate_news_features(grouped_df: GroupedData) -> DataFrame:
    news_sentiment_features = grouped_df.pivot("source_standardized", CRYPTO_NEWS_SOURCES).agg(
        first("avg_sentiment").alias("avg_sentiment"),
        first("std_sentiment").alias("std_sentiment"),
        first("max_sentiment").alias("max_sentiment"),
        first("min_sentiment").alias("min_sentiment"),
    )
    for colname in news_sentiment_features.columns:
        if colname in NEWS_COLUMNS:
            continue
        news_sentiment_features = news_sentiment_features.withColumn(
            colname, coalesce(col(colname), lit(0.0)).alias(colname)
        )
    return news_sentiment_features
