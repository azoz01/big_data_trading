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
    LongType,
    StringType,
    StructField,
    StructType,
)

INITIAL_TRANSACTIONS_SCHEMA = StructType(
    [
        StructField("op", StringType(), True),
        StructField(
            "x",
            StructType(
                [
                    StructField("lock_time", LongType(), True),
                    StructField("ver", LongType(), True),
                    StructField("size", LongType(), True),
                    StructField(
                        "inputs",
                        ArrayType(
                            StructType(
                                [
                                    StructField("sequence", LongType(), True),
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
                                                    LongType(),
                                                    True,
                                                ),
                                                StructField("type", LongType(), True),
                                                StructField("addr", StringType(), True),
                                                StructField("value", LongType(), True),
                                                StructField("n", LongType(), True),
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
                    StructField("tx_index", LongType(), True),
                    StructField("vin_sz", LongType(), True),
                    StructField("hash", StringType(), True),
                    StructField("vout_sz", LongType(), True),
                    StructField("relayed_by", StringType(), True),
                    StructField(
                        "out",
                        ArrayType(
                            StructType(
                                [
                                    StructField("spent", BooleanType(), True),
                                    StructField("tx_index", LongType(), True),
                                    StructField("type", LongType(), True),
                                    StructField("addr", StringType(), True),
                                    StructField("value", LongType(), True),
                                    StructField("n", LongType(), True),
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
        col("x.lock_time").cast(LongType()).alias("lock_time"),
        col("x.ver").cast(LongType()).alias("ver"),
        col("x.size").cast(LongType()).alias("size"),
        col("x.tx_index").cast(LongType()).alias("tx_index"),
        col("x.vin_sz").cast(LongType()).alias("vin_sz"),
        col("x.vout_sz").cast(LongType()).alias("vout_sz"),
        col("x.inputs").alias("inputs"),
        col("x.out").alias("out"),
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
        .option("subscribe", "blockchain")
        .load()
    )
    parsed_stream = (
        stream.selectExpr("CAST(value AS STRING)")
        .select(from_json("value", INITIAL_TRANSACTIONS_SCHEMA).alias("data"))
        .select("data.*")
    )
    return process_transactions(parsed_stream).withWatermark("timestamp", "1 week")
