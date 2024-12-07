from pyspark.sql import SparkSession
from pyspark.sql.functions import coalesce, col, lit
from pyspark.sql.types import DoubleType

from .constants import FEATURE_LIST


def get_or_create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("big_data_trading")
        .config("spark.redis.host", "redis")
        .config("spark.redis.port", "6379")
        .config("spark.sql.streaming.statefulOperator.allowMultiple", False)
        .enableHiveSupport()
        .getOrCreate()
    )


def ensure_schema_exists(schema_name: str) -> None:
    spark = get_or_create_spark_session()
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")


def convert_features_to_double_non_null(df):
    for column in FEATURE_LIST:
        df = df.withColumn(column, coalesce(col(column).cast(DoubleType()), lit(0.0)))
    return df
