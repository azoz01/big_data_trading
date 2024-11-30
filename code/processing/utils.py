from pyspark.sql import SparkSession


def get_or_create_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("big_data_trading")
        .config("spark.redis.host", "redis")
        .config("spark.redis.port", "6379")
        .enableHiveSupport()
        .getOrCreate()
    )


def ensure_schema_exists(schema_name: str) -> None:
    spark = get_or_create_spark_session()
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
