from pyspark.sql.functions import (
    col,
    date_trunc,
    desc,
    exp,
    lag,
    last,
    lit,
    log,
    percentile_approx,
    rank,
    sum,
    when,
)
from pyspark.sql.window import Window

from ..utils import get_or_create_spark_session
from .process_registry import process_registry


@process_registry("calculate_roi")
class CalculateRoiProcess:

    def execute(self):
        spark = get_or_create_spark_session()
        df = (
            spark.read.format("org.elasticsearch.spark.sql")
            .option("es.mapping.id", "timestamp")
            .option("es.resource", "predictions")
            .load()
        )

        df = df.withColumn(
            "date_rank", rank().over(Window.orderBy(desc(date_trunc("day", col("timestamp")))))
        ).filter(col("date_rank") == 1)
        bounds = df.select(
            percentile_approx(col("probability"), 0.9).alias("upper"),
            percentile_approx(col("probability"), 0.1).alias("lower"),
        ).collect()
        lower_bound = bounds[0]["lower"]
        upper_bound = bounds[0]["upper"]
        decision = (
            when(col("probability") >= upper_bound, "BUY")
            .when(col("probability") <= lower_bound, "SELL")
            .otherwise("NOTHING")
        )
        time_window = Window.orderBy("timestamp")
        last_action = last(
            when(col("decision").isin("BUY", "SELL"), col("decision")), ignorenulls=True
        ).over(time_window)

        df = df.withColumn(
            "potential_price_change", lag(col("price"), -1).over(time_window) / col("price")
        )
        df = df.withColumn("decision", decision)
        df = df.withColumn("last_action", last_action)
        df = df.withColumn("state", when(last_action == "BUY", "CRYPTO").otherwise("MONEY"))
        df = df.withColumn(
            "portfolio_value_change",
            when(col("state") == "MONEY", lit(1)).otherwise(col("potential_price_change")),
        )
        df = df.withColumn(
            "roi", exp(sum(log(col("portfolio_value_change"))).over(time_window)) - lit(1.0)
        )
        df.select("timestamp", "roi", "decision", "potential_price_change").write.mode(
            "overwrite"
        ).format("org.elasticsearch.spark.sql").option("es.mapping.id", "timestamp").option(
            "es.resource", "roi"
        ).save()


# PYSPARK_PYTHON=./venv/bin/python spark-submit main.py --process calculate_roi
