from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    from_unixtime,
    lit,
    to_timestamp,
)
from pyspark.sql.types import (
    ArrayType,
    BooleanType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# Commented out some columns due to elastic errors
INITIAL_TRANSACTIONS_SCHEMA = StructType(
    [
        StructField("op", StringType(), True),
        StructField(
            "x",
            StructType(
                [
                    StructField("lock_time", IntegerType(), True),
                    StructField("ver", IntegerType(), True),
                    StructField("size", IntegerType(), True),
                    StructField(
                        "inputs",
                        ArrayType(
                            StructType(
                                [
                                    StructField("sequence", IntegerType(), True),
                                    StructField(
                                        "prev_out",
                                        StructType(
                                            [
                                                StructField(
                                                    "spent",
                                                    BooleanType(),
                                                    True,
                                                ),
                                                StructField(
                                                    "tx_index",
                                                    IntegerType(),
                                                    True,
                                                ),
                                                StructField("type", IntegerType(), True),
                                                StructField("addr", StringType(), True),
                                                StructField("value", IntegerType(), True),
                                                StructField("n", IntegerType(), True),
                                                StructField(
                                                    "script",
                                                    StringType(),
                                                    True,
                                                ),
                                            ]
                                        ),
                                        True,
                                    ),
                                    StructField("script", StringType(), True),
                                ]
                            )
                        ),
                        True,
                    ),
                    StructField("time", IntegerType(), True),
                    StructField("tx_index", IntegerType(), True),
                    StructField("vin_sz", IntegerType(), True),
                    StructField("hash", StringType(), True),
                    StructField("vout_sz", IntegerType(), True),
                    StructField("relayed_by", StringType(), True),
                    StructField(
                        "out",
                        ArrayType(
                            StructType(
                                [
                                    StructField("spent", BooleanType(), True),
                                    StructField("tx_index", IntegerType(), True),
                                    StructField("type", IntegerType(), True),
                                    StructField("addr", StringType(), True),
                                    StructField("value", IntegerType(), True),
                                    StructField("n", IntegerType(), True),
                                    StructField("script", StringType(), True),
                                ]
                            )
                        ),
                        True,
                    ),
                ]
            ),
            True,
        ),
    ]
)

TRANSACTIONS_HISTORY_PATH = "/crypto/blockchain/transactions"


def process_transactions(df: DataFrame) -> DataFrame:
    return df.select(
        col("op"),
        from_unixtime(col("x.time")).alias("time"),
        col("x.hash").alias("hash"),
        col("x.relayed_by").alias("relayed_by"),
        lit("transaction").alias("event"),
        to_timestamp(from_unixtime(col("x.time"))).alias("timestamp"),
    )


def get_transactions_history(spark: SparkSession) -> DataFrame:
    df = spark.read.schema(INITIAL_TRANSACTIONS_SCHEMA).parquet(TRANSACTIONS_HISTORY_PATH)
    return process_transactions(df)


def get_transactions_stream(spark: SparkSession) -> DataFrame:
    stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "broker:19092")
        .option("failOnDataLoss", "false")
        .option("subscribe", "blockchain")
        .load()
    )
    parsed_stream = (
        stream.selectExpr("CAST(value AS STRING)")
        .select(from_json("value", INITIAL_TRANSACTIONS_SCHEMA).alias("data"))
        .select("data.*")
    )
    return process_transactions(parsed_stream)


def process_transactions_to_elastic(df: DataFrame) -> DataFrame:
    return df.drop(
        "lock_time",
        "ver",
        "size",
        "tx_index",
        "vin_sz",
        "vout_sz",
        "inputs",
        "out",
    )
