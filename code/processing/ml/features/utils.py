from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import (
    col,
    current_timestamp,
    desc,
    lit,
    when,
    window,
)

from ...utils import get_or_create_spark_session


def with_column_if_ticker(df: DataFrame, name, c: Column) -> DataFrame:
    return df.withColumn(name, when(col("event") == "ticker", c))


def add_rolling_window_to_stream(
    df: DataFrame, colname: str, aggregate_col: Column, duration: str
) -> DataFrame:
    aggregates_stream = (
        df.withWatermark("timestamp", duration)
        .groupBy(window("timestamp", duration, "1 second"))
        .agg(aggregate_col.alias(colname))
        .select(
            col("window.end").alias("timestamp"),
            colname,
            current_timestamp(),
        )
        .filter(col("timestamp") <= current_timestamp())
        .orderBy(desc("timestamp"))
        .limit(1)
        .select(colname)
    )
    aggregates_stream.writeStream.format("memory").queryName(colname).outputMode("complete").start()
    spark = get_or_create_spark_session()
    aggregates = spark.sql(f"SELECT * FROM {colname}")
    return df.join(aggregates, lit(True), "left")
