from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pyspark.sql import DataFrame, GroupedData, Window
from pyspark.sql.functions import (
    avg,
    coalesce,
    col,
    first,
    last,
    lit,
    lower,
    max,
    min,
    regexp_replace,
    stddev,
    udf,
    unix_timestamp,
    when,
)
from pyspark.sql.types import StringType

from ...constants import CRYPTO_NEWS_SOURCES, NEWS_COLUMNS


def sentiment_analyzer(text: str) -> float:
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return scores["compound"]


sentiment_udf = udf(sentiment_analyzer, StringType())


def calculate_sentiment_aggregates(grouped_data: GroupedData) -> DataFrame:
    return grouped_data.agg(
        avg(col("sentiment")).alias("avg_sentiment"),
        stddev(col("sentiment")).alias("std_sentiment"),
        max(col("sentiment")).alias("max_sentiment"),
        min(col("sentiment")).alias("min_sentiment"),
    )


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
