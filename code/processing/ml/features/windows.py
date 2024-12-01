from pyspark.sql import Window
from pyspark.sql.functions import col, unix_timestamp

from ...utils import get_or_create_spark_session

get_or_create_spark_session()  # Without this call there is error with uninitialized spark context

LAST_15_S_WINDOW = Window.orderBy(unix_timestamp(col("timestamp"))).rangeBetween(-15, -1)

LAST_30_S_WINDOW = Window.orderBy(unix_timestamp(col("timestamp"))).rangeBetween(-30, -1)

LAST_60_S_WINDOW = Window.orderBy(unix_timestamp(col("timestamp"))).rangeBetween(-60, -1)
