from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql.functions import col, desc, rank
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
    TimestampType,
)

NEWS_SCHEMA = StructType(
    [
        StructField("summary", StringType(), True),
        StructField("headline", StringType(), True),
    ]
)

NEWS_HISTORY_PATH = "/crypto/news/data/"


def process_news(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "timestamp",
        col("version").cast(TimestampType()),
    )


def get_news_history(spark: SparkSession) -> DataFrame:
    df = spark.read.schema(NEWS_SCHEMA).json(NEWS_HISTORY_PATH)
    return process_news(df)


def get_newest_news_snapshot(spark: SparkSession) -> DataFrame:
    df = get_news_history(spark)
    return (
        df.withColumn("rnk", rank().over(Window.orderBy(desc("version"))))
        .filter(col("rnk") == 1)
        .drop("rnk")
    )


def get_news_sentiment_aggregates_from_redis(spark: SparkSession) -> DataFrame:
    return (
        spark.read.format("org.apache.spark.sql.redis")
        .option("table", "sentiments_aggregates")
        .load()
    )
