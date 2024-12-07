from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lead
from pyspark.sql.types import IntegerType
from pyspark.sql.window import Window


def calculate_target_column(df: DataFrame) -> DataFrame:
    next_price = lead("price").over(Window.orderBy("timestamp"))
    return df.withColumn("target", (col("price") < next_price).cast(IntegerType())).filter(
        col("target").isNotNull()
    )
