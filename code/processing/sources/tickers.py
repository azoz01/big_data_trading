from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

TICKER_RAW_SCHEMA = StructType(
    [
        StructField("type", StringType(), True),
        StructField("sequence", LongType(), True),
        StructField("product_id", StringType(), True),
        StructField("price", StringType(), True),
        StructField("open_24h", StringType(), True),
        StructField("volume_24h", StringType(), True),
        StructField("low_24h", StringType(), True),
        StructField("high_24h", StringType(), True),
        StructField("volume_30d", StringType(), True),
        StructField("best_bid", StringType(), True),
        StructField("best_bid_size", StringType(), True),
        StructField("best_ask", StringType(), True),
        StructField("best_ask_size", StringType(), True),
        StructField("side", StringType(), True),
        StructField("time", StringType(), True),
        StructField("trade_id", LongType(), True),
        StructField("last_size", StringType(), True),
    ]
)

TICKERS_HISTORY_PATH = "/crypto/exchange/ticker"


def process_tickers(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("price", col("price").cast(DoubleType()))
        .withColumn("open_24h", col("open_24h").cast(DoubleType()))
        .withColumn("volume_24h", col("volume_24h").cast(DoubleType()))
        .withColumn("low_24h", col("low_24h").cast(DoubleType()))
        .withColumn("high_24h", col("high_24h").cast(DoubleType()))
        .withColumn("volume_30d", col("volume_30d").cast(DoubleType()))
        .withColumn("best_bid", col("best_bid").cast(DoubleType()))
        .withColumn("best_bid_size", col("best_bid_size").cast(DoubleType()))
        .withColumn("time", col("time").cast(TimestampType()))
        .withColumn("best_ask", col("best_ask").cast(DoubleType()))
        .withColumn("best_ask_size", col("best_ask_size").cast(DoubleType()))
        .withColumn("last_size", col("last_size").cast(DoubleType()))
    )


def get_tickers_history(spark: SparkSession) -> DataFrame:
    df = spark.read.schema(TICKER_RAW_SCHEMA).json(TICKERS_HISTORY_PATH)
    return process_tickers(df)


def get_tickers_stream(spark: SparkSession) -> DataFrame:
    stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "broker:19092")
        .option("subscribe", "exchange-ticker")
        .load()
    )
    parsed_stream = (
        stream.selectExpr("CAST(value AS STRING)")
        .select(from_json("value", TICKER_RAW_SCHEMA).alias("data"))
        .select("data.*")
    )
    return process_tickers(parsed_stream)
